from state import State
from event import Event

def test_trans(state):
    print('Prechod do stavu: ' + str(state))

transitions = {
    (State.OFF, Event.PWR_BTN_LONG): (State.LIVE, test_trans), #misto (state, event): state jde udelat (state, event): (state, acition)
    (State.LIVE, Event.MENU_BTN): (State.MENU, test_trans),
    (State.MENU, Event.MENU_BTN): (State.LIVE, test_trans),
    (State.LIVE, Event.REC_BTN): (State.CLIP, test_trans),
    (State.CLIP, Event.REC_BTN): (State.LIVE, test_trans),
    (State.LIVE, Event.PWR_BTN_LONG): (State.OFF, test_trans),
    (State.CLIP, Event.PWR_BTN_LONG): (State.OFF, test_trans),
    (State.MENU, Event.PWR_BTN_LONG): (State.OFF, test_trans),
    (State.MENU, None): (State.MENU_CROSS, test_trans),#vstup do menu/cross
    (State.MENU_CROSS, Event.ENC_A_LEFT): (State.MENU_LANGUAGE, test_trans),#cross-language main
    (State.MENU_CROSS, Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE, test_trans),#cross-view_mode main
    (State.MENU_CROSS, Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, test_trans),#cross/color
    (State.MENU_CROSS_COLOR, Event.ENC_A_LEFT): (State.MENU_CROSS_Y, test_trans),#color-y
    (State.MENU_CROSS_Y, Event.ENC_A_LEFT): (State.MENU_CROSS_X, test_trans),#x-y
    (State.MENU_CROSS_COLOR, Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE, test_trans),#color-type
    (State.MENU_CROSS_COLOR, Event.ENC_A_BTN): (State.MENU_CROSS_COLOR_R, test_trans),#color/r
    (State.MENU_CROSS_COLOR_R, Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, test_trans),#r-color vyber moznosti
    (State.MENU_CROSS_COLOR_R, Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_G, test_trans), #r-g
    (State.MENU_CROSS_COLOR_R, Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_B, test_trans), #r-b
    (State.MENU_CROSS_COLOR_G, Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, test_trans),#g-color vyber moznosti
    (State.MENU_CROSS_COLOR_G, Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_B, test_trans), #g-b
    (State.MENU_CROSS_COLOR_G, Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_R, test_trans), #g-r
    (State.MENU_CROSS_COLOR_B, Event.ENC_A_BTN): (State.MENU_CROSS_COLOR, test_trans),#b-color vyber moznosti
    (State.MENU_CROSS_COLOR_B, Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR_R, test_trans), #b-r
    (State.MENU_CROSS_COLOR_B, Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR_G, test_trans), #b-g
    (State.MENU_CROSS_TYPE, Event.ENC_A_LEFT): (State.MENU_CROSS_COLOR, test_trans),#type-color
    (State.MENU_CROSS_X, Event.ENC_A_RIGHT): (State.MENU_CROSS_Y, test_trans),#x-y
    (State.MENU_CROSS_TYPE, Event.ENC_A_RIGHT): (State.MENU_CROSS_X, test_trans),#type-x
    (State.MENU_CROSS_X, Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE, test_trans),#x-type
    (State.MENU_CROSS_TYPE, Event.MENU_BTN): (State.MENU_CROSS, test_trans),#type-cross
    (State.MENU_CROSS_TYPE, Event.ENC_A_BTN): (State.MENU_CROSS_TYPE_CROSS, test_trans),#type/cross
    (State.MENU_CROSS_TYPE_CROSS, Event.ENC_A_BTN): (State.MENU_CROSS_TYPE, test_trans),#cross-type vyber moznosti
    (State.MENU_CROSS_TYPE_CROSS, Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_DOT, test_trans), #cross-dot
    (State.MENU_CROSS_TYPE_CROSS, Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_HALO, test_trans), #cross-halo
    (State.MENU_CROSS_TYPE_DOT, Event.ENC_A_BTN): (State.MENU_CROSS_TYPE, test_trans),#dot-type vyber moznosti
    (State.MENU_CROSS_TYPE_DOT, Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_HALO, test_trans), #dot-halo
    (State.MENU_CROSS_TYPE_DOT, Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_CROSS, test_trans), #dot-cross
    (State.MENU_CROSS_TYPE_HALO, Event.ENC_A_BTN): (State.MENU_CROSS_TYPE, test_trans),#dot-type vyber moznosti
    (State.MENU_CROSS_TYPE_HALO, Event.ENC_A_RIGHT): (State.MENU_CROSS_TYPE_CROSS, test_trans), #halo-cross
    (State.MENU_CROSS_TYPE_HALO, Event.ENC_A_LEFT): (State.MENU_CROSS_TYPE_DOT, test_trans), #halo-dot
    (State.MENU_CROSS_COLOR, Event.MENU_BTN): (State.MENU_CROSS, test_trans),#color-cross
    (State.MENU_CROSS_Y, Event.MENU_BTN): (State.MENU_CROSS, test_trans),#y-cross
    (State.MENU_CROSS_Y, Event.ENC_A_BTN): (State.MENU_CROSS_Y, test_trans),#y-y vyber moznosti
    (State.MENU_CROSS_Y, Event.ENC_A_RIGHT): (State.MENU_CROSS_COLOR, test_trans),#y-color
    (State.MENU_CROSS_X, Event.ENC_A_BTN): (State.MENU_CROSS_X, test_trans),#x-x vyber moznosti
    (State.MENU_CROSS_X, Event.MENU_BTN): (State.MENU_CROSS, test_trans),#x-cross
    (State.MENU_VIEW_MODE, Event.ENC_A_LEFT): (State.MENU_CROSS, test_trans),#view_mode-cross main
    (State.MENU_VIEW_MODE, Event.ENC_A_RIGHT): (State.MENU_VIDEO, test_trans),#view_mode-video main
    (State.MENU_VIEW_MODE, Event.ENC_A_BTN): (State.MENU_VIEW_MODE_DAY, test_trans),#view_mode/day
    (State.MENU_VIEW_MODE_DAY, Event.MENU_BTN): (State.MENU_VIEW_MODE, test_trans),#day-view_mode
    (State.MENU_VIEW_MODE_DAY, Event.ENC_A_BTN): (State.MENU_VIEW_MODE_DAY, test_trans),#day-day vyber moznosti
    (State.MENU_VIEW_MODE_DAY, Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_GRN_NIGHT, test_trans),#day-grn_night
    (State.MENU_VIEW_MODE_DAY, Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_GREY_NIGHT, test_trans),#day-grey_night
    (State.MENU_VIEW_MODE_GRN_NIGHT, Event.MENU_BTN): (State.MENU_VIEW_MODE, test_trans),#grn_night-view_mode
    (State.MENU_VIEW_MODE_GRN_NIGHT, Event.ENC_A_BTN): (State.MENU_VIEW_MODE_GRN_NIGHT, test_trans),#grn_night - grn_night vyber moznosti
    (State.MENU_VIEW_MODE_GRN_NIGHT, Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_GREY_NIGHT, test_trans),#grn_night-grey_night
    (State.MENU_VIEW_MODE_GRN_NIGHT, Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_DAY, test_trans),#grn_night-day
    (State.MENU_VIEW_MODE_GREY_NIGHT, Event.MENU_BTN): (State.MENU_VIEW_MODE, test_trans),#grey_night-view_mode
    (State.MENU_VIEW_MODE_GREY_NIGHT, Event.ENC_A_BTN): (State.MENU_VIEW_MODE_GREY_NIGHT, test_trans),#grey_night - grey_night vyber moznosti
    (State.MENU_VIEW_MODE_GREY_NIGHT, Event.ENC_A_RIGHT): (State.MENU_VIEW_MODE_DAY, test_trans),#grey_night-day
    (State.MENU_VIEW_MODE_GREY_NIGHT, Event.ENC_A_LEFT): (State.MENU_VIEW_MODE_GRN_NIGHT, test_trans),#grey_night-grn_night
    (State.MENU_VIDEO, Event.ENC_A_RIGHT): (State.MENU_LANGUAGE, test_trans),#video-language main
    (State.MENU_VIDEO, Event.ENC_A_LEFT): (State.MENU_VIEW_MODE, test_trans),#video-view_mode main
    (State.MENU_VIDEO, Event.ENC_A_BTN): (State.MENU_VIDEO_RES, test_trans),#video/res
    (State.MENU_VIDEO_RES, Event.ENC_A_RIGHT): (State.MENU_VIDEO_FPS, test_trans),#res-fps
    (State.MENU_VIDEO_RES, Event.ENC_A_LEFT): (State.MENU_VIDEO_CLIP_AFTER, test_trans),#res-clip_after
    (State.MENU_VIDEO_RES, Event.ENC_A_BTN): (State.MENU_VIDEO_RES_720, test_trans),#res-720
    (State.MENU_VIDEO_RES_720, Event.ENC_A_BTN): (State.MENU_VIDEO_RES_720, test_trans),#720-720 vyber moznosti
    (State.MENU_VIDEO_RES_720, Event.ENC_A_RIGHT): (State.MENU_VIDEO_RES_1080, test_trans),#720-1080
    (State.MENU_VIDEO_RES_720, Event.ENC_A_LEFT): (State.MENU_VIDEO_RES_1080, test_trans),#720-1080 
    (State.MENU_VIDEO_RES_720, Event.MENU_BTN): (State.MENU_VIDEO_RES, test_trans),#720-res 
    (State.MENU_VIDEO_RES_1080, Event.ENC_A_BTN): (State.MENU_VIDEO_RES_1080, test_trans),#720-720 vyber moznosti
    (State.MENU_VIDEO_RES_1080, Event.ENC_A_RIGHT): (State.MENU_VIDEO_RES_720, test_trans),#720-1080
    (State.MENU_VIDEO_RES_1080, Event.ENC_A_LEFT): (State.MENU_VIDEO_RES_720, test_trans),#720-1080 
    (State.MENU_VIDEO_RES_1080, Event.MENU_BTN): (State.MENU_VIDEO_RES, test_trans),#1080-res 
    (State.MENU_VIDEO_FPS, Event.ENC_A_RIGHT): (State.MENU_VIDEO_CLIP_BEFORE, test_trans),#fps-clip
    (State.MENU_VIDEO_FPS, Event.ENC_A_LEFT): (State.MENU_VIDEO_RES, test_trans),#fps-res
    (State.MENU_VIDEO_FPS, Event.ENC_A_BTN): (State.MENU_VIDEO_FPS_SET, test_trans),#fps-fps_set
    (State.MENU_VIDEO_FPS_SET, Event.MENU_BTN): (State.MENU_VIDEO_FPS, test_trans),#fps_set-fps
    (State.MENU_VIDEO_CLIP_AFTER, Event.ENC_A_RIGHT): (State.MENU_VIDEO_RES, test_trans),#clip_after-res
    (State.MENU_VIDEO_CLIP_AFTER, Event.ENC_A_LEFT): (State.MENU_VIDEO_CLIP_BEFORE, test_trans),#clip_after-clip_before
    (State.MENU_VIDEO_RES, Event.MENU_BTN): (State.MENU_VIDEO, test_trans),#res-video
    (State.MENU_VIDEO_FPS, Event.MENU_BTN): (State.MENU_VIDEO, test_trans),#fps-video
    (State.MENU_VIDEO_CLIP_AFTER, Event.MENU_BTN): (State.MENU_VIDEO, test_trans),#clip-video
    (State.MENU_VIDEO_CLIP_AFTER, Event.ENC_A_BTN): (State.MENU_VIDEO_CLIP_AFTER_SET, test_trans), #clip_after-clip_after_set
    (State.MENU_VIDEO_CLIP_AFTER_SET, Event.MENU_BTN): (State.MENU_VIDEO_CLIP_AFTER, test_trans), #clip_after-clip_after_set
    (State.MENU_VIDEO_CLIP_BEFORE, Event.ENC_A_BTN): (State.MENU_VIDEO_CLIP_BEFORE_SET, test_trans), #clip_before-clip_before_set
    (State.MENU_VIDEO_CLIP_BEFORE_SET, Event.MENU_BTN): (State.MENU_VIDEO_CLIP_BEFORE, test_trans), #clip_before_set-clip_before
    (State.MENU_VIDEO_CLIP_BEFORE, Event.MENU_BTN): (State.MENU_VIDEO, test_trans), #clip_before-video
    (State.MENU_VIDEO_CLIP_BEFORE, Event.ENC_A_RIGHT): (State.MENU_VIDEO_CLIP_AFTER, test_trans), #clip_before-clip_after
    (State.MENU_VIDEO_CLIP_BEFORE, Event.ENC_A_LEFT): (State.MENU_VIDEO_FPS, test_trans), #clip_before-fps
    (State.MENU_LANGUAGE, Event.ENC_A_RIGHT): (State.MENU_CROSS, test_trans),#language-cross main
    (State.MENU_LANGUAGE, Event.ENC_A_LEFT): (State.MENU_VIDEO, test_trans),#language-video main
    (State.MENU_LANGUAGE, Event.ENC_A_BTN): (State.MENU_LANGUAGE_CZ, test_trans), #language/cz
    (State.MENU_LANGUAGE_CZ, Event.ENC_A_BTN): (State.MENU_LANGUAGE_CZ, test_trans), #cz-cz
    (State.MENU_LANGUAGE_CZ, Event.MENU_BTN): (State.MENU_LANGUAGE, test_trans), #cz-language
    (State.MENU_CROSS, Event.MENU_BTN): (State.LIVE, test_trans), #cross-live
    (State.MENU_VIDEO, Event.MENU_BTN): (State.LIVE, test_trans), #video-live
    (State.MENU_VIEW_MODE, Event.MENU_BTN): (State.LIVE, test_trans), #view_mode-live
    (State.MENU_LANGUAGE, Event.MENU_BTN): (State.LIVE, test_trans), #language-live
    
}