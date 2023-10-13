# -*- coding: utf-8 -*-
import server.extraServerApi as serverApi
import Config
from modCommon.shop.GoodsCMD import GoodsCMDClass
from modCommon.cloud.Cloud import CloudClass
import logging
import time

CODE_VERSION = Config.CODE_VERSION
DEBUG = Config.DEBUG
FACTORY = Config.SERVER_FACTORY
CMD = Config.COMMAND
LEVEL_ID = Config.LEVELID
GAME_RULE = Config.DEFAULT_GAME_RULE
CONNECT_BY_GET = Config.CONNECT_BY_GET
CONNECT_BY_SET = Config.CONNECT_BY_SET
CREATE_GAME_BY_LEVELID = Config.CREATE_GAME_BY_LEVELID
GOODS_CMD = GoodsCMDClass()   #发货指令
CLOUD = CloudClass()   #云数据操作

#云配置数据
mapName = "未获取到地图名"  #地图名
mapNotice = "未获取到公告"  #公告
mapUrgentSwitch = False  #紧急公告控制
mapUrgentNotice = "如果你看到这个一直在弹出来，请关闭房间保存地图重新启动"  #紧急公告

eventList = []  #监听中的事件
playerList = [] #玩家列表
whiteList = []  #管理员列表
uidDict = {}    #玩家的UID
playerGoodsDict = {}    #玩家拥有的商品（商品 = 实现指令）

cdDict = {} #冷却变量表（每秒-1）

if DEBUG:
    whiteList.append("Spawner") #添加你的测试启动器开发者账号名字

#一个装饰器，使某个服务端类的函数变成回调函数。
#funcOrStr：既可以是函数，也可以是事件名称。
#EN：EngineNamespace，ESN：EngineSystemName，不传则默认监听游戏本体事件。
#本模板封装了更方便的通信接口，所以EN，ESN这两个参数可能无需使用。
def Listen(funcOrStr=None, EN=serverApi.GetEngineNamespace(), ESN=serverApi.GetEngineSystemName()):
    def binder(func):
        eventList.append((EN, ESN, funcOrStr if isinstance(funcOrStr, str)else func.__name__, func))
        return func
    return binder(funcOrStr)if callable(funcOrStr)else binder

class ServerSystem(serverApi.GetServerSystemCls()):
    #无需在此处监听引擎事件，请使用@Listen；无需监听客户端自定义事件，请在客户端使用CallServer。
    #可在此处进行初始化操作。
    def __init__(self, namespace, systemName):
        super(ServerSystem, self).__init__(namespace, systemName)
        logging.info( "代码版本: " + CODE_VERSION)  
        for EN, ESN, eventName, callback in eventList:
            self.ListenForEvent(EN, ESN, eventName, self, callback)
        self.InitWorld()
        self.InitOptions()
        
    #无需在此处取消监听引擎事件
    def Destroy(self):
        for EN, ESN, eventName, callback in eventList:
            self.UnListenForEvent(EN, ESN, eventName, self, callback)

    #无需改动。此处监听来自客户端的事件进行函数分发
    @Listen('ClientEvent', Config.MOD_NAME, 'ClientSystem')
    def OnGetClientEvent(self, args):
        args['funcArgs']['__id__'] = args['__id__']
        getattr(self, args['funcName'])(args['funcArgs'])

    #无需改动。调用客户端函数并发送数据（str：客户端对应玩家id，str：客户端函数名称，dict：要发送的数据字典）
    def CallClient(self, playerId, funcName, funcArgs):
        self.NotifyToClient(playerId, 'ServerEvent', {'funcName': funcName, 'funcArgs': funcArgs})

    def CallAllClient(self, funcName, funcArgs):
        self.BroadcastToAllClient('ServerEvent', {'funcName': funcName, 'funcArgs': funcArgs})

