# This is a Multi Ipcam.
#
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from tkinter import *
from tkinter import ttk
import random
from global_def import *
from videocanvas import *
from onvif_ipcam import *
from threading import Timer
import logging
import utils.log_utils
from mainwindow import MainWindow


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    log.info('Main')

    mw = MainWindow()
    mw.start()

    exit(0)


