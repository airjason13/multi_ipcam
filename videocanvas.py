import tkinter as tk
import cv2
from PIL import Image, ImageTk
from global_def import *
import threading
import time


class VideoCanvas(tk.Frame):
    def __init__(self, window, cam_id, video_src, preview_width=default_image_width, preview_height=default_image_width,
                 _row=0, _column=0, video_src_fps=60, *args, **kwargs):
        super().__init__(window)
        self.window = window
        self.cam_id = cam_id
        self.video_capture_running = True
        self.preview_width = preview_width
        self.preview_height = preview_height
        self.video_src = video_src
        self.cv2_video_capture = cv2.VideoCapture(self.video_src)

        self.video_capture_ret = False    # For opencv
        self.video_capture_frame = None   # For opencv
        self.image = None   # For Imagetk
        self.photo = None   # For Canvas
        self.video_lost_count = 0
        self.video_src_fps = video_src_fps

        # start thread
        self.video_capture_thread = threading.Thread(target=self.video_capture_process)
        self.video_capture_thread.start()

        self.canvas = tk.Canvas(window, width=self.preview_width, height=self.preview_height)
        self.canvas.grid(row=_row, column=_column)
        self.delay = 30
        self.start_canvas_refresh()

    def video_capture_process(self):
        while self.video_capture_running is True:
            if self.cv2_video_capture is None:
                self.cv2_video_capture = cv2.VideoCapture(self.video_src)
                print("[Info] re-open cv2_video_capture")
                time.sleep(1)

            if self.cv2_video_capture is not None:
                ret, frame = self.cv2_video_capture.read()
                if ret:
                    # process image
                    frame = cv2.resize(frame, (self.preview_width, self.preview_height))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    print('[Error] cam_id : ' + str(self.cam_id) + ',stream end:', self.video_src)
                    # TODO: reopen stream
                    # self.video_capture_running = False
                    if self.cv2_video_capture.isOpened():
                        self.cv2_video_capture.release()
                    self.cv2_video_capture = None
                    # break

                # assign new frame
                self.video_capture_ret = ret
                self.video_capture_frame = frame # Already resize anc cvtColor

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
        if self.video_capture_ret is True and self.video_capture_frame is not None:
            self.image = Image.fromarray(self.video_capture_frame)
            self.photo = ImageTk.PhotoImage(image=self.image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        else:
            print("[Error] video_capture_ret = False")

        self.canvas.after(self.delay, self.video_loop)