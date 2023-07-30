from threading import Timer
from tkinter import *
from tkinter import ttk
import random
from global_def import *
from videocanvas import *
from onvif_ipcam import *
import utils.net_utils
import utils.log_utils


log = utils.log_utils.logging_init(__file__)


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

        # Machine Network Interface Name
        self.network_interface_name = Network_Interface_Name
        self.ip = utils.net_utils.get_ip_address(self.network_interface_name)
        '''log.info("self.network_interface_name : %s", self.network_interface_name)
        log.info("self.ip : %s", self.ip)
        tmp_ip = self.ip.split(".")
        test_ip = tmp_ip[0] + "." + tmp_ip[1] + "." + tmp_ip[2] + "." + "55"
        log.debug("test_ip :%s", test_ip)'''

        self.label_ip_cam_ip = []

        self.discovery_label = tk.Label(self.big_frame, )
        self.discovery_frameCnt = 100  # need to check gif pic number
        self.discovery_frames = [PhotoImage(file='./material/discovery.gif',
                                            format='gif -index %i' % (i)) for i in range(self.discovery_frameCnt)]
        self.discovery_label.pack(fill="both", expand=True)
        self.discovery_label.after(100, self.show_discovery_image, 0)

        # self.list_discovery_ip_cam = []
        self.list_discovery_ip_cam = [-1 for i in range(256)]
        self.list_alive_ip_cam = []
        self.discovery_thread = []
        self.discovery_status = DiscoveryStatus.DISCOVERY_NOT_YET  # Discovery Status in global_def

        # start check discovery status after 3 secs
        self.check_discovery_status_timer = Timer(3, self.check_discovery_status)
        self.check_discovery_status_timer.start()
        # resp = cam_device.start_get_device_info()
        self.start_discovery_timer = Timer(2, self.start_discovery)  # start discovery after 2 secs
        self.start_discovery_timer.start()

        self.ip_cam_vid = []

    def start_ping_ipv4(self):
        log.debug("start_ping")

    def search_ip_cam_device(self, n):
        # ip = "192.168.0." + n
        tmp_ip = self.ip.split(".")
        ip = tmp_ip[0] + "." + tmp_ip[1] + "." + tmp_ip[2] + "." + n
        log.debug('in search_ipcam_device, ip= %s', ip)
        cam = OnVifIpCam(ip=ip, port="80")
        cam_device = cam.try_to_connect()

        if cam_device is not None:
            log.debug("[Info] found Ip_cam, ip: %s", ip)
            self.list_discovery_ip_cam[int(n)] = cam
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
        label_ip_cam_ip = tk.Label(self.big_frame, text="Alive IP Cam")
        label_ip_cam_ip.pack()

        # show ip in left
        for i in range(len(self.list_alive_ip_cam)):
            label_ip_cam_ip = tk.Label(self.big_frame, text=self.list_alive_ip_cam[i].ip)
            label_ip_cam_ip.pack()
            self.label_ip_cam_ip.append(label_ip_cam_ip)

        # max_row, max_column = self.get_max_row_and_column(len(self.list_alive_ip_cam))
        max_row, max_column = self.get_max_row_and_column()
        tmp_canvas_preview_width, tmp_canvas_preview_height = self.get_preview_canvas_width_height(max_row, max_column)
        log.debug("preview_width = %d, preview_height = %d\n", tmp_canvas_preview_width, tmp_canvas_preview_height )
        tmp_row = 0
        tmp_column = 0
        # start preview here??
        for n in range(len(self.list_alive_ip_cam)):
            self.list_alive_ip_cam[n].start_get_device_info()
            self.list_alive_ip_cam[n].get_media2_service()
            self.list_alive_ip_cam[n].get_cam_encoder_configuration()

            vid1 = VideoCanvas(self.right_frame, 0, self.list_alive_ip_cam[n].get_stream_uris()[1],
                               preview_width=tmp_canvas_preview_width, preview_height=tmp_canvas_preview_height,
                               _row=tmp_row, _column=tmp_column)
            tmp_column += 1
            if tmp_column >= max_column:
                tmp_row += 1
                tmp_column = 0
            self.ip_cam_vid.append(vid1)

        geo = str(default_window_width) + "x" + str(default_window_height)
        self.resize(geo)
        return True

    def get_preview_canvas_width_height(self, max_row, max_column):
        if max_row < 2:
            return default_image_width, default_image_height
        else:
            return int((default_window_width - 300)/max_column), int((default_window_height - 200)/max_row)

    def get_max_row_and_column(self):
        length = len(self.list_alive_ip_cam)
        if length <= 1:
            return 1, 1
        for i in range(8):
            if i * i >= length:
                return i, i

    def resize(self, geometry_str):
        self.root.geometry(geometry_str)

    def start(self):
        self.root.mainloop()

