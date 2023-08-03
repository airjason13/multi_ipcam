import os

from global_def import *
import subprocess


def kill_all_ffmpeg_process():
	cmd = "pkill ffmpeg"
	os.popen(cmd)


def rtsp_parser_streaming(src_ip=Parser_Src_Ip, src_port=Parser_Src_Port,
                          dst_ip=Parser_Dst_Ip, dst_port=Parser_Dst_Port, stream_name=Default_Rtsp_Stream_Name,
                          video_bitrate=Default_Video_BitRate):
	ffmpeg_cmd = ("ffmpeg -re -i udp://" + src_ip + ":" + src_port + "?overrun_nonfatal=1"
				  + str_blank + "-b:v" + str_blank + video_bitrate + str_blank
	              + "-f rtsp" + str_blank + "rtsp://" + dst_ip + ":" + dst_port + "/" + stream_name + str_blank + "&")
	log.debug("rtsp_parser_streaming ffmpeg_cmd : %s", ffmpeg_cmd)
	process = subprocess.Popen(ffmpeg_cmd, shell=True)
	log.debug("process pid : %d", process.pid)
	return process


def x11grab_stream(src_width, src_height, out_width=Streaming_Video_Width, out_height=Streaming_Video_Height,
                   src_x=0, src_y=0, encode_factor=Default_Encode_Factor, video_bitrate=Default_Video_BitRate,
                   dst_ip=Parser_Src_Ip, dst_port=Parser_Src_Port):
	src_video_res = str(src_width) + "x" + str(src_height)
	src_video_pos = str(src_x) + "," + str(src_y)
	video_out_res = str(out_width) + "x" + str(out_height)
	ffmpeg_cmd = ("ffmpeg -re -f x11grab -video_size" + str_blank + src_video_res + str_blank
	              + "-i :1+" + src_video_pos + str_blank
	              + "-s" + str_blank + video_out_res + str_blank
	              + "-b:v" + str_blank + video_bitrate + str_blank
	              + "-f" + str_blank + encode_factor + str_blank
	              + "udp://" + dst_ip + ":" + dst_port + str_blank + "&")
	log.debug("x11grab_stream ffmpeg_cmd : %s", ffmpeg_cmd)
	process = subprocess.Popen(ffmpeg_cmd, shell=True)
	log.debug("process pid : %d", process.pid)
	return process