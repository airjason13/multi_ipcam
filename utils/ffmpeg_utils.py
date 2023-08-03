from global_def import *
import subprocess


def rtsp_parser_streaming(src_ip=Parser_Src_Ip, src_port=Parser_Src_Port,
                          dst_ip=Parser_Dst_Ip, dst_port=Parser_Dst_Port, stream_name=Default_Rtsp_Stream_Name):
	ffmpeg_cmd = ("ffmpeg -re -i udp://" + src_ip + ":" + src_port + str_blank +
	              "-f rtsp" + str_blank + "rtsp://" + dst_ip + ":" + dst_port + "/" + stream_name)
	log.debug("ffmpeg_cmd : %s", ffmpeg_cmd)
	process = subprocess.Popen(ffmpeg_cmd, shell=True)
	log.debug("process pid : %d", process.pid)

def x11grab_stream():
	pass