# -*- coding: utf-8 -*-
import client.extraClientApi as clientApi
import FastLobbyGameMod.modCommon.Config as Config  #请自行前缀为你的mod名
CF = clientApi.GetEngineCompFactory()
PID = clientApi.GetLocalPlayerId()
eventList = []

#所有具体用法可查看主体客户端ClientSystem文件，这里不再赘述。
def Listen(funcOrStr=None, EN=clientApi.GetEngineNamespace(), ESN=clientApi.GetEngineSystemName()):
    def binder(func):
        eventList.append((EN, ESN, funcOrStr if isinstance(funcOrStr, str)else func.__name__, func))
        return func
    return binder(funcOrStr)if callable(funcOrStr)else binder

class ClientSystem(clientApi.GetClientSystemCls()):
    def __init__(self, namespace, systemName):
        super(ClientSystem, self).__init__(namespace, systemName)
        for EN, ESN, eventName, callback in eventList:
            self.ListenForEvent(EN, ESN, eventName, self, callback)

    @Listen('ServerEvent', Config.PLUGIN_STORE_MOD_PATH, 'ServerSystem')
    def OnGetServerEvent(self, args):
        getattr(self, args['funcName'])(args['funcArgs'])

    def CallServer(self, funcName, funcArgs):
        self.NotifyToServer('ClientEvent', {'funcName': funcName, 'funcArgs': funcArgs})

#--------------------------------------------------------------------------------------------------------#

    # 客户端指令接口，传入指令字符串即可，执行者为客户端玩家id。
    def CMD(self, command):
        self.CallServer('OnSetCommand', {'command': command})

    def Tellraw(self, text):
        self.CMD('tellraw @s {"rawtext":[{"text":"§f'+text+'"}]}')

    @Listen
    def UiInitFinished(self, args):
        uiName = 'flg_plugin_store_ui0'
        clientApi.RegisterUI(Config.PLUGIN_STORE_MOD_NAME, uiName, Config.PLUGIN_STORE_MOD_UI_PATH+'.'+uiName+'.'+uiName, uiName+'.main')
        self.uiNode = clientApi.CreateUI(Config.PLUGIN_STORE_MOD_NAME, uiName, {'isHud': 1})

    #渲染商店的玩家背包
    @Listen
    def RenderPlayerBagOnStore(self,args):
        self.uiNode.RenderStorePlayerBag(args["itemsList"])

    #刷新上架页面全部数据
    def RefreshUploadDatum(self,args):
        self.uiNode.RefreshUploadDatum()


    def OnRepeat(self, args):
        self.Tellraw(Config.PLUGIN_STORE_MOD_NAME + '客户端收到： ' + args['message'])