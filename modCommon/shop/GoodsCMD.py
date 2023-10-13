from FastLobbyGameMod.Config import SERVER_FACTORY   #此处需要自行修改Mod的名字
import logging

#实现指令模块
class GoodsCMDClass():

    #初始化商品信息
    def __init__(cls):
        # 物品映射表，需自行添加
        cls.reflexGoodsDict = {
            "buyFreeChest": cls.buyFreeChest,
        }

    #实现指令（请通过此处实现指令）
    def executeCMD(cls,goodsName,playerId):
        try:
            cls.reflexGoodsDict[goodsName](playerId)
            return True
        except:
            logging.info("{}: {}: 实现指令出错".format(playerId,goodsName))
            return False
        
    #通知玩家实现成功（str：玩家id，str：商品名）
    def notifyMessageToPlayer(cls,playerId,goodsName):
        logging.info("有玩家实现了指令: {}".format(goodsName))
        compCreateMsg = SERVER_FACTORY.CreateMsg(playerId)
        compCreateMsg.NotifyOneMessage(playerId, "恭喜你获得了: {}".format(goodsName), "§6")

    #发放物品
    def sendItem(cls,playerId,itemDict):
        compCreateItem = SERVER_FACTORY.CreateItem(playerId)
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)

#------------------------------------------具体实现区域------------------------------------------#
    
    def buyFreeChest(cls,playerId):
        itemDict = {'itemName': 'minecraft:chest','count': 1}
        cls.sendItem(playerId,itemDict)
        cls.notifyMessageToPlayer(playerId,"免费宝箱")
