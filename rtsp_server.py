import os
import subprocess

import utils.log_utils
from global_def import *


class RtspServerProcess:
	def __init__(self, config_file=None, *args, **kwargs):
		self.i_pid = None
		self.config_file = config_file
		self.launch_cmd = None
		self.process = None

	def launch_server(self):
		log.debug("")
		self.terminate()

		# launch_cmd = "/bin/sh /home/venom/Downloads/test_rtsp_server.sh " + os.getcwd() + "/executable/ " + "2>&1"
		# os.popen(launch_cmd)
		# launch_cmd = "nohup /home/venom/Downloads/test_rtsp_server.sh"
		launch_cmd = ("nohup" + str_blank + os.getcwd() + "/executable/test_rtsp_server.sh" + str_blank
		              + os.getcwd() + "/executable/")
		log.debug("launch_cmd :%s", launch_cmd)
		self.process = subprocess.Popen(launch_cmd, shell=True)
		self.i_pid = int(self.process.pid)
		log.debug("self.pid : %d", self.i_pid)

	def get_pid(self):
		return self.i_pid

	def terminate(self):
		log.debug("terminate all mediamtx first!")
		p = os.popen("pkill mediamtx")
		p.close()
