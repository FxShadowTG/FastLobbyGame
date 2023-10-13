# -*- coding: utf-8 -*-
import client.extraClientApi as clientApi
import Config as CONFIG
CF = clientApi.GetEngineCompFactory()
PID = clientApi.GetLocalPlayerId()
eventList = []
# 一个装饰器，使某个服务端类的函数变成回调函数。
# funcOrStr：既可以是函数，也可以是事件名称。
# EN：EngineNamespace，ESN：EngineSystemName，不传则默认监听游戏本体事件。
# 本模板封装了更方便的通信接口，所以EN，ESN这两个参数可能无需使用。
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
        # 无需在此处监听引擎事件，请使用@Listen；无需监听服务端自定义事件，请在服务端使用CallClient或CallAllClient。

    # 无需改动。此处监听来自服务端的事件进行函数分发
    @Listen('ServerEvent', CONFIG.MOD_NAME, 'ServerSystem')
    def OnGetServerEvent(self, args):
        getattr(self, args['funcName'])(args['funcArgs'])

    # 无需改动。调用服务端函数并发送数据。（str，服务端函数名称，dict：要发送的数据字典）自带'__id__'表示客户端玩家id。
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
        self.Tellraw(CONFIG.MOD_NAME + '客户端： ' + 'UiInitFinished')
        uiName = 'uiName'
        # clientApi.RegisterUI(CONFIG.MOD_NAME, uiName, CONFIG.MOD_NAME+'.'+uiName+'.'+uiName, uiName+'.main')
        # self.uiNode = clientApi.CreateUI(CONFIG.MOD_NAME, uiName, {'isHud': 1})

    def OnRepeat(self, args):
        self.Tellraw(CONFIG.MOD_NAME + '客户端收到： ' + args['message'])