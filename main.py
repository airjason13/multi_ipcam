# This is a Multi Ipcam.
#
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# import tkinter as tk
from tkinter import *
from tkinter import ttk
import random
from global_def import *
from videocanvas import *
from onvif_ipcam import *
from threading import Timer


class MainWindow(object):
    def __init__(self):
        self.root = tk.Tk()
        # self.root.config(bg="black")
        self.root.geometry("640x480")
        self.root.tk.call("source", "azure.tcl")
        self.root.tk.call("set_theme", "dark")
        self.root.title("Infoboom Multi IpCam")
        # self.big_frame = ttk.Frame(self.root)
        # self.big_frame.pack(fill="both", expand=True)
        self.big_frame = ttk.Frame(self.root)
        self.right_frame = ttk.Frame(self.root)
        self.big_frame.pack(side="left", expand=True)
        self.right_frame.pack(side="right", expand=True)

        self.label_ip_cam_ip = []

        self.discovery_label = tk.Label(self.big_frame,)
        self.discovery_frameCnt = 100 # need to check gif pic number
        self.discovery_frames = [PhotoImage(file='./material/discovery.gif',
                                            format='gif -index %i' % (i)) for i in range(self.discovery_frameCnt)]
        self.discovery_label.pack(fill="both", expand=True)
        self.discovery_label.after(100, self.show_discovery_image, 0)

        # self.list_discovery_ip_cam = []
        self.list_discovery_ip_cam = [-1 for i in range(256)]
        self.list_alive_ip_cam = []
        self.discovery_thread = []
        self.discovery_status = DiscoveryStatus.DISCOVERY_NOT_YET # Discovery Status in global_def

        # start check discovery status after 3 secs
        self.check_discovery_status_timer = Timer(3, self.check_discovery_status)
        self.check_discovery_status_timer.start()
        # resp = cam_device.start_get_device_info()
        self.start_discovery_timer = Timer(1, self.start_discovery) # start discovery after 2 secs
        self.start_discovery_timer.start()

        self.ip_cam_vid = []
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
        # print("[Info] cam_device:", cam_device)
        if cam_device is not None:
            print("[Info] found Ip_cam, ip:", ip)
            self.list_discovery_ip_cam[int(n)] = cam
        else:
            self.list_discovery_ip_cam[int(n)] = None

    def start_discovery(self):
        self.discovery_status = DiscoveryStatus.DISCOVERY_START
        for i in range(256):
            t = threading.Thread(target=self.search_ip_cam_device, args=(str(i),))
            t.start()

    def show_discovery_image(self, ind):
        frame = self.discovery_frames[ind]
        ind += 1
        if ind == self.discovery_frameCnt:
            ind = 0
        self.discovery_label.configure(image=frame)
        if self.discovery_status != DiscoveryStatus.DISCOVERY_END:
            # update discover label again with new pic index
            self.discovery_label.after(100, self.show_discovery_image, ind)

    def check_discovery_status(self):
        for i in range(256):
            if self.list_discovery_ip_cam[i] == -1:
                self.check_discovery_status_timer = Timer(3, self.check_discovery_status)
                self.check_discovery_status_timer.start()
                print("[Info] check discovery status return False")
                return False
        print("[Info] check discovery status True")
        for i in range(len(self.list_discovery_ip_cam)):
            try:
                if self.list_discovery_ip_cam[i] is not None:
                    self.list_alive_ip_cam.append(self.list_discovery_ip_cam[i])
            except Exception as e:
                pass
        print('[Info] Final Alive Ipcam device length : ', str(len(self.list_alive_ip_cam)))
        self.discovery_status = DiscoveryStatus.DISCOVERY_END
        self.discovery_label.destroy()
        #show ip in left
        for i in range(len(self.list_alive_ip_cam)):
            label_ip_cam_ip = tk.Label(self.big_frame, text=self.list_alive_ip_cam[i].ip)
            label_ip_cam_ip.pack()
            self.label_ip_cam_ip.append(label_ip_cam_ip)
        # start preview here??
        for n in range(len(self.list_alive_ip_cam)):
            self.list_alive_ip_cam[n].start_get_device_info()
            self.list_alive_ip_cam[n].get_media2_service()
            self.list_alive_ip_cam[n].get_cam_encoder_configuration()
            
            vid1 = VideoCanvas(self.right_frame, 0, self.list_alive_ip_cam[n].get_stream_uris()[1], _row=0, _column=0)
            self.ip_cam_vid.append(vid1)
        return True

    def resize(self, geometry_str):
        self.root.geometry(geometry_str)

    def start(self):
        self.root.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mw = MainWindow()
    mw.start()