#------------------------------------------初始化和管理------------------------------------------#
    
    #初始化世界
    def InitWorld(self):
        #设置实体上限
        serverApi.SetEntityLimit(200)
        #设置生存模式为默认游戏模式
        CREATE_GAME_BY_LEVELID.SetDefaultGameType(0)
        #设置游戏难度
        CREATE_GAME_BY_LEVELID.SetGameDifficulty(3)
        #关闭我的伙伴
        compCreatePet = FACTORY.CreatePet(LEVEL_ID)
        compCreatePet.Disable()
        #设置默认游戏规则
        CREATE_GAME_BY_LEVELID.SetGameRulesInfoServer(GAME_RULE)
        
        #禁止物品
        if not DEBUG:
            compCreateItemBanned = FACTORY.CreateItemBanned(LEVEL_ID)
            compCreateItemBanned.AddBannedItem("minecraft:bedrock")
            compCreateItemBanned.AddBannedItem("minecraft:deny")
            compCreateItemBanned.AddBannedItem("minecraft:allow")

    #初始化地图后端配置
    def InitOptions(self):
        CLOUD.GetOperateInfoFromCloud()
        self.ActionTimer()

    #初始化个人数据
    def LoadPlayerData(self,playerId):
        if playerId not in playerList:
            playerList.append(playerId)

        if not DEBUG:
            if playerId not in uidDict:
                uidDict[playerId] = self.GetUid(playerId)

    #移除个人数据
    def RemovePlayerData(self,playerId):
        if playerId in playerList:
            playerList.remove(playerId)

        if not DEBUG:
            if playerId in uidDict:
                del uidDict[playerId]

#------------------------------------------计时相关操作------------------------------------------#

    #轮询查询并发货
    def DeliverGoodsCycle(self):
        for playerId in playerList:
            self.DeliverGoods(playerId)

    #轮询减少所有cd
    def ReduceCDCycle(self):
        for k,v in cdDict.items():
            if v > 0:
                cdDict[k] -= 1

    #启动所有计时器
    def ActionTimer(self):
        CREATE_GAME_BY_LEVELID.AddRepeatedTimer(30.0,self.DeliverGoodsCycle)
        CREATE_GAME_BY_LEVELID.AddRepeatedTimer(30.0,self.GetUrgentNotice)
        CREATE_GAME_BY_LEVELID.AddRepeatedTimer(25.0,self.GetOperateInfoFromCloud)
        CREATE_GAME_BY_LEVELID.AddRepeatedTimer(1.0,self.ReduceCDCycle)
        CREATE_GAME_BY_LEVELID.AddRepeatedTimer(1.0,self.Safety)

#------------------------------------------云数据相关操作------------------------------------------#

    #获取玩家uid
    def GetUid(self,playerId):
        compGetPlayerUid = CONNECT_BY_GET.GetPlayerUid(playerId)
        uid = compGetPlayerUid.GetPlayerUid(playerId)
        return uid
    
    #获取紧急公告（只有执行过GetOperateInfoFromCloud时，该函数才有效）
    def GetUrgentNotice(self):
        if mapUrgentSwitch == True:
            CREATE_GAME_BY_LEVELID.SetNotifyMsg("urgentNotice",serverApi.GenerateColor('RED'))

    #获取云配置数据信息（只有执行过GetOperateInfoFromCloud时，该函数才有效）
    def GetOperateInfoFromFile(self):
        return {"name": mapName,"notice": mapNotice,"urgentSwitch": mapUrgentSwitch,"urgentNotice": mapUrgentNotice}

    #自定义回调调试信息
    def GetDebugCallback(self,message,code,key,value):
        data = {'message': message,'code': code,'details': '','entity': {'data': [{'version': 1,'key': key,'value': value}]}}
        return data
    
    #上传数据到云
    def UploadDataToCloud(self,uid,key,value):
        def cb(data):
            if data:
                logging.info("UploadDataToCloud succeeded")
            else:
                logging.info("UploadDataToCloud failed")
        def getter():
                return [{"key": key,"value": value}]
        CONNECT_BY_GET.LobbySetStorageAndUserItem(cb, uid, None, getter)

    #获取运营配置信息
    def GetOperateInfoFromCloud(self):
        key = ["op_CONFIG"]
        def cb(data):
            if data:
                dataDict = data["entity"]["data"][0]["value"]
                mapName = dataDict["name"]
                mapNotice = dataDict["notice"]
                mapUrgentSwitch = dataDict["urgentSwitch"]
                mapUrgentNotice = dataDict["urgentNotice"]
                logging.info("GetOprInfo succeeded")
            else:
                logging.info("GetOprInfo failed")
        if DEBUG:
            data = {'name': '随机方块空岛生存[无限宝箱版]','notice': '欢迎游玩本地图，如有任何疑惑请在我们的社交媒体反馈','urgentSwitch': False,'urgentNotice': '§l§c紧急公告! 服务器将在5分钟后更新, 请立即保存地图退出游戏进行等待!'}
            mock = self.GetDebugCallback("op_CONFIGMessage",0,key,data)
            cb(mock)
        else:
            CONNECT_BY_GET.LobbyGetStorage(cb, 0, key)
            
    #对未处理的订单进行发货
    def DeliverGoods(self,playerId):
        def cb(data):
            if data:
                ordersDict = data["entity"]["orders"]
                for order in ordersDict:
                    #根据订单请求实现发货
                    result = GOODS_CMD.executeCMD(order["cmd"],playerId)
                    compCreateMsg = FACTORY.CreateMsg(playerId)
                    if result == False:
                        compCreateMsg.NotifyOneMessage(playerId, "物品发货失败，请联系管理员！ ", "§c")
                        return
                    #存储用户的实现指令并上传云端
                    if playerId not in playerGoodsDict:
                        playerGoodsDict[playerId] = [order["cmd"]]
                    else:
                        playerGoodsDict[playerId].append(order["cmd"])
                    CLOUD.SetData(uidDict[playerId],Config.CLOUD_KEY_SHOP_GOODS,playerGoodsDict[playerId])
                    #标记发货
                    self.TagOrder(uidDict[playerId],order["order_id"])
                    compCreateMsg.NotifyOneMessage(playerId, "感谢你购买本商品，如有任何疑惑请在评论区反馈! ", "§e")
                    logging.info("DeliverGoods succeeded")
            else:
                logging.info("DeliverGoods failed")
        CONNECT_BY_GET.QueryLobbyUserItem(cb, uidDict[playerId])

    #标记订单
    def TagOrder(self,uid,orderId):
        def cb(data):
            if data:
                logging.info("TagOrder succeeded")
            else:
                logging.info("TagOrder failed")
        def getter():
                return [{"key": "orders","value": orderId}]
        CONNECT_BY_SET.LobbySetStorageAndUserItem(cb, uid, orderId, getter)

