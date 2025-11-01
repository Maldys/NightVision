from state import State
from fsm_event import Fsm_Event
from context import Context
from camera_worker import camera_worker
from fsm_event import Fsm_Event
from cam_event  import Cam_Event
from threading import Thread



def logger(state, ctx: Context):
    print('Prechod do stavu: ' + str(state))
    ctx.state = state

def test_trans(state, ctx: Context):
    logger(state,ctx)


def cam_live(state, ctx: Context):
    logger(state,ctx)
    ctx.start_camera()
    

def cam_off(state, ctx: Context):
    logger(state,ctx)
    ctx.shutdown_camera()



transitions = {
    (State.OFF, Fsm_Event.PWR_BTN_LONG): (State.LIVE, cam_live), #misto (state, event): state jde udelat (state, event): (state, acition)
    (State.LIVE, Fsm_Event.MENU_BTN): (State.MENU, test_trans),
    ('ANY', Fsm_Event.PWR_BTN_LONG): (State.OFF, cam_off),
    (State.MENU, Fsm_Event.MENU_BTN): (State.LIVE, cam_live),
    (State.LIVE, Fsm_Event.REC_BTN): (State.CLIP, test_trans),
    (State.CLIP, Fsm_Event.REC_BTN): (State.LIVE, cam_live),
    (State.LIVE, Fsm_Event.PWR_BTN_LONG): (State.OFF, cam_off),
    (State.CLIP, Fsm_Event.PWR_BTN_LONG): (State.OFF, cam_off),
    (State.MENU, Fsm_Event.PWR_BTN_LONG): (State.OFF, cam_off),
    (State.MENU, None): (State.MENU_CROSS, test_trans),#vstup do menu/cross
    (State.MENU_CROSS, Fsm_Event.ENC_A_LEFT): (State.MENU_LANGUAGE, test_trans),#cross-language main
    (State.MENU_CROSS, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE, test_trans),#cross-view_mode main
    (State.MENU_CROSS, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, test_trans),#cross/color
    (State.MENU_CROSS_COLOR, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_Y, test_trans),#color-y
    (State.MENU_CROSS_Y, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_X, test_trans),#x-y
    (State.MENU_CROSS_COLOR, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE, test_trans),#color-type
    (State.MENU_CROSS_COLOR, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR_R, test_trans),#color/r
    (State.MENU_CROSS_COLOR_R, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, test_trans),#r-color vyber moznosti
    (State.MENU_CROSS_COLOR_R, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_G, test_trans), #r-g
    (State.MENU_CROSS_COLOR_R, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_B, test_trans), #r-b
    (State.MENU_CROSS_COLOR_G, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, test_trans),#g-color vyber moznosti
    (State.MENU_CROSS_COLOR_G, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_B, test_trans), #g-b
    (State.MENU_CROSS_COLOR_G, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_R, test_trans), #g-r
    (State.MENU_CROSS_COLOR_B, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, test_trans),#b-color vyber moznosti
    (State.MENU_CROSS_COLOR_B, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_R, test_trans), #b-r
    (State.MENU_CROSS_COLOR_B, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_G, test_trans), #b-g
    (State.MENU_CROSS_TYPE, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR, test_trans),#type-color
    (State.MENU_CROSS_X, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_Y, test_trans),#x-y
    (State.MENU_CROSS_TYPE, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_X, test_trans),#type-x
    (State.MENU_CROSS_X, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE, test_trans),#x-type
    (State.MENU_CROSS_TYPE, Fsm_Event.MENU_BTN): (State.MENU_CROSS, test_trans),#type-cross
    (State.MENU_CROSS_TYPE, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE_CROSS, test_trans),#type/cross
    (State.MENU_CROSS_TYPE_CROSS, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE, test_trans),#cross-type vyber moznosti
    (State.MENU_CROSS_TYPE_CROSS, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_DOT, test_trans), #cross-dot
    (State.MENU_CROSS_TYPE_CROSS, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_HALO, test_trans), #cross-halo
    (State.MENU_CROSS_TYPE_DOT, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE, test_trans),#dot-type vyber moznosti
    (State.MENU_CROSS_TYPE_DOT, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_HALO, test_trans), #dot-halo
    (State.MENU_CROSS_TYPE_DOT, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_CROSS, test_trans), #dot-cross
    (State.MENU_CROSS_TYPE_HALO, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_TYPE, test_trans),#dot-type vyber moznosti
    (State.MENU_CROSS_TYPE_HALO, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_CROSS, test_trans), #halo-cross
    (State.MENU_CROSS_TYPE_HALO, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_DOT, test_trans), #halo-dot
    (State.MENU_CROSS_COLOR, Fsm_Event.MENU_BTN): (State.MENU_CROSS, test_trans),#color-cross
    (State.MENU_CROSS_Y, Fsm_Event.MENU_BTN): (State.MENU_CROSS, test_trans),#y-cross
    (State.MENU_CROSS_Y, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_Y, test_trans),#y-y vyber moznosti
    (State.MENU_CROSS_Y, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR, test_trans),#y-color
    (State.MENU_CROSS_X, Fsm_Event.ENC_A_BTN): (State.MENU_CROSS_X, test_trans),#x-x vyber moznosti
    (State.MENU_CROSS_X, Fsm_Event.MENU_BTN): (State.MENU_CROSS, test_trans),#x-cross
    (State.MENU_VIEW_MODE, Fsm_Event.ENC_A_LEFT): (State.MENU_CROSS, test_trans),#view_mode-cross main
    (State.MENU_VIEW_MODE, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO, test_trans),#view_mode-video main
    (State.MENU_VIEW_MODE, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_DAY, test_trans),#view_mode/day
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.MENU_BTN): (State.MENU_VIEW_MODE, test_trans),#day-view_mode
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_DAY, test_trans),#day-day vyber moznosti
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_GRN_NIGHT, test_trans),#day-grn_night
    (State.MENU_VIEW_MODE_DAY, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_GREY_NIGHT, test_trans),#day-grey_night
    (State.MENU_VIEW_MODE_GRN_NIGHT, Fsm_Event.MENU_BTN): (State.MENU_VIEW_MODE, test_trans),#grn_night-view_mode
    (State.MENU_VIEW_MODE_GRN_NIGHT, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_GRN_NIGHT, test_trans),#grn_night - grn_night vyber moznosti
    (State.MENU_VIEW_MODE_GRN_NIGHT, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_GREY_NIGHT, test_trans),#grn_night-grey_night
    (State.MENU_VIEW_MODE_GRN_NIGHT, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_DAY, test_trans),#grn_night-day
    (State.MENU_VIEW_MODE_GREY_NIGHT, Fsm_Event.MENU_BTN): (State.MENU_VIEW_MODE, test_trans),#grey_night-view_mode
    (State.MENU_VIEW_MODE_GREY_NIGHT, Fsm_Event.ENC_A_BTN): (State.MENU_VIEW_MODE_GREY_NIGHT, test_trans),#grey_night - grey_night vyber moznosti
    (State.MENU_VIEW_MODE_GREY_NIGHT, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_DAY, test_trans),#grey_night-day
    (State.MENU_VIEW_MODE_GREY_NIGHT, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_GRN_NIGHT, test_trans),#grey_night-grn_night
    (State.MENU_VIDEO, Fsm_Event.ENC_A_RIGHT): (State.MENU_LANGUAGE, test_trans),#video-language main
    (State.MENU_VIDEO, Fsm_Event.ENC_A_LEFT): (State.MENU_VIEW_MODE, test_trans),#video-view_mode main
    (State.MENU_VIDEO, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_RES, test_trans),#video/res
    (State.MENU_VIDEO_RES, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_FPS, test_trans),#res-fps
    (State.MENU_VIDEO_RES, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_CLIP_AFTER, test_trans),#res-clip_after
    (State.MENU_VIDEO_RES, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_RES_720, test_trans),#res-720
    (State.MENU_VIDEO_RES_720, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_RES_720, test_trans),#720-720 vyber moznosti
    (State.MENU_VIDEO_RES_720, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_RES_1080, test_trans),#720-1080
    (State.MENU_VIDEO_RES_720, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_RES_1080, test_trans),#720-1080 
    (State.MENU_VIDEO_RES_720, Fsm_Event.MENU_BTN): (State.MENU_VIDEO_RES, test_trans),#720-res 
    (State.MENU_VIDEO_RES_1080, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_RES_1080, test_trans),#720-720 vyber moznosti
    (State.MENU_VIDEO_RES_1080, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_RES_720, test_trans),#720-1080
    (State.MENU_VIDEO_RES_1080, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_RES_720, test_trans),#720-1080 
    (State.MENU_VIDEO_RES_1080, Fsm_Event.MENU_BTN): (State.MENU_VIDEO_RES, test_trans),#1080-res 
    (State.MENU_VIDEO_FPS, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_CLIP_BEFORE, test_trans),#fps-clip
    (State.MENU_VIDEO_FPS, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_RES, test_trans),#fps-res
    (State.MENU_VIDEO_FPS, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_FPS_SET, test_trans),#fps-fps_set
    (State.MENU_VIDEO_FPS_SET, Fsm_Event.MENU_BTN): (State.MENU_VIDEO_FPS, test_trans),#fps_set-fps
    (State.MENU_VIDEO_CLIP_AFTER, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_RES, test_trans),#clip_after-res
    (State.MENU_VIDEO_CLIP_AFTER, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_CLIP_BEFORE, test_trans),#clip_after-clip_before
    (State.MENU_VIDEO_RES, Fsm_Event.MENU_BTN): (State.MENU_VIDEO, test_trans),#res-video
    (State.MENU_VIDEO_FPS, Fsm_Event.MENU_BTN): (State.MENU_VIDEO, test_trans),#fps-video
    (State.MENU_VIDEO_CLIP_AFTER, Fsm_Event.MENU_BTN): (State.MENU_VIDEO, test_trans),#clip-video
    (State.MENU_VIDEO_CLIP_AFTER, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_CLIP_AFTER_SET, test_trans), #clip_after-clip_after_set
    (State.MENU_VIDEO_CLIP_AFTER_SET, Fsm_Event.MENU_BTN): (State.MENU_VIDEO_CLIP_AFTER, test_trans), #clip_after-clip_after_set
    (State.MENU_VIDEO_CLIP_BEFORE, Fsm_Event.ENC_A_BTN): (State.MENU_VIDEO_CLIP_BEFORE_SET, test_trans), #clip_before-clip_before_set
    (State.MENU_VIDEO_CLIP_BEFORE_SET, Fsm_Event.MENU_BTN): (State.MENU_VIDEO_CLIP_BEFORE, test_trans), #clip_before_set-clip_before
    (State.MENU_VIDEO_CLIP_BEFORE, Fsm_Event.MENU_BTN): (State.MENU_VIDEO, test_trans), #clip_before-video
    (State.MENU_VIDEO_CLIP_BEFORE, Fsm_Event.ENC_A_RIGHT): (State.MENU_VIDEO_CLIP_AFTER, test_trans), #clip_before-clip_after
    (State.MENU_VIDEO_CLIP_BEFORE, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO_FPS, test_trans), #clip_before-fps
    (State.MENU_LANGUAGE, Fsm_Event.ENC_A_RIGHT): (State.MENU_CROSS, test_trans),#language-cross main
    (State.MENU_LANGUAGE, Fsm_Event.ENC_A_LEFT): (State.MENU_VIDEO, test_trans),#language-video main
    (State.MENU_LANGUAGE, Fsm_Event.ENC_A_BTN): (State.MENU_LANGUAGE_CZ, test_trans), #language/cz
    (State.MENU_LANGUAGE_CZ, Fsm_Event.ENC_A_BTN): (State.MENU_LANGUAGE_CZ, test_trans), #cz-cz
    (State.MENU_LANGUAGE_CZ, Fsm_Event.MENU_BTN): (State.MENU_LANGUAGE, test_trans), #cz-language
    (State.MENU_CROSS, Fsm_Event.MENU_BTN): (State.LIVE, cam_live), #cross-live
    (State.MENU_VIDEO, Fsm_Event.MENU_BTN): (State.LIVE, cam_live), #video-live
    (State.MENU_VIEW_MODE, Fsm_Event.MENU_BTN): (State.LIVE, cam_live), #view_mode-live
    (State.MENU_LANGUAGE, Fsm_Event.MENU_BTN): (State.LIVE, cam_live), #language-live
    
}