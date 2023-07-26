from onvif import ONVIFCamera


class OnVifIpCam:
	def __init__(self, ip="", port="80", user='admin', passwd='admin', *args, **kwargs):
		self.ip = ip
		self.port = port
		self.user = user
		self.passwd = passwd
		self.cam_device = None

	def try_to_connect(self):
		try:
			self.cam_device = ONVIFCamera(self.ip, self.port, self.user, self.port, "./wsdl")
		except Exception as e:
			print('[Error] ', e)
		return self.cam_device

	def start_get_device_info(self):
		resp = None
		try:
			resp = self.cam_device.devicemgmt.GetDeviceInformation()
			print(str(resp))
		except Exception as e:
			print('[Error] ', e)

		return resp