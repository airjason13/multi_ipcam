# This is a Multi Ipcam.
#
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import time
from tkinter import *
from tkinter import ttk
import random
from global_def import *
from videocanvas import *
from onvif_ipcam import *
from threading import Timer
import os
import utils.log_utils
import utils.ffmpeg_utils
from mainwindow import MainWindow


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    log.info('Main')
    '''
    utils.ffmpeg_utils.rtsp_parser_streaming()
    '''
    '''
    src_list = ['/home/venom/Downloads/435MFC-253.mp4',
                '/home/venom/Downloads/435MFC-253.mp4',
                '/home/venom/Downloads/435MFC-253.mp4',
                '/home/venom/Downloads/435MFC-253.mp4',
                ]
    '''
    '''
    src_list = ['rtsp://192.168.0.15/v02',
                'rtsp://192.168.0.16/v02',
                'rtsp://192.168.0.17/v02',
                ]
    utils.ffmpeg_utils.forward_rtsp_src_to_parser(src_list)
    while True:
        log.debug("a")
        time.sleep(100)
        pass
    '''
    mw = MainWindow()
    mw.start()

    exit(0)


