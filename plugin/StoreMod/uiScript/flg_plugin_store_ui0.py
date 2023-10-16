# -*- coding: utf-8 -*-
import client.extraClientApi as clientApi
import FastLobbyGameMod.modCommon.Config as Config  #请自行前缀为你的mod名
import re
# Client就是你的客户端，你可以用Client.xxx调用客户端函数。
Client = clientApi.GetSystem(Config.PLUGIN_STORE_MOD_PATH, 'ClientSystem')
ScreenNode = clientApi.GetScreenNodeCls()
CLIENT_FACTORY = clientApi.GetEngineCompFactory()
PLAYER_ID = clientApi.GetLocalPlayerId()
LEVEL_ID = Config.LEVELID
CREATE_ITEM = CLIENT_FACTORY.CreateItem(LEVEL_ID)

class flg_plugin_store_ui0(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        # #获取UI模式
        # self.compCreatePlayerView = CLIENT_FACTORY.CreatePlayerView(self.levelId)
        #玩家在商城背包中的当前选中的物品，即展示框上的物品
        self.currentSelectingItemDict = {}

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
            self.reflectPlayerStoreBagList[i].asButton().SetButtonTouchDownCallback(self.AddItemToDisplayFrame)

        #获取上架渲染展示区的实例
        self.shopPanel_display_asItemRenderer_control = self.shopPanel_control.GetChildByName("mainBackground/ownerPanel/displayBackground/item_base_background/item_renderer").asItemRenderer()
        self.shopPanel_display_asLabel_control = self.shopPanel_control.GetChildByName("mainBackground/ownerPanel/displayBackground/base_info_background/itemInformation").asLabel()
        self.shopPanel_display_countEditBox_asTextEditBox_control = self.shopPanel_control.GetChildByName("mainBackground/ownerPanel/displayBackground/base_info_background/countEditBox").asTextEditBox()
        self.shopPanel_display_priceEditBox_asTextEditBox_control = self.shopPanel_control.GetChildByName("mainBackground/ownerPanel/displayBackground/base_info_background/priceEditBox").asTextEditBox()

        #获取前往小店和上架商品按钮
        self.shopPanel_display_changeToMyStoreButton_control = self.shopPanel_control.GetChildByName("mainBackground/ownerPanel/changeToMyStoreButton")
        self.shopPanel_display_changeToMyStoreButton_control.asButton().AddTouchEventParams()
        self.shopPanel_display_changeToMyStoreButton_control.asButton().SetButtonTouchDownCallback(self.JumpPage)
        self.shopPanel_display_upload_control = self.shopPanel_control.GetChildByName("mainBackground/ownerPanel/uploadButton")
        self.shopPanel_display_upload_control.asButton().AddTouchEventParams()
        self.shopPanel_display_upload_control.asButton().SetButtonTouchDownCallback(self.uploadItem_click)
    
    #跳转页面
    def JumpPage(self,args):
        print("JumpPage")

    #点击上架按钮的回调
    def uploadItem_click(self,args):
        count = self.shopPanel_display_countEditBox_asTextEditBox_control.GetEditText()
        price = self.shopPanel_display_priceEditBox_asTextEditBox_control.GetEditText()
        #只能为数字并且数量不能超过物品本身
        if count.isdigit() == False or price.isdigit() == False or int(count) > self.currentSelectingItemDict["count"]:
            self.shopPanel_display_countEditBox_asTextEditBox_control.SetEditText("")
            self.shopPanel_display_priceEditBox_asTextEditBox_control.SetEditText("")
            return
        
        count = int(count)
        price = int(price)

        #提交物品到服务端
        playerOrderData = Client.CreateEventData()
        playerOrderData["count"] = count
        playerOrderData["price"] = price
        playerOrderData["itemDict"] = self.currentSelectingItemDict
        Client.CallServer('UploadItemToStore', playerOrderData)
        self.RefreshUploadDatum()

    #刷新上架页面全部数据
    def RefreshUploadDatum(self):
        self.currentSelectingItemDict = None
        self.shopPanel_display_countEditBox_asTextEditBox_control.SetEditText("")
        self.shopPanel_display_priceEditBox_asTextEditBox_control.SetEditText("")
        self.shopPanel_display_asItemRenderer_control.asItemRenderer().SetUiItem("flg_fx:air", 0,True)
        self.RenderStorePlayerBag()
        self.RenderDisplayAreaInformation()

    #渲染商店玩家背包
    def RenderStorePlayerBag(self):
        #获取当前背包里的所有物品
        compCreateItem = CLIENT_FACTORY.CreateItem(PLAYER_ID)
        itemsList = compCreateItem.GetPlayerAllItems(clientApi.GetMinecraftEnum().ItemPosType.INVENTORY)
        for i in range(0,36):
            path = "/mainBackground/ownerPanel/bagPanel/gird_touch_button" + str(i) + "/item_renderer"
            self.shopPanel_item_render_control = self.shopPanel_control.GetChildByName(path)
            if itemsList[i] != None:
                itemName = itemsList[i]["newItemName"]
                auxValue = itemsList[i]["auxValue"]
                if itemsList[i]["enchantData"] == []:
                    self.shopPanel_item_render_control.asItemRenderer().SetUiItem(itemName, auxValue,False)
                else:
                    self.shopPanel_item_render_control.asItemRenderer().SetUiItem(itemName, auxValue,True)
            else:
                self.shopPanel_item_render_control.asItemRenderer().SetUiItem("flg_fx:air", 0,False)
    
    #玩家添加物品到展示区
    def AddItemToDisplayFrame(self,args):
        number = re.findall(r'\d+', args["ButtonPath"])[-1]
        compCreateItem = CLIENT_FACTORY.CreateItem(PLAYER_ID)
        itemDict = compCreateItem.GetPlayerItem(clientApi.GetMinecraftEnum().ItemPosType.INVENTORY, int(number))
        if itemDict == None or "newItemName" not in itemDict or itemDict["newItemName"] == None:
            return
        if itemDict["enchantData"] == []:
            self.shopPanel_display_asItemRenderer_control.SetUiItem(itemDict["newItemName"], 0,False)
        else:
            self.shopPanel_display_asItemRenderer_control.SetUiItem(itemDict["newItemName"], 0,True)
        self.currentSelectingItemDict = itemDict
        self.RenderDisplayAreaInformation()

    #渲染展示区信息
    def RenderDisplayAreaInformation(self):
        itemDict = self.currentSelectingItemDict
        compCreateItem = CLIENT_FACTORY.CreateItem(CREATE_ITEM)
        if itemDict == None:
            self.shopPanel_display_asLabel_control.SetText("请选中物品")
            return
        info = compCreateItem.GetItemBasicInfo(itemDict["newItemName"], 0, True)
        self.shopPanel_display_asLabel_control.SetText(info["itemName"] + "\n" + str(itemDict["count"]) + "个")

    #获取玩家背包信息
    def GetPlayerBag(self):
        return
    
    def storeButton_click(self,args):
        #渲染
        self.RenderStorePlayerBag()
        self.shopPanel_control.SetVisible(True, True)

    def shopPanel_closeButton_click(self,args):
        self.shopPanel_control.SetVisible(False, False)

    def Destroy(self):
        pass

    def Update(self):
        pass