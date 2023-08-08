import os

from global_def import *
import subprocess

pip_stream_id_arr = ['a', 'b', 'c', 'd', 'e', 'f', 'g']


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


def rtsp_forwarding():
    command = [FFMPEG_BIN,
               '-hwaccel', 'auto',
               '-rtsp_transport', 'tcp',
               '-re',
               '-i', 'rtsp://192.168.0.15/v02', '-an',
               '-i', 'rtsp://192.168.0.16/v02', '-an',
               '-i', 'rtsp://192.168.0.17/v02', '-an',
               '-max_muxing_queue_size', '512',
               '-filter_complex', '[0:v]pad=iw*2:ih*2[a];[a][1:v]overlay=w[b];[b][2:v]overlay=0:h',
               '-b:v', '2000k', '-f', 'rtsp', '-rtsp_transport', 'tcp', 'rtsp://localhost:8554/av01']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10 ** 8)
    log.debug("process pid : %d", process.pid)
    return process


def forward_rtsp_src_to_parser(src_list, video_bitrate=Default_Video_BitRate,
                            total_window_width=Streaming_Video_Width, total_window_height=Streaming_Video_Height,
                            parser_ip=Parser_Src_Ip, parser_port=Parser_Src_Port):
    number_of_input = len(src_list)
    if number_of_input < 1:
        log.fatal("No Input!")
        return
    log.debug("number_of_input : %d", number_of_input)
    max_row, max_column = get_max_row_and_column(number_of_input)
    ffmpeg_cmd = [FFMPEG_BIN,
                  '-hwaccel', 'auto',
                  '-re',
                  ]
    # handle input src
    input_param = []
    for i in range(number_of_input):
        tmp_input = ['-i', src_list[i]]
        input_param += (tmp_input)
    log.debug("input_param = %s", input_param)

    # handle codec param
    codec_param = ['-b:v', video_bitrate]

    # handle filter_complex param
    scale_width = int(total_window_width / max_row)
    scale_height = int(total_window_height / max_column)
    filter_complex_param = ['-filter_complex']
    p_scale = ''
    pipe_stream_id = 0
    for j in range(number_of_input):
        if j == 0:
            tmp_scale = ('[' + str(j) + ':v]scale='
                         + str(scale_width) + ':' + str(scale_height) + ',pad='
                         + str(total_window_width) + ":" + str(total_window_height)
                         + '[' + pip_stream_id_arr[j] + ']' + ';')
        else:
            tmp_scale = ('[' + str(j) + ':v]scale='
                         + str(scale_width) + ':' + str(scale_height)
                         + '[' + pip_stream_id_arr[j] + ']' + ';')
        pipe_stream_id += 1
        p_scale += tmp_scale
    log.debug("p_scale = %s", p_scale)

    # overlay param
    p_overlay = ''
    row = 0
    column = 0
    for k in range(number_of_input - 1):
        row += 1
        if row >= max_row:
            row = 0
            column += 1
            if column >= max_column:
                column = max_column - 1
        if k == 0:
            tmp_overlay = ('[' + pip_stream_id_arr[k] + ']' + '[' + pip_stream_id_arr[k + 1] + ']'
                           + 'overlay=' + str(int(row * scale_width)) + ':' + str(int(column * scale_height))
                           + '[' + pip_stream_id_arr[pipe_stream_id] + '];')
        elif k == (number_of_input - 2):
            tmp_overlay = ('[' + pip_stream_id_arr[pipe_stream_id - 1] + ']' + '[' + pip_stream_id_arr[k + 1] + ']'
                           + 'overlay=' + str(int(row * scale_width)) + ':' + str(int(column * scale_height)))
        else:
            tmp_overlay = ('[' + pip_stream_id_arr[pipe_stream_id - 1] + ']' + '[' + pip_stream_id_arr[k + 1] + ']'
                           + 'overlay=' + str(int(row * scale_width)) + ':' + str(int(column * scale_height))
                           + '[' + pip_stream_id_arr[pipe_stream_id] + '];')
        pipe_stream_id += 1
        p_overlay += tmp_overlay
    log.debug("p_overlay = %s", p_overlay)
    f_c_p = p_scale + p_overlay
    filter_complex_param.append(f_c_p)
    log.debug("filter_complex_param = %s", filter_complex_param)

    output_param = ['-f', 'h264',
                    'udp://' + parser_ip + ":" + parser_port]

    ffmpeg_cmd += input_param
    ffmpeg_cmd += codec_param
    ffmpeg_cmd += filter_complex_param
    ffmpeg_cmd += output_param

    log.debug("ffmpeg_cmd = %s", ffmpeg_cmd)

    process = subprocess.Popen(ffmpeg_cmd)
    log.debug("process pid : %d", process.pid)
    return process


def get_max_row_and_column(length):
    if length <= 1:
        return 1, 1
    for i in range(8):
        if i * i >= length:
            return i, i
