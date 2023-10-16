# -*- coding: utf-8 -*-
import server.extraServerApi as serverApi
import FastLobbyGameMod.modCommon.Config as Config  #请自行前缀为你的mod名
import logging
import time
from math import floor

CODE_VERSION = Config.CODE_VERSION
DEBUG = Config.DEBUG
FACTORY = Config.SERVER_FACTORY
CMD = Config.COMMAND
LEVEL_ID = Config.LEVELID
CONNECT_BY_GET = Config.CONNECT_BY_GET
CONNECT_BY_SET = Config.CONNECT_BY_SET
CREATE_GAME_BY_LEVELID = Config.CREATE_GAME_BY_LEVELID

eventList = []  #监听中的事件
# wholeExtraDataDict = {} #实体信息
# playerList = [] #玩家列表
# whiteList = []  #管理员列表
# uidDict = {}    #玩家的UID
# playerGoodsDict = {}    #玩家拥有的商品（商品 = 实现指令）
# playerSpanItemsDict = {}    #玩家拥有的跨房物品

# cdDict = {} #冷却变量表（每秒-1）

# if DEBUG:
#     whiteList.append("1292492939") #添加你的测试启动器开发者账号的UID

#所有具体用法可查看主体服务端ServerSystem文件，这里不再赘述。
def Listen(funcOrStr=None, EN=serverApi.GetEngineNamespace(), ESN=serverApi.GetEngineSystemName()):
    def binder(func):
        eventList.append((EN, ESN, funcOrStr if isinstance(funcOrStr, str)else func.__name__, func))
        return func
    return binder(funcOrStr)if callable(funcOrStr)else binder

class ServerSystem(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, systemName):
        super(ServerSystem, self).__init__(namespace, systemName)
        logging.info( "code version: " + CODE_VERSION)  
        for EN, ESN, eventName, callback in eventList:
            self.ListenForEvent(EN, ESN, eventName, self, callback)
        # self.InitWorld()
        # self.InitOptions()
        
    def Destroy(self):
        for EN, ESN, eventName, callback in eventList:
            self.UnListenForEvent(EN, ESN, eventName, self, callback)

    @Listen('ClientEvent', Config.MOD_NAME, 'ClientSystem')
    def OnGetClientEvent(self, args):
        args['funcArgs']['__id__'] = args['__id__']
        getattr(self, args['funcName'])(args['funcArgs'])

    if Config.PLUGIN_STORE_MOD_STATUS:
        @Listen('ClientEvent', Config.PLUGIN_STORE_MOD_PATH, 'ClientSystem')
        def OnGetClientEvent(self, args):
            args['funcArgs']['__id__'] = args['__id__']
            getattr(self, args['funcName'])(args['funcArgs'])

    def CallClient(self, playerId, funcName, funcArgs):
        self.NotifyToClient(playerId, 'ServerEvent', {'funcName': funcName, 'funcArgs': funcArgs})

    def CallAllClient(self, funcName, funcArgs):
        self.BroadcastToAllClient('ServerEvent', {'funcName': funcName, 'funcArgs': funcArgs})

#------------------------------------------test------------------------------------------#

    #callback - 请求指令
    @Listen
    def OnSetCommand(self, args):
        CMD(args['command'], args['__id__'])

    #callBack - 获取背包所有物品
    @Listen
    def GetPlayerBag(self, args):
        print("这里是store的GetPlayerBag server")
        CMD("/give @s glass",args["playerId"])
        return
        
    #玩家聊天时
    @Listen('ServerChatEvent')
    def OnServerChat(self, args):
        print("这里是store的ServerChatEvent")
        CMD("/give @s glass",args["playerId"])
        return
