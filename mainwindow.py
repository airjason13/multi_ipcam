import os
from threading import Timer
from tkinter import *
from tkinter import ttk
import random
from global_def import *
from videocanvas import *
from videocanvas_ffmpeg import *
from onvif_ipcam import *
import utils.net_utils
import utils.log_utils
import utils.ffmpeg_utils
from rtsp_server import *


class MainWindow(object):
    def __init__(self):
        self.root = tk.Tk()

        # window resize and move callback
        self.root.bind("<Configure>", self.on_window_resize)

        self.root.config(bg="black")
        self.root.geometry("500x282")
        self.root.tk.call("source", "azure.tcl")
        self.root.tk.call("set_theme", "dark")
        self.root.title("Infoboom Multi IpCam")

        # Kill ffmpeg process first
        utils.ffmpeg_utils.kill_all_ffmpeg_process()

        self.big_frame = ttk.Frame(self.root)
        self.right_frame = ttk.Frame(self.root)
        self.big_frame.pack(side="left", expand=True)
        self.right_frame.pack(side="right", expand=True)
        self.right_frame.config(width=1280, height=720)

        # Rtsp Server
        self.rtsp_server = RtspServerProcess()
        self.rtsp_server.terminate()
        self.rtsp_server.launch_server()
        log.debug("self.rtsp_server.i_pid : %d", self.rtsp_server.i_pid)

        # Machine Network Interface Name
        self.network_interface_name = Network_Interface_Name
        self.ip = utils.net_utils.get_ip_address(self.network_interface_name)

        self.label_ip_cam_ip = []

        self.discovery_label = tk.Label(self.big_frame, )
        self.discovery_frameCnt = 100  # need to check gif pic number
        self.discovery_frames = [PhotoImage(file='./material/discovery.gif',
                                            format='gif -index %i' % (i)) for i in range(self.discovery_frameCnt)]
        self.discovery_label.pack(fill="both", expand=True)
        self.discovery_label.after(100, self.show_discovery_image, 0)

        self.list_ping_ipv4 = [-1 for i in range(256)]
        # self.ping_ipv4_thread = []
        self.start_ping_ipv4_timer = Timer(1, self.start_ping_ipv4)  # start discovery after 2 secs
        self.start_ping_ipv4_timer.start()
        self.check_ping_status_timer = Timer(3, self.check_ping_status)
        self.check_ping_status_timer.start()

        # self.list_discovery_ip_cam = []
        self.list_discovery_ip_cam = [-1 for i in range(256)]
        self.list_alive_ip_cam = []
        # self.discovery_thread = []
        self.discovery_status = DiscoveryStatus.DISCOVERY_NOT_YET  # Discovery Status in global_def

        self.check_discovery_status_timer = None
        self.start_discovery_timer = None

        self.ip_cam_vid = []

    def check_ping_status(self):
        for i in range(256):
            if self.list_ping_ipv4[i] == -1:
                self.check_ping_status_timer = Timer(3, self.check_ping_status)
                self.check_ping_status_timer.start()
                print("[Info] check discovery status return False")
                return False
        log.debug("Ping Ipv4 finished, return True")

        for i in range(len(self.list_ping_ipv4)):
            if "Not Exists" in self.list_ping_ipv4[i]:
                pass
            else:
                log.debug("self.list_ping_ipv4[%d] : %s", i, self.list_ping_ipv4[i])
        self.check_discovery_status_timer = Timer(3, self.check_discovery_status)
        self.check_discovery_status_timer.start()

        self.start_discovery_timer = Timer(2, self.start_discovery)  # start discovery after 2 secs
        self.start_discovery_timer.start()
        return True

    def ping_ipv4(self, n):
        tmp_ip = self.ip.split(".")
        ip = tmp_ip[0] + "." + tmp_ip[1] + "." + tmp_ip[2] + "." + n

        process = os.popen("nc -vz -w 1 " + ip + " " + "554 2>&1")
        ret = process.read()
        process.close()
        # log.debug("ping ipv4 %s, ret :%s", ip, ret)
        if "succeeded" in ret:  # ip exist and could ping
            self.list_ping_ipv4[int(n)] = ip
            log.debug("ping ipv4 %s, ret :%s", ip, ret)
        else:
            self.list_ping_ipv4[int(n)] = "IP Not Exists"

    def start_ping_ipv4(self):
        log.debug("start_ping")
        for i in range(256):
            t = threading.Thread(target=self.ping_ipv4, args=(str(i),))
            t.start()

    def search_ip_cam_device(self, n):
        if "Not Exists" in self.list_ping_ipv4[int(n)]:
            self.list_discovery_ip_cam[int(n)] = None
            return
        # ip = "192.168.0." + n
        tmp_ip = self.ip.split(".")
        ip = tmp_ip[0] + "." + tmp_ip[1] + "." + tmp_ip[2] + "." + n

        # log.debug('in search_ipcam_device, ip= %s', ip)
        tmp_cam = OnVifIpCam(ip=ip, port="80")
        cam_device = tmp_cam.try_to_connect()

        if cam_device is not None:
            log.debug("[Info] found Ip_cam, ip: %s", ip)
            self.list_discovery_ip_cam[int(n)] = tmp_cam
        else:
            self.list_discovery_ip_cam[int(n)] = None

    def start_discovery(self):
        log.debug("start_discovery timer launch")
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
        log.debug("[Info] check discovery status True")
        for i in range(len(self.list_discovery_ip_cam)):
            try:
                if self.list_discovery_ip_cam[i] is not None:
                    self.list_alive_ip_cam.append(self.list_discovery_ip_cam[i])
            except Exception as e:
                pass

        log.debug('[Info] Final Alive Ipcam device length : %s', str(len(self.list_alive_ip_cam)))
        self.discovery_status = DiscoveryStatus.DISCOVERY_END
        self.discovery_label.destroy()

        # ipcam ip label
        label_ip_cam_ip = tk.Label(self.big_frame, text="Alive IP Cam:")
        label_ip_cam_ip.pack()
        # show ip in left frame
        for i in range(len(self.list_alive_ip_cam)):
            label_ip_cam_ip = tk.Label(self.big_frame, text=self.list_alive_ip_cam[i].ip)
            label_ip_cam_ip.pack()
            self.label_ip_cam_ip.append(label_ip_cam_ip)

        # show ip in left frame
        self.adjust_preview_frame()

        # test ffmpeg parse stream
        utils.ffmpeg_utils.rtsp_parser_streaming()
        '''preview_frame_pos_x = self.root.winfo_x() + self.right_frame.winfo_x()
        preview_frame_pos_y = self.root.winfo_y() + self.right_frame.winfo_y()
        utils.ffmpeg_utils.x11grab_stream(self.right_frame.winfo_width(), self.right_frame.winfo_height(),
                                          src_x=preview_frame_pos_x, src_y=preview_frame_pos_y)'''

        # test forwarding directly
        src_list = []
        for i in range(len(self.list_alive_ip_cam)):
            src_list.append(self.list_alive_ip_cam[i].get_stream_uris()[1])

        log.debug("%s", src_list)
        utils.ffmpeg_utils.forward_rtsp_src_to_parser(src_list)
        return True

    def adjust_preview_frame(self):
        # need to adjust mainwindow geo first
        geo = str(default_window_width) + "x" + str(default_window_height)
        self.resize(geo)

        self.right_frame.config(width=1280, height=720)

        log.debug("self.right_frame.winfo_width() = %d", self.right_frame.winfo_width())

        # calculate preview canvas size
        max_row, max_column = self.get_max_row_and_column()
        tmp_canvas_preview_width, tmp_canvas_preview_height = self.get_preview_canvas_width_height(max_row, max_column)
        log.debug("preview_width = %d, preview_height = %d\n", tmp_canvas_preview_width, tmp_canvas_preview_height)
        tmp_row = 0
        tmp_column = 0
        # start preview here??
        for n in range(len(self.list_alive_ip_cam)):
            self.list_alive_ip_cam[n].start_get_device_info()
            self.list_alive_ip_cam[n].get_media2_service()
            self.list_alive_ip_cam[n].get_cam_encoder_configuration()

            vid1 = VideoCanvasFFMpeg(self.right_frame, 0, self.list_alive_ip_cam[n].get_stream_uris()[1],
                               preview_width=tmp_canvas_preview_width, preview_height=tmp_canvas_preview_height,
                               _row=tmp_row, _column=tmp_column)
            '''vid1 = VideoCanvas(self.right_frame, 0, self.list_alive_ip_cam[n].get_stream_uris()[1],
                                     preview_width=tmp_canvas_preview_width, preview_height=tmp_canvas_preview_height,
                                     _row=tmp_row, _column=tmp_column)'''

            tmp_column += 1
            if tmp_column >= max_column:
                tmp_row += 1
                tmp_column = 0
            self.ip_cam_vid.append(vid1)

    def get_preview_canvas_width_height(self, max_row, max_column):
        right_frame_width = self.right_frame.winfo_width()
        right_frame_height = self.right_frame.winfo_height()
        log.debug("right_frame_width :%d, right_frame_height:%d", right_frame_width, right_frame_height)
        if max_row < 2:
            return default_image_width, default_image_height
        else:
            # This needs to be implemented
            return int(right_frame_width / max_column), int(right_frame_height / max_row)

    def get_max_row_and_column(self):
        length = len(self.list_alive_ip_cam)
        if length <= 1:
            return 1, 1
        for i in range(8):
            if i * i >= length:
                return i, i

    def resize(self, geometry_str):
        self.root.geometry(geometry_str)
        width = geometry_str.split("x")[0]
        while True:
            # log.debug("%d ,%d", int(self.root.winfo_width()), int(width))
            if str(self.root.winfo_width()) == width:
                break

    def on_window_resize(self, event):
        width = event.width
        height = event.height
        # log.debug("self.right_frame.winfo_width() = %d", self.right_frame.winfo_width())
        # log.debug("window position : %d, %d", self.root.winfo_x(), self.root.winfo_y())
        # log.debug("window size :%dx%d", width, height)

    def start(self):
        self.root.mainloop()

