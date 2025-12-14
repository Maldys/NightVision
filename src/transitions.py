from state import State
from fsm_event import Fsm_Event
from context import Context
from fsm_event import Fsm_Event
from threading import Thread
from cross_type import Cross_type
from reset import kill_other_instances
from mode import Mode



def logger(state, ctx: Context):
    print('Prechod do stavu: ' + str(state))
    ctx.state = state

def test_trans(state, ctx: Context):
    logger(state,ctx)

def save_ctx_trans(state, ctx: Context):
    logger(state, ctx)
    off_menu_trans(state, ctx)
    ctx.context_saver.save_ctx()



def cam_live(state, ctx: Context):
    kill_other_instances()
    logger(state,ctx)
    ctx.camera.live()
        
    

def cam_off(state, ctx: Context):
    logger(state,ctx)
    ctx.camera.shutdown()

def menu_trans(state, ctx: Context):
    logger(state,ctx)
    text = str(state).replace('State.', "")
    if 'MENU_' in text: 
        text = text.replace('MENU_', '')
    text = text.replace('_', ' ')
    ctx.text_to_show = text

def off_menu_trans(state, ctx: Context):
    text = ''
    ctx.text_to_show = text

def setter_trans_clr(state, ctx: Context, toast_text: str):
    menu_trans(state, ctx)
    ctx.camera.show_toast(toast_text)

def setter_trans_xy(state, ctx: Context):
    menu_trans(state, ctx)
    ctx.camera.show_toast('X, Y [' + str(ctx.cross_params[ctx.sel_cross].x_offset) + ', ' + str(ctx.cross_params[ctx.sel_cross].y_offset) + ']')
    

def setter_trans_type(state, ctx: Context, toast_text: str):
    menu_trans(state, ctx)
    ctx.camera.show_toast(toast_text)





#obsluzne funkce (set xy, set color etc.)

def set_color(state, ctx: Context):
    if state == State.MENU_CROSS_COLOR_R:
        ctx.cross_params[ctx.sel_cross].color = (255, 0, 0)
        color_str = 'RED'
    elif state == State.MENU_CROSS_COLOR_G:
        ctx.cross_params[ctx.sel_cross].color = (0, 255, 0)
        color_str = 'GREEN'
    elif state == State.MENU_CROSS_COLOR_B:
        ctx.cross_params[ctx.sel_cross].color = (0, 0, 255)
        color_str = 'BLUE'
    
    setter_trans_clr(state, ctx, color_str + ' COLOR SET')

def set_xy_plus(state, ctx: Context):
    if state == State.MENU_CROSS_X_SET:
        x = ctx.cross_params[ctx.sel_cross].x_offset
        if x < 100:
            x = x+1
        ctx.cross_params[ctx.sel_cross].x_offset = x
    elif state == State.MENU_CROSS_Y_SET:
        y = ctx.cross_params[ctx.sel_cross].y_offset
        if y < 100:
            y = y+1
        ctx.cross_params[ctx.sel_cross].y_offset = y

def set_xy_minus(state, ctx: Context):
    if state == State.MENU_CROSS_X_SET:
        x = ctx.cross_params[ctx.sel_cross].x_offset
        if x > -100:
            x = x-1
        ctx.cross_params[ctx.sel_cross].x_offset = x
    elif state == State.MENU_CROSS_Y_SET:
        y = ctx.cross_params[ctx.sel_cross].y_offset
        if y > -100:
            y = y-1
        ctx.cross_params[ctx.sel_cross].y_offset = y   

def set_cross_type(state, ctx: Context):
    if state == State.MENU_CROSS_TYPE_CROSS:
        ctx.cross_params[ctx.sel_cross].cross_type = Cross_type.CROSS
        str_type = 'CROSS'
    elif state == State.MENU_CROSS_TYPE_DOT:
        ctx.cross_params[ctx.sel_cross].cross_type = Cross_type.DOT
        str_type = 'DOT'
    elif state == State.MENU_CROSS_TYPE_HALO:
        ctx.cross_params[ctx.sel_cross].cross_type = Cross_type.HALO
        str_type = 'HALO'
    
    setter_trans_type(state, ctx, 'CROSS TYPE SET TO ' + str_type)

