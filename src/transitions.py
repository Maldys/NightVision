from state import State
from fsm_event import Fsm_Event
from context import Context
from fsm_event import Fsm_Event
from threading import Thread



def logger(state, ctx: Context):
    print('Prechod do stavu: ' + str(state))
    ctx.state = state

def test_trans(state, ctx: Context):
    logger(state,ctx)


def cam_live(state, ctx: Context):
    logger(state,ctx)
    ctx.camera.live()
        
    

def cam_off(state, ctx: Context):
    logger(state,ctx)
    ctx.camera.shutdown()

def menu_trans(state, ctx: Context):
    logger(state,ctx)
    text = str(state).replace('State.', "")
    ctx.cross_params.text_to_show = text

def off_menu_trans(state, ctx: Context):
    logger(state,ctx)
    text = ''
    ctx.cross_params.text_to_show = text




transitions = {
    (State.OFF, Fsm_Event.PWR_BTN_LONG): (State.LIVE, cam_live), #misto (state, event): state jde udelat (state, event): (state, acition)
    (State.LIVE, Fsm_Event.MENU_BTN): (State.MENU_CROSS, menu_trans),
    ('ANY', Fsm_Event.PWR_BTN_LONG): (State.OFF, cam_off),
    (State.LIVE, Fsm_Event.REC_BTN): (State.CLIP, test_trans),
    (State.CLIP, Fsm_Event.REC_BTN): (State.LIVE, test_trans),
    (State.LIVE, Fsm_Event.PWR_BTN_LONG): (State.OFF, cam_off),
    (State.CLIP, Fsm_Event.PWR_BTN_LONG): (State.OFF, cam_off),
    (State.MENU_CROSS, Fsm_Event.ENC_A_LEFT): (State.MENU_LANGUAGE, menu_trans),#cross-language main
    (State.MENU_CROSS, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE, menu_trans),#cross-view_mode main
    (State.MENU_CROSS, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, menu_trans),#cross/color
    (State.MENU_CROSS_COLOR, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_Y, menu_trans),#color-y
    (State.MENU_CROSS_Y, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_X, menu_trans),#x-y
    (State.MENU_CROSS_COLOR, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE, menu_trans),#color-type
    (State.MENU_CROSS_COLOR, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR_R, menu_trans),#color/r
    (State.MENU_CROSS_COLOR_R, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, menu_trans),#r-color vyber moznosti
    (State.MENU_CROSS_COLOR_R, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_G, menu_trans), #r-g
    (State.MENU_CROSS_COLOR_R, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_B, menu_trans), #r-b
    (State.MENU_CROSS_COLOR_G, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, menu_trans),#g-color vyber moznosti
    (State.MENU_CROSS_COLOR_G, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_B, menu_trans), #g-b
    (State.MENU_CROSS_COLOR_G, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_R, menu_trans), #g-r
    (State.MENU_CROSS_COLOR_B, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, menu_trans),#b-color vyber moznosti
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
    (State.MENU_CROSS_TYPE_CROSS, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE, menu_trans),#cross-type vyber moznosti
    (State.MENU_CROSS_TYPE_CROSS, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_DOT, menu_trans), #cross-dot
    (State.MENU_CROSS_TYPE_CROSS, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_HALO, menu_trans), #cross-halo
    (State.MENU_CROSS_TYPE_DOT, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE, menu_trans),#dot-type vyber moznosti
    (State.MENU_CROSS_TYPE_DOT, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_HALO, menu_trans), #dot-halo
    (State.MENU_CROSS_TYPE_DOT, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_CROSS, menu_trans), #dot-cross
    (State.MENU_CROSS_TYPE_HALO, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE, menu_trans),#dot-type vyber moznosti
    (State.MENU_CROSS_TYPE_HALO, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_CROSS, menu_trans), #halo-cross
    (State.MENU_CROSS_TYPE_HALO, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_DOT, menu_trans), #halo-dot
    (State.MENU_CROSS_COLOR, Fsm_Event.MENU_BTN): (State.MENU_CROSS, menu_trans),#color-cross
    (State.MENU_CROSS_Y, Fsm_Event.MENU_BTN): (State.MENU_CROSS, menu_trans),#y-cross
    (State.MENU_CROSS_Y, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_Y, menu_trans),#y-y vyber moznosti
    (State.MENU_CROSS_Y, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR, menu_trans),#y-color
    (State.MENU_CROSS_X, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_X, menu_trans),#x-x vyber moznosti
    (State.MENU_CROSS_X, Fsm_Event.MENU_BTN): (State.MENU_CROSS, menu_trans),#x-cross
    (State.MENU_VIEW_MODE, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS, menu_trans),#view_mode-cross main
    (State.MENU_VIEW_MODE, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO, menu_trans),#view_mode-video main
    (State.MENU_VIEW_MODE, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_DAY, menu_trans),#view_mode/day
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.MENU_BTN): (State.MENU_VIEW_MODE, menu_trans),#day-view_mode
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_DAY, menu_trans),#day-day vyber moznosti
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_GRN_NIGHT, menu_trans),#day-grn_night
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_GREY_NIGHT, menu_trans),#day-grey_night
    (State.MENU_VIEW_MODE_GRN_NIGHT, Fsm_Event.MENU_BTN): (State.MENU_VIEW_MODE, menu_trans),#grn_night-view_mode
    (State.MENU_VIEW_MODE_GRN_NIGHT, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_GRN_NIGHT, menu_trans),#grn_night - grn_night vyber moznosti
    (State.MENU_VIEW_MODE_GRN_NIGHT, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_GREY_NIGHT, menu_trans),#grn_night-grey_night
    (State.MENU_VIEW_MODE_GRN_NIGHT, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_DAY, menu_trans),#grn_night-day
    (State.MENU_VIEW_MODE_GREY_NIGHT, Fsm_Event.MENU_BTN): (State.MENU_VIEW_MODE, menu_trans),#grey_night-view_mode
    (State.MENU_VIEW_MODE_GREY_NIGHT, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_GREY_NIGHT, menu_trans),#grey_night - grey_night vyber moznosti
    (State.MENU_VIEW_MODE_GREY_NIGHT, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_DAY, menu_trans),#grey_night-day
    (State.MENU_VIEW_MODE_GREY_NIGHT, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_GRN_NIGHT, menu_trans),#grey_night-grn_night
    (State.MENU_VIDEO, Fsm_Event.ENC_A_RIGHT): (State.MENU_LANGUAGE, menu_trans),#video-language main
    (State.MENU_VIDEO, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE, menu_trans),#video-view_mode main
    (State.MENU_VIDEO, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_RES, menu_trans),#video/res
    (State.MENU_VIDEO_RES, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_FPS, menu_trans),#res-fps
    (State.MENU_VIDEO_RES, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_CLIP_AFTER, menu_trans),#res-clip_after
    (State.MENU_VIDEO_RES, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_RES_720, menu_trans),#res-720
    (State.MENU_VIDEO_RES_720, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_RES_720, menu_trans),#720-720 vyber moznosti
    (State.MENU_VIDEO_RES_720, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_RES_1080, menu_trans),#720-1080
    (State.MENU_VIDEO_RES_720, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_RES_1080, menu_trans),#720-1080 
    (State.MENU_VIDEO_RES_720, Fsm_Event.MENU_BTN): (State.MENU_VIDEO_RES, menu_trans),#720-res 
    (State.MENU_VIDEO_RES_1080, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_RES_1080, menu_trans),#720-720 vyber moznosti
    (State.MENU_VIDEO_RES_1080, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_RES_720, menu_trans),#720-1080
    (State.MENU_VIDEO_RES_1080, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_RES_720, menu_trans),#720-1080 
    (State.MENU_VIDEO_RES_1080, Fsm_Event.MENU_BTN): (State.MENU_VIDEO_RES, menu_trans),#1080-res 
    (State.MENU_VIDEO_FPS, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_CLIP_BEFORE, menu_trans),#fps-clip
    (State.MENU_VIDEO_FPS, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_RES, menu_trans),#fps-res
    (State.MENU_VIDEO_FPS, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_FPS_SET, menu_trans),#fps-fps_set
    (State.MENU_VIDEO_FPS_SET, Fsm_Event.MENU_BTN): (State.MENU_VIDEO_FPS, menu_trans),#fps_set-fps
    (State.MENU_VIDEO_CLIP_AFTER, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_RES, menu_trans),#clip_after-res
    (State.MENU_VIDEO_CLIP_AFTER, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_CLIP_BEFORE, menu_trans),#clip_after-clip_before
    (State.MENU_VIDEO_RES, Fsm_Event.MENU_BTN): (State.MENU_VIDEO, menu_trans),#res-video
    (State.MENU_VIDEO_FPS, Fsm_Event.MENU_BTN): (State.MENU_VIDEO, menu_trans),#fps-video
    (State.MENU_VIDEO_CLIP_AFTER, Fsm_Event.MENU_BTN): (State.MENU_VIDEO, menu_trans),#clip-video
    (State.MENU_VIDEO_CLIP_AFTER, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_CLIP_AFTER_SET, menu_trans), #clip_after-clip_after_set
    (State.MENU_VIDEO_CLIP_AFTER_SET, Fsm_Event.MENU_BTN): (State.MENU_VIDEO_CLIP_AFTER, menu_trans), #clip_after-clip_after_set
    (State.MENU_VIDEO_CLIP_BEFORE, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_CLIP_BEFORE_SET, menu_trans), #clip_before-clip_before_set
    (State.MENU_VIDEO_CLIP_BEFORE_SET, Fsm_Event.MENU_BTN): (State.MENU_VIDEO_CLIP_BEFORE, menu_trans), #clip_before_set-clip_before
    (State.MENU_VIDEO_CLIP_BEFORE, Fsm_Event.MENU_BTN): (State.MENU_VIDEO, menu_trans), #clip_before-video
    (State.MENU_VIDEO_CLIP_BEFORE, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_CLIP_AFTER, menu_trans), #clip_before-clip_after
    (State.MENU_VIDEO_CLIP_BEFORE, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_FPS, menu_trans), #clip_before-fps
    (State.MENU_LANGUAGE, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS, menu_trans),#language-cross main
    (State.MENU_LANGUAGE, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO, menu_trans),#language-video main
    (State.MENU_LANGUAGE, Fsm_Event.ENC_A_BTN): (State.MENU_LANGUAGE_CZ, menu_trans), #language/cz
    (State.MENU_LANGUAGE_CZ, Fsm_Event.ENC_A_BTN): (State.MENU_LANGUAGE_CZ, menu_trans), #cz-cz
    (State.MENU_LANGUAGE_CZ, Fsm_Event.MENU_BTN): (State.MENU_LANGUAGE, menu_trans), #cz-language
    (State.MENU_CROSS, Fsm_Event.MENU_BTN): (State.LIVE, off_menu_trans), #cross-live
    (State.MENU_VIDEO, Fsm_Event.MENU_BTN): (State.LIVE, off_menu_trans), #video-live
    (State.MENU_VIEW_MODE, Fsm_Event.MENU_BTN): (State.LIVE, off_menu_trans), #view_mode-live
    (State.MENU_LANGUAGE, Fsm_Event.MENU_BTN): (State.LIVE, off_menu_trans), #language-live
    
}