# -*- coding: utf-8 -*-
import client.extraClientApi as clientApi
import Config as DB
# Client就是你的客户端，你可以用Client.xxx调用客户端函数。
Client = clientApi.GetSystem(DB.ModName, 'ClientSystem')
ScreenNode = clientApi.GetScreenNodeCls()
CF = clientApi.GetEngineCompFactory()
PID = clientApi.GetLocalPlayerId()
class uiname(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)

    def Create(self):
        pass

    def Destroy(self):
        pass

    def Update(self):
        pass