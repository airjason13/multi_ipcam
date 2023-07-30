from enum import Enum

APP_NAME = "multi_ipcam"

# Machine Network Interface Name
Network_Interface_Name = "enp8s0"

# default window size
default_window_width = 1500
default_window_height = 800

# default ipcam preview size and label size
default_image_width = 640
default_image_height = 480

# max numbers of alive ip cam
Max_Numbers_of_Alive_Ip_Cam = 64
MAX_Factor_Number = 8 # 8*8 =64


# discovery status enum
class DiscoveryStatus(Enum):
    DISCOVERY_NOT_YET = 0
    DISCOVERY_START = 1
    DISCOVERY_END = 2