#------------------------------------------玩家进退区域------------------------------------------#

    #玩家加入联机大厅时
    @Listen('lobbyGoodBuySucServerEvent')
    def OnlobbyGoodBuySucServerEvent(self,args):
        #如果为玩家购买商品(eid: 玩家实体id，buyItem: 商品ID)
        if args["eid"] != None:
            playerId = args["eid"]
            if args["buyItem"] != False:
                self.DeliverGoods(playerId)
            #如果为进入大厅，初始化个人数据
            elif args["buyItem"] == False:
                self.LoadPlayerData(playerId)

    #玩家加入游戏时
    @Listen('AddServerPlayerEvent')
    def OnAddServerPlayerEvent(self,args):
        self.LoadPlayerData(args["id"])

    #玩家退出游戏时
    @Listen('PlayerIntendLeaveServerEvent')
    def OnPlayerIntendLeaveServerEvent(self,args):
        #移除服务端数据
        self.RemovePlayerData(args["id"])

#------------------------------------------反作弊区域------------------------------------------#

    #模式改变时
    @Listen('GameTypeChangedServerEvent')
    def OnGameTypeChangedServerEvent(self,args):
        compCreateName = FACTORY.CreateName(args["playerId"])
        name = compCreateName.GetName()
        #如果为创造则改模式并踢掉
        if args["newGameType"] == 1 and uidDict[args["playerId"]] not in whiteList:
            CMD("/gamemode 0 " + name)
            CMD("/kick " + name)

    #使用命令时
    @Listen('CommandEvent')
    def OnCommandEvent(self,args):
        compCreateName = FACTORY.CreateName(args["playerId"])
        name = compCreateName.GetName()
        if uidDict[args["entityId"]] not in whiteList:
            args["cancel"] = True
            CMD("/kick " + name)

    #防作弊
    def Safety(self):
        if not DEBUG:
            CMD("/deop @a")
            CMD("/gamerule commandblocksenabled true")

#------------------------------------------主逻辑监听区域------------------------------------------#
#@Listen后可传入事件名，这样函数就可以自己起名了。
#如果单独写@Listen或不写，服务端调用的函数名与本文件函数重名，依然会调用该函数。

    #回调指令
    @Listen
    def OnSetCommand(self, args):
        CMD(args['command'], args['__id__'])

    #玩家点击催发货按钮
    @Listen('UrgeShipEvent')
    def OnUrgeShipEvent(self, args):
        self.CallClient(args['playerId'], 'OnRepeat', {'message': args['message']})
        playerId = args["playerId"]
        GOODS_CMD.executeCMD("buyFreeChest",playerId)

    #玩家聊天时
    @Listen('ServerChatEvent')
    def OnServerChat(self, args):
        self.GetUrgentNotice()
        return
        self.CallClient(args['playerId'], 'OnRepeat', {'message': args['message']})
        playerId = args["playerId"]
        GOODS_CMD.executeCMD("buyFreeChest",playerId)

        
