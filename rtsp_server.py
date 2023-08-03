import os

import utils.log_utils
from global_def import *


class RtspServerProcess:
	def __init__(self, config_file=None, *args, **kwargs):
		self.i_pid = None
		self.config_file = config_file
		self.launch_cmd = None

	def launch_server(self):
		log.debug("")
		launch_cmd = "/bin/sh /home/venom/Downloads/test_rtsp_server.sh " + os.getcwd() + "/executable/ " + "2>&1 &"
		os.popen(launch_cmd)

		self.i_pid = int(os.popen("pgrep mediamtx").read())
		log.debug("self.pid : %d", self.i_pid)

	def get_pid(self):
		return self.i_pid

	def terminate(self):
		if self.i_pid is None:
			log.debug("rtsp server pid is None")
		else:
			os.kill(self.i_pid, -9)
			
		if os.popen("pgrep mediamtx").read() is not None:
			log.debug(" process mediamtx : %s", os.popen("pgrep mediamtx").read())
			os.popen("pkill mediamtx")