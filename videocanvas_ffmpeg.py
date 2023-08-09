import tkinter as tk
import cv2
from PIL import Image, ImageTk
from global_def import *
import threading
import time
import subprocess
import numpy


class VideoCanvasFFMpeg(tk.Frame):
    def __init__(self, window, cam_id, video_src, preview_width=default_image_width, preview_height=default_image_width,
                 _row=0, _column=0, video_src_fps=60, *args, **kwargs):
        super().__init__(window)
        self.window = window
        self.cam_id = cam_id
        self.video_capture_running = True
        self.preview_width = preview_width
        self.preview_height = preview_height
        self.video_src = video_src

        self.video_capture_raw_image  = None
        self.raw_image = None # For ffmpeg
        self.image = None   # For Imagetk
        self.photo = None   # For Canvas
        self.video_lost_count = 0
        self.video_src_fps = video_src_fps

        # start thread
        self.video_capture_thread = threading.Thread(target=self.video_capture_process)
        self.video_capture_thread.start()

        # self.canvas = tk.Canvas(window, width=self.preview_width, height=self.preview_height)
        # self.canvas.grid(row=_row, column=_column)
        self.label = tk.Label(window, width=self.preview_width, height=self.preview_height)
        self.label.grid(row=_row, column=_column)
        self.delay = 60
        self.start_canvas_refresh()

    def video_capture_process(self):
        scale_factor = "scale=" + str(self.preview_width) + ":" + str(self.preview_height)
        if 'rtsp' in self.video_src:
            command = [FFMPEG_BIN,
                       '-rtsp_transport', 'tcp',
                       '-i', self.video_src,
                       '-f', 'image2pipe',
                       '-pix_fmt', 'rgb24',
                       '-vcodec', 'rawvideo', '-vf', scale_factor, '-']
        else:
            command = [FFMPEG_BIN,
                       '-hwaccel', 'auto',
                       '-stream_loop', '-1',
                       '-re',
                       '-i', self.video_src,
                       '-f', 'image2pipe',
                       '-pix_fmt', 'rgb24',
                       '-vcodec', 'rawvideo', '-vf', scale_factor, '-']
        log.debug("ffmpeg cmd : %s", command)
        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10 ** 8)
        while self.video_capture_running is True:
            try:
                self.raw_image = pipe.stdout.read(self.preview_width * self.preview_height * 3)
                # transform the byte read into a numpy array
                image = numpy.fromstring(self.raw_image, dtype='uint8')
                image = image.reshape((self.preview_height, self.preview_width, 3))
                # throw away the data in the pipe's buffer.
                pipe.stdout.flush()
                # assign new frame
                self.video_capture_raw_image = image # Already resize anc cvtColor

            except Exception as e:
                log.debug("%s", e)

                # sleep for next frame
            time.sleep(1 / self.video_src_fps)

        print("[Error] exit video_capture_process")

    def __del__(self):
        # stop thread
        if self.video_capture_running:
            self.video_capture_running = False
            self.video_capture_thread.join()

        # relase stream
        if self.cv2_video_capture.isOpened():
            self.cv2_video_capture.release()

    def start_canvas_refresh(self):
        self.video_loop()

    def video_loop(self):
        if self.video_capture_running is True and self.video_capture_raw_image is not None:
            # pass
            self.image = None
            self.photo = None

            self.image = Image.fromarray(self.video_capture_raw_image)
            self.photo = ImageTk.PhotoImage(image=self.image)

            # self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.label.configure(image=self.photo)

        else:
            print("[Error] video_capture_ret = False")

        self.label.after(self.delay, self.video_loop)
