# -*- coding: utf-8 -*-
from common.mod import Mod
from Config import MOD_NAME
import server.extraServerApi as serverApi
import client.extraClientApi as clientApi
import logging

@Mod.Binding(name = MOD_NAME, version = '0.0.1')
class Main(object):
    def __init__(self):
        logging.info("Template: FastLobbyGameV1.0 by: FxShadow")
    @Mod.InitServer()
    def ServerInit(self):
        serverApi.RegisterSystem(MOD_NAME, 'ServerSystem', MOD_NAME + '.ServerSystem.ServerSystem')
    @Mod.DestroyServer()
    def ServerDestroy(self):
        pass
    @Mod.InitClient()
    def ClientInit(self):
        clientApi.RegisterSystem(MOD_NAME, 'ClientSystem', MOD_NAME + '.ClientSystem.ClientSystem')
    @Mod.DestroyClient()
    def ClientDestroy(self):
        pass