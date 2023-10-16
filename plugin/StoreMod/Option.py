# -*- coding: utf-8 -*-
import server.extraServerApi as serverApi
import client.extraClientApi as clientApi

MOD_NAME = "StoreMod"
SERVER_FACTORY = serverApi.GetEngineCompFactory()
CLIENT_FACTORY = clientApi.GetEngineCompFactory()

LEVELID = serverApi.GetLevelId()    #存档ID
COMMAND = SERVER_FACTORY.CreateCommand(LEVELID).SetCommand #游戏指令
CREATE_GAME_BY_LEVELID = SERVER_FACTORY.CreateGame(LEVELID)

#创建联机大厅双链接
CONNECT_BY_GET = SERVER_FACTORY.CreateHttp(LEVELID)
CONNECT_BY_SET = SERVER_FACTORY.CreateHttp(LEVELID)

#代码版本号（自行修改）
CODE_VERSION = MOD_NAME + " v1"

#云数据KEY配置（不可修改）
CLOUD_KEY_OP_CONFIG = "op_CONFIG",
CLOUD_KEY_ORDERS = "orders"

#云数据KEY配置（可修改）
# CLOUD_KEY_SHOP_GOODS = "shopGoods",
# CLOUD_KEY_SPAN_GOODS = "spanItems"

#DEBUG
DEBUG = True
