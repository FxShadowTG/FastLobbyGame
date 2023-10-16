from FastLobbyGameMod.modCommon.Config import SERVER_FACTORY   #此处需要自行修改Mod的名字
import logging
from math import floor
#实现指令模块
class GoodsCMDClass():

    #初始化商品信息
    def __init__(cls):
        # 物品映射表，需自行添加
        cls.reflexGoodsDict = {
            "buyFreeChest": {"name":"免费宝箱","func":cls.buyFreeChest},
            "buyDiamond": {"name":"钻石","func":cls.buyDiamond}
        }

    #实现指令（请通过此处实现指令）
    def executeCMD(cls,goodsName,playerId):
        try:
            cls.reflexGoodsDict[goodsName]["func"](playerId)
            cls.notifyMessageToPlayer(playerId,cls.reflexGoodsDict[goodsName]["name"])
            return True
        except:
            logging.info("{}: {}: 实现指令出错".format(playerId,goodsName))
            return False
        
    #通知玩家实现成功（str：玩家实体id，str：商品名）
    def notifyMessageToPlayer(cls,playerId,goodsName):
        logging.info("有玩家实现了指令: {}".format(goodsName))
        compCreateMsg = SERVER_FACTORY.CreateMsg(playerId)
        compCreateMsg.NotifyOneMessage(playerId, "恭喜你获得了: {}".format(goodsName), "§6")

    #发放物品给玩家（多出的物品会生成到玩家脚下）
    def sendItem(cls,playerId,itemDict):
        compCreateItem = SERVER_FACTORY.CreateItem(playerId)
        result = compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)
        #如果生成失败就生成在玩家脚下
        if result == False:
            #获取玩家维度
            compCreateDimension = SERVER_FACTORY.CreateDimension(playerId)
            dimension = compCreateDimension.GetEntityDimensionId()
            #获取玩家坐标
            compCreatePos = SERVER_FACTORY.CreatePos(playerId)
            playerIdPos = compCreatePos.GetFootPos()
            playerIdPosX = round(floor((playerIdPos[0])),0)
            playerIdPosY = round(floor((playerIdPos[1])),0)
            playerIdPosZ = round(floor((playerIdPos[2])),0)
            newPlayerPos = (playerIdPosX,playerIdPosY,playerIdPosZ)
            cls.CreateEngineItemEntity(itemDict, dimension, newPlayerPos)

#------------------------------------------实现指令区域------------------------------------------#
    
    def buyFreeChest(cls,playerId):
        itemDict = {'itemName': 'minecraft:chest','count': 1}
        cls.sendItem(playerId,itemDict)

    def buyDiamond(cls,playerId):
        itemDict = {'itemName': 'minecraft:diamond','count': 1}
        cls.sendItem(playerId,itemDict)
