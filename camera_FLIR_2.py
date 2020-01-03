
__all__ = ['Camera_FLIR', ]
import os
import cv2
from time import sleep
# from base_camera import BaseCamera
import threading
from FLIRCam.USB_camera import Camera as FLIRCamera
import PySpin

class Camera_FLIR():
    # video_source = 0

    def __init__(self, cam: FLIRCamera ):
        self.cam = cam
        self.frame = None
        # BaseCamera.__init__(self)
        # super(Camera_FLIR, self).__init__()

        self.stopped = False
        self.thread = threading.Thread(target=self.frames, args=())
        # self.thread.daemon = True
        self.thread.start()


    def get_frame(self):
        """Return the current camera frame."""
        # BaseCamera.last_access = time.time()
        #
        # # wait for a signal from the camera thread
        # BaseCamera.event.wait()
        # BaseCamera.event.clear()
        # Todo 'wait for event'
        return self.frame

    # @staticmethod
    def frames(self):
        # self.cam = FLIRCamera(model='ptgrey', identity=self.identity, name=self.name)
        # Start acquisition
        self.cam.start()
        # Wait for a while
        sleep(1)

        if not self.cam.is_running:
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            # img = self.cam.get_next_image()
            frame = self.cam.GetNextImage()
            image_converted = frame.Convert(PySpin.PixelFormat_RGB8)
            image_converted = image_converted.GetNDArray()
            # encode as a jpeg image and return it
            # yield cv2.imencode('.jpg', image_converted)[1].tobytes()
            self.frame = cv2.imencode('.jpg', image_converted)[1].tobytes()


    def stop(self):
        """indicate that the thread should be stopped"""
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()