
__all__ = ['Camera_FLIR', ]
import os
import cv2
from time import sleep
from base_camera import BaseCamera
import numpy as np

from FLIRCam.USB_camera import Camera as FLIRCamera
import PySpin


class Camera_FLIR(BaseCamera):
    # video_source = 0

    def __init__(self, cam: FLIRCamera ):
        self.cam = cam
        BaseCamera.__init__(self)
        # super(Camera_FLIR, self).__init__()

    # @staticmethod
    # def set_cam identity_source(source):
    #     Camera_FLIR.video_source = source

    # @staticmethod
    def frames(self):
        # self.FLIRcam = FLIRCamera(model='ptgrey', identity=self.identity, name=self.name)
        # Start acquisition
        self.cam.start()
        # Wait for a while
        sleep(1)

        if not self.cam.is_running:
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            if (0):
                img = self.cam.get_next_image()
            else:
                if self.cam.is_running:
                    frame = self.cam._ptgrey_camera.GetNextImage()
                    image_converted = frame.Convert(PySpin.PixelFormat_RGB8)
                    img = image_converted.GetNDArray()
                    self.cam.log.debug(' Size:' + str(img.shape) \
                                     + ' Type:' + str(img.dtype))
                else:
                    img = np.ones((100,100,3), dtype=np.int8)
            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()

