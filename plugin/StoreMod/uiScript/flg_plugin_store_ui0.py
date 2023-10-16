# -*- coding: utf-8 -*-
import client.extraClientApi as clientApi
import FastLobbyGameMod.modCommon.Config as Config  #请自行前缀为你的mod名
# Client就是你的客户端，你可以用Client.xxx调用客户端函数。
Client = clientApi.GetSystem(Config.PLUGIN_STORE_MOD_PATH, 'ClientSystem')
ScreenNode = clientApi.GetScreenNodeCls()
CLIENT_FACTORY = clientApi.GetEngineCompFactory()
PLAYER_ID = clientApi.GetLocalPlayerId()

class flg_plugin_store_ui0(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        # self.levelId = clientApi.GetLevelId()
        # #获取UI模式
        # self.compCreatePlayerView = CLIENT_FACTORY.CreatePlayerView(self.levelId)

    def Create(self):
        self.shopPanel_control = self.GetBaseUIControl("/shopPanel")
        self.shopPanel_control.SetVisible(True, True)

        #关闭按钮
        self.shopPanel_closeButton_control = self.shopPanel_control.GetChildByName("closeButton")
        self.shopPanel_closeButton_control.asButton().AddTouchEventParams()
        self.shopPanel_closeButton_control.asButton().SetButtonTouchDownCallback(self.shopPanel_closeButton_click)

        #显示商店
        self.storeButton_control = self.GetBaseUIControl("/storeButton")
        self.storeButton_control.asButton().AddTouchEventParams()
        self.storeButton_control.asButton().SetButtonTouchDownCallback(self.storeButton_click)
        self.storeButton_control.SetVisible(True, True)

        #玩家背包物品栏按钮映射
        self.reflectPlayerStoreBagList = []
        for i in range(0,36):
            path = "mainBackground/ownerPanel/bagPanel/gird_touch_button" + str(i)
            self.reflectPlayerStoreBagList.append(self.shopPanel_control.GetChildByName(path))
            self.reflectPlayerStoreBagList[i].asButton().AddTouchEventParams()
            self.reflectPlayerStoreBagList[i].asButton().SetButtonTouchDownCallback(self.addItem_click)
        self.RenderStorePlayerBag()

    #渲染商店玩家背包
    def RenderStorePlayerBag(self):
        for i in range(0,36):
            path = "/mainBackground/ownerPanel/bagPanel/gird_touch_button" + str(i) + "/item_renderer"
            itemName = "minecraft:wool"
            auxValue = 0
            self.shopPanel_item_render_control = self.shopPanel_control.GetChildByName(path)
            self.shopPanel_item_render_control.asItemRenderer().SetUiItem(itemName, auxValue,True)

    def addItem_click(self,args):
        print("666")
        self.GetPlayerBag()
        #通知服务端请求获取当前格子的物品

    #获取玩家背包信息
    def GetPlayerBag(self):
        Client.CallServer('GetPlayerBag', {'playerId': PLAYER_ID})
        print("aa")

    def storeButton_click(self,args):
        self.shopPanel_control.SetVisible(True, True)

    def shopPanel_closeButton_click(self,args):
        self.shopPanel_control.SetVisible(False, False)

    def Destroy(self):
        pass

    def Update(self):
        pass