def clip(state, ctx: Context):
    logger(state,ctx)
    ctx.camera.make_clip()

def select_config(state, ctx: Context):
    menu_trans(state, ctx)
    num = state.name[len(state.name)-1]
    config_to_select = int(num)
    ctx.sel_cross = config_to_select
    ctx.camera.show_toast(f'SELECTED CONFIG: {config_to_select}')

def switch_mode(state, ctx: Context):
    menu_trans(state, ctx)
    if ctx.mode == Mode.DAY:
        sw_mode = Mode.NIGHT
    else:
        sw_mode = Mode.DAY
    ctx.mode = sw_mode
    ctx.camera.change_mode()
    ctx.camera.show_toast(f"{sw_mode.name} SELECTED")
    






transitions = {
    (State.OFF, Fsm_Event.PWR_BTN_LONG): (State.LIVE, cam_live), #misto (state, event): state jde udelat (state, event): (state, acition)
    (State.LIVE, Fsm_Event.MENU_BTN): (State.MENU_CROSS, menu_trans),
    ('ANY', Fsm_Event.PWR_BTN_LONG): (State.OFF, cam_off),
    (State.LIVE, Fsm_Event.REC_BTN): (State.LIVE, clip),
    (State.MENU_CROSS, Fsm_Event.ENC_A_LEFT): (State.MENU_SELECT_CONFIG, menu_trans),#cross-view_mode main
    (State.MENU_CROSS, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE, menu_trans),#cross-view_mode main
    (State.MENU_CROSS, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, menu_trans),#cross/color
    (State.MENU_CROSS_COLOR, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_Y, menu_trans),#color-y
    (State.MENU_CROSS_Y, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_X, menu_trans),#x-y
    (State.MENU_CROSS_COLOR, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE, menu_trans),#color-type
    (State.MENU_CROSS_COLOR, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR_R, menu_trans),#color/r
    (State.MENU_CROSS_COLOR_R, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR_R, set_color),#r-color vyber moznosti
    (State.MENU_CROSS_COLOR_R, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_G, menu_trans), #r-g
    (State.MENU_CROSS_COLOR_R, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_B, menu_trans), #r-b
    (State.MENU_CROSS_COLOR_G, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR_G, set_color),#g-color vyber moznosti
    (State.MENU_CROSS_COLOR_G, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_B, menu_trans), #g-b
    (State.MENU_CROSS_COLOR_G, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_R, menu_trans), #g-r
    (State.MENU_CROSS_COLOR_B, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR_B, set_color),#b-color vyber moznosti
    (State.MENU_CROSS_COLOR_B, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_R, menu_trans), #b-r
    (State.MENU_CROSS_COLOR_B, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_G, menu_trans), #b-g
    (State.MENU_CROSS_COLOR_R, Fsm_Event.MENU_BTN): (State.MENU_CROSS_COLOR, menu_trans), #r-color
    (State.MENU_CROSS_COLOR_G, Fsm_Event.MENU_BTN): (State.MENU_CROSS_COLOR, menu_trans), #g-color
    (State.MENU_CROSS_COLOR_B, Fsm_Event.MENU_BTN): (State.MENU_CROSS_COLOR, menu_trans), #b-color
    (State.MENU_CROSS_TYPE, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR, menu_trans),#type-color
    (State.MENU_CROSS_X, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_Y, menu_trans),#x-y
    (State.MENU_CROSS_TYPE, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_X, menu_trans),#type-x
    (State.MENU_CROSS_X, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE, menu_trans),#x-type
    (State.MENU_CROSS_TYPE, Fsm_Event.MENU_BTN): (State.MENU_CROSS, menu_trans),#type-cross
    (State.MENU_CROSS_TYPE, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE_CROSS, menu_trans),#type/cross
    (State.MENU_CROSS_TYPE_CROSS, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE_CROSS, set_cross_type),#cross vyber moznosti
    (State.MENU_CROSS_TYPE_CROSS, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_DOT, menu_trans), #cross-dot
    (State.MENU_CROSS_TYPE_CROSS, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_HALO, menu_trans), #cross-halo
    (State.MENU_CROSS_TYPE_CROSS, Fsm_Event.MENU_BTN): (State.MENU_CROSS_TYPE, menu_trans),#cross-menu
    (State.MENU_CROSS_TYPE_DOT, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE_DOT, set_cross_type),#dot vyber moznosti
    (State.MENU_CROSS_TYPE_DOT, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_HALO, menu_trans), #dot-halo
    (State.MENU_CROSS_TYPE_DOT, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_CROSS, menu_trans), #dot-cross
    (State.MENU_CROSS_TYPE_DOT, Fsm_Event.MENU_BTN): (State.MENU_CROSS_TYPE, menu_trans),#dot-type
    (State.MENU_CROSS_TYPE_HALO, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE_HALO, set_cross_type),#dot vyber moznosti
    (State.MENU_CROSS_TYPE_HALO, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_CROSS, menu_trans), #halo-cross
    (State.MENU_CROSS_TYPE_HALO, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_DOT, menu_trans), #halo-dot
    (State.MENU_CROSS_TYPE_HALO, Fsm_Event.MENU_BTN): (State.MENU_CROSS_TYPE, menu_trans),#halo-type
    (State.MENU_CROSS_COLOR, Fsm_Event.MENU_BTN): (State.MENU_CROSS, menu_trans),#color-cross
    (State.MENU_CROSS_Y, Fsm_Event.MENU_BTN): (State.MENU_CROSS, menu_trans),#y-cross
    (State.MENU_CROSS_Y, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_Y_SET, menu_trans),#y-y vyber moznosti
    (State.MENU_CROSS_Y, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR, menu_trans),#y-color
    (State.MENU_CROSS_X, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_X_SET, menu_trans),#x-x vyber moznosti
    (State.MENU_CROSS_X, Fsm_Event.MENU_BTN): (State.MENU_CROSS, menu_trans),#x-cross
    (State.MENU_CROSS_X_SET, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_X_SET, set_xy_plus),
    (State.MENU_CROSS_X_SET, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_X_SET, set_xy_minus),
    (State.MENU_CROSS_X_SET, Fsm_Event.MENU_BTN): (State.MENU_CROSS_X, setter_trans_xy),
    (State.MENU_CROSS_X_SET, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_X, setter_trans_xy),
    (State.MENU_CROSS_Y_SET, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_Y_SET, set_xy_plus),
    (State.MENU_CROSS_Y_SET, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_Y_SET, set_xy_minus),
    (State.MENU_CROSS_Y_SET, Fsm_Event.MENU_BTN): (State.MENU_CROSS_Y, setter_trans_xy),
    (State.MENU_CROSS_Y_SET, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_Y, setter_trans_xy),
    (State.MENU_VIEW_MODE, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS, menu_trans),#view_mode-cross main
    (State.MENU_VIEW_MODE, Fsm_Event.ENC_A_RIGHT): (State.MENU_SELECT_CONFIG, menu_trans),#view_mode-video main
    (State.MENU_VIEW_MODE, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_DAY, menu_trans),#view_mode/day
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.MENU_BTN): (State.MENU_VIEW_MODE, menu_trans),#day-view_mode
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_DAY, switch_mode),#day-day vyber moznosti
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_NIGHT, menu_trans),#day-grn_night
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_NIGHT, menu_trans),#day-grey_night
    (State.MENU_VIEW_MODE_NIGHT, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_NIGHT, switch_mode),#grey_night - grey_night vyber moznosti
    (State.MENU_VIEW_MODE_NIGHT, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_DAY, menu_trans),#grey_night-day
    (State.MENU_VIEW_MODE_NIGHT, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_DAY, menu_trans),
    (State.MENU_VIEW_MODE_NIGHT, Fsm_Event.MENU_BTN): (State.MENU_VIEW_MODE, menu_trans),
    (State.MENU_CROSS, Fsm_Event.MENU_BTN): (State.LIVE, save_ctx_trans), #cross-live
    (State.MENU_VIEW_MODE, Fsm_Event.MENU_BTN): (State.LIVE, save_ctx_trans), #view_mode-live
    (State.MENU_SELECT_CONFIG, Fsm_Event.MENU_BTN): (State.LIVE, save_ctx_trans),
    (State.MENU_SELECT_CONFIG, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS, menu_trans),
    (State.MENU_SELECT_CONFIG, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE, menu_trans),
    (State.MENU_SELECT_CONFIG, Fsm_Event.ENC_A_BTN): (State.MENU_SELECT_CONFIG_0, menu_trans),
    (State.MENU_SELECT_CONFIG_0, Fsm_Event.MENU_BTN): (State.MENU_SELECT_CONFIG, menu_trans),
    (State.MENU_SELECT_CONFIG_0, Fsm_Event.ENC_A_RIGHT): (State.MENU_SELECT_CONFIG_1, menu_trans),
    (State.MENU_SELECT_CONFIG_0, Fsm_Event.ENC_A_LEFT): (State.MENU_SELECT_CONFIG_4, menu_trans),
    (State.MENU_SELECT_CONFIG_0, Fsm_Event.ENC_A_BTN): (State.MENU_SELECT_CONFIG_0, select_config),
    (State.MENU_SELECT_CONFIG_1, Fsm_Event.MENU_BTN): (State.MENU_SELECT_CONFIG, menu_trans),
    (State.MENU_SELECT_CONFIG_1, Fsm_Event.ENC_A_RIGHT): (State.MENU_SELECT_CONFIG_2, menu_trans),
    (State.MENU_SELECT_CONFIG_1, Fsm_Event.ENC_A_LEFT): (State.MENU_SELECT_CONFIG_1, menu_trans),
    (State.MENU_SELECT_CONFIG_1, Fsm_Event.ENC_A_BTN): (State.MENU_SELECT_CONFIG_1, select_config),
    (State.MENU_SELECT_CONFIG_2, Fsm_Event.MENU_BTN): (State.MENU_SELECT_CONFIG, menu_trans),
    (State.MENU_SELECT_CONFIG_2, Fsm_Event.ENC_A_RIGHT): (State.MENU_SELECT_CONFIG_3, menu_trans),
    (State.MENU_SELECT_CONFIG_2, Fsm_Event.ENC_A_LEFT): (State.MENU_SELECT_CONFIG_1, menu_trans),
    (State.MENU_SELECT_CONFIG_2, Fsm_Event.ENC_A_BTN): (State.MENU_SELECT_CONFIG_2, select_config),
    (State.MENU_SELECT_CONFIG_3, Fsm_Event.MENU_BTN): (State.MENU_SELECT_CONFIG, menu_trans),
    (State.MENU_SELECT_CONFIG_3, Fsm_Event.ENC_A_RIGHT): (State.MENU_SELECT_CONFIG_4, menu_trans),
    (State.MENU_SELECT_CONFIG_3, Fsm_Event.ENC_A_LEFT): (State.MENU_SELECT_CONFIG_2, menu_trans),
    (State.MENU_SELECT_CONFIG_3, Fsm_Event.ENC_A_BTN): (State.MENU_SELECT_CONFIG_3, select_config),
    (State.MENU_SELECT_CONFIG_4, Fsm_Event.MENU_BTN): (State.MENU_SELECT_CONFIG, menu_trans),
    (State.MENU_SELECT_CONFIG_4, Fsm_Event.ENC_A_RIGHT): (State.MENU_SELECT_CONFIG_1, menu_trans),
    (State.MENU_SELECT_CONFIG_4, Fsm_Event.ENC_A_LEFT): (State.MENU_SELECT_CONFIG_3, menu_trans),
    (State.MENU_SELECT_CONFIG_4, Fsm_Event.ENC_A_BTN): (State.MENU_SELECT_CONFIG_4, select_config),
}