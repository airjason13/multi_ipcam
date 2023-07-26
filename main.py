# This is a Multi Ipcam.
#
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import tkinter as tk
import random
from global_def import *
from videocanvas import *
from onvif_ipcam import *

class MainWindow(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Infoboom Multi Ipcam")
        self.list_ip_cam = []
        for i in range(256):
            test_thread = threading.Thread(target=self.search_ip_cam_device, args=(str(i),))
            test_thread.start()
        # resp = cam_device.start_get_device_info()

        '''
        # self.vid1 = VideoCanvas(self.root, "/home/venom/Videos/DASS-190.mp4")
        self.vid1 = VideoCanvas(self.root, 0, "rtsp://192.168.0.12/v01", _row=0, _column=0)

        self.vid2 = VideoCanvas(self.root, 1, "rtsp://192.168.0.13/v01", _row=0, _column=1)

        self.vid3 = VideoCanvas(self.root, 2, "rtsp://192.168.0.14/v01", _row=1, _column=0)
        '''

    def search_ip_cam_device(self, n):
        ip = "192.168.0." + n
        print('[Info] in search_ipca_device, ip=', ip)
        cam = OnVifIpCam(ip=ip, port="80")
        cam_device = cam.try_to_connect()
        print("[Info] cam_device:", cam_device)
        if cam_device is not None:
            self.list_ip_cam.append(cam_device)

    def resize(self, geometry_str):
        self.root.geometry(geometry_str)

    def start(self):
        self.root.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mw = MainWindow()
    mw.start()


