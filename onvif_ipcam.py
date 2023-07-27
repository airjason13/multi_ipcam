from onvif import ONVIFCamera


class OnVifIpCam:
	def __init__(self, ip="", port="80", user='admin', passwd='admin', *args, **kwargs):
		self.ip = ip
		self.port = port
		self.user = user
		self.passwd = passwd
		self.cam_device = None
		self.cam_device_info = None
		self.media2_service = None
		self.cam_profiles = None
		self.cam_encoder_configuration = None
		self.stream_uri = []
	def try_to_connect(self):
		try:
			self.cam_device = ONVIFCamera(self.ip, self.port, self.user, self.passwd, "./wsdl")
		except Exception as e:
			print('[Error] ', e)
			return None
		return self.cam_device

	def start_get_device_info(self):
		resp = None
		try:
			resp = self.cam_device.devicemgmt.GetDeviceInformation()
			print(str(resp))
		except Exception as e:
			print('[Error]', e)
		self.cam_device_info = resp

		return resp

	def get_media2_service(self):
		media2_service = None
		try:
			if self.cam_device is None:
				self.try_to_connect()
			media2_service = self.cam_device.create_media_service()
		except Exception as e:
			print('[Error]', e)
		self.media2_service = media2_service
		print("[Info] self.media2_service :", self.media2_service)
		return media2_service

	def get_cam_profiles(self):
		cam_profiles = None
		try:
			if self.media2_service is None:
				self.get_media2_service()
			cam_profiles = self.media2_service.GetProfiles()
		except Exception as e:
			print('[Error]', e)
		self.cam_profiles = cam_profiles
		print("[Info] self.cam_profiles :", self.cam_profiles)
		return cam_profiles

	def get_cam_encoder_configuration(self):
		cam_encoder_configuration = None
		try:
			cam_encoder_configuration = self.media2_service.GetVideoEncoderConfigurations()
		except Exception as e:
			print('[Error]', e)
		self.cam_encoder_configuration = cam_encoder_configuration
		print("[Info] self.cam_encoder_configuration :", self.cam_encoder_configuration)
		return cam_encoder_configuration

	def get_stream_uris(self):
		uris = []
		if self.cam_profiles is None:
			self.get_cam_profiles()
		print("[Info] len(self.cam_profiles) : ", str(len(self.cam_profiles)))
		for i in range(len(self.cam_profiles)):
			token = self.cam_profiles[i].token
			cam_temp = self.media2_service.create_type('GetStreamUri')
			cam_temp.ProfileToken = token
			cam_temp.StreamSetup = {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}
			print("[Info] stream_uri :", self.media2_service.GetStreamUri(cam_temp))
			self.stream_uri.append(self.media2_service.GetStreamUri(cam_temp))

		for i in range(len(self.stream_uri)):
			print("[Info] rtsp stream uri : ", self.stream_uri[i]['Uri'])
			uris.append(self.stream_uri[i]['Uri'])
		return uris


if __name__ == '__main__':
	cam = OnVifIpCam("192.168.0.50", "80")
	cam.try_to_connect()
	cam.get_media2_service()
	cam.get_cam_encoder_configuration()
	cam.get_stream_uris()

