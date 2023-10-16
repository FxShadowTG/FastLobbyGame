# -*- coding: utf-8 -*-
from common.mod import Mod
import modCommon.Config
import server.extraServerApi as serverApi
import client.extraClientApi as clientApi
import logging

print(modCommon.Config.MOD_NAME)
@Mod.Binding(name = modCommon.Config.MOD_NAME, version = '0.0.1')
class Main(object):
    def __init__(self):
        logging.info("Template: FastLobbyGameV1.0 by: FxShadow")
    @Mod.InitServer()
    def ServerInit(self):
        serverApi.RegisterSystem(modCommon.Config.MOD_NAME, 'ServerSystem', modCommon.Config.MOD_NAME + '.ServerSystem.ServerSystem')
        if modCommon.Config.PLUGIN_STORE_MOD_STATUS:
            serverApi.RegisterSystem(modCommon.Config.PLUGIN_STORE_MOD_PATH, 'ServerSystem', modCommon.Config.PLUGIN_STORE_MOD_PATH + '.ServerSystem.ServerSystem')
        logging.info("服务初始化成功")
    @Mod.DestroyServer()
    def ServerDestroy(self):
        pass
    @Mod.InitClient()
    def ClientInit(self):
        clientApi.RegisterSystem(modCommon.Config.MOD_NAME, 'ClientSystem', modCommon.Config.MOD_NAME + '.ClientSystem.ClientSystem')
        if modCommon.Config.PLUGIN_STORE_MOD_STATUS:
            clientApi.RegisterSystem(modCommon.Config.PLUGIN_STORE_MOD_PATH, 'ClientSystem', modCommon.Config.PLUGIN_STORE_MOD_PATH + '.ClientSystem.ClientSystem')
    @Mod.DestroyClient()
    def ClientDestroy(self):
        pass