from enum import Enum

# default ipcam preview size and label size
default_image_width = 640
default_image_height = 480


# discovery status enum
class DiscoveryStatus(Enum):
    DISCOVERY_NOT_YET = 0
    DISCOVERY_START = 1
    DISCOVERY_END = 2
