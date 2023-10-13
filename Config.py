# -*- coding: utf-8 -*-
import server.extraServerApi as serverApi
import client.extraClientApi as clientApi

MOD_NAME = __file__.rsplit('/'if'/'in __file__ else'.', 2)[-2]
SERVER_FACTORY = serverApi.GetEngineCompFactory()
CLIENT_FACTORY = clientApi.GetEngineCompFactory()

LEVELID = serverApi.GetLevelId()    #存档ID
COMMAND = SERVER_FACTORY.CreateCommand(LEVELID).SetCommand #游戏指令
CREATE_GAME_BY_LEVELID = SERVER_FACTORY.CreateGame(LEVELID)

#创建联机大厅双链接
CONNECT_BY_GET = SERVER_FACTORY.CreateHttp(LEVELID)
CONNECT_BY_SET = SERVER_FACTORY.CreateHttp(LEVELID)

#代码版本号（自行修改）
CODE_VERSION = "v231014.1"

#云配置数据（通过开发者后台云配置读取，这里仅能修改提示）
MAP_NAME = "未获取到地图名"  #地图名
MAP_NOTICE = "未获取到公告"  #公告
MAP_URGENT_SWITCH = False  #紧急公告开关
MAP_URGENT_NOTICE = "如果你看到这个一直在弹出来，请关闭房间保存地图重新启动"  #紧急公告

#默认游戏规则
DEFAULT_GAME_RULE ={
'option_info': {
    'pvp': True, #玩家伤害
    'show_coordinates': True, #显示坐标
    'fire_spreads': True, #火焰蔓延
    'tnt_explodes': True, #tnt爆炸
    'mob_loot': True, #生物战利品
    'natural_regeneration': True, #自然生命恢复
    'tile_drops': True, #方块掉落
    'immediate_respawn':False #立即重生
    },
'cheat_info': {
    'enable': False, #是否开启作弊
    'mob_griefing': True, #生物破坏方块
    'keep_inventory': True, #保留物品栏
    'weather_cycle': True, #天气更替
    'mob_spawn': True, #生物生成
    'entities_drop_loot': True, #实体掉落
    'daylight_cycle': True, #开启昼夜交替
    'command_blocks_enabled': True, #启用方块命令
    }
}

#云数据KEY配置（不可修改）
CLOUD_KEY_OP_CONFIG = "op_CONFIG",
CLOUD_KEY_ORDERS = "orders"

#云数据KEY配置（可修改）
CLOUD_KEY_SHOP_GOODS = "shopGoods",
CLOUD_KEY_SPAN_GOODS = "spanItems"




#DEBUG
DEBUG = True
