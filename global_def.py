import os
from enum import Enum
import utils.log_utils
import utils.net_utils

APP_NAME = "multi_ipcam"

log = utils.log_utils.logging_init(__file__)

str_blank = " "

NONE_IPCAM_PREVIEW_SRC = os.getcwd() + "/material/error_animation.mp4"

# Machine Network Interface Name
Network_Interface_Name = "eno1"

# default window size
default_window_width = 1500
default_window_height = 800


# default ipcam preview size and label size
default_image_width = 640
default_image_height = 480

# max numbers of alive ip cam
Max_Numbers_of_Alive_Ip_Cam = 64
MAX_Factor_Number = 8 # 8*8 =64


# ping_ipv4 status enum
class PingIpv4Status(Enum):
    PING_NOT_YET = 0
    PING_START = 1
    PING_END = 2


# discovery status enum
class DiscoveryStatus(Enum):
    DISCOVERY_NOT_YET = 0
    DISCOVERY_START = 1
    DISCOVERY_END = 2


# Used for ffmpeg streaming
Parser_Src_Ip = "localhost"
Parser_Dst_Ip = utils.net_utils.get_ip_address(Network_Interface_Name)
Parser_Src_Port = "8989"
Parser_Dst_Port = "8554"

Real_Stream_Dst_Ip = Parser_Src_Ip

Streaming_Video_Width = 1280
Streaming_Video_Height = 720

Default_Rtsp_Stream_Name = "av01"

Default_Encode_Factor = "h264"
Default_Video_BitRate = "2000k"


FFMPEG_BIN = "ffmpeg"

