
__all__ = ['CameraFLIR', ]
import os
import cv2
from time import sleep
from base_camera import BaseCamera
import numpy as np
from imutils import resize
import time
import threading

from FLIRCam.USB_camera import Camera as FLIRCamera
import PySpin

import logging
# logger = logging.getLogger('main')
logger = logging.getLogger(__name__)
class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """
    def __init__(self):
        self.events = {}


    def wait(self, ident, cam_id):
        """Invoked from each client's thread to wait for the next frame."""
        # ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time(), cam_id]
        return self.events[ident][0].wait()

    def set_all(self, cam_id):
        """Invoked by the camera thread when a new frame is available, set events for camera cam_id."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if cam_id == event[2]:
                # if camera id matches
                if not event[0].isSet():
                    # if this client's event is not set, then set it
                    # also update the last set timestamp to now
                    event[0].set()
                    event[1] = now
                    # logger.info(f'EVENT: set event[{cam_id}]:')
                else:
                    # if the client's event is already set, it means the client
                    # did not process a previous frame
                    # if the event stays set for more than 5 seconds, then assume
                    # the client is gone and remove it
                    if now - event[1] > 5:
                        remove = ident
        if remove:
            del self.events[remove]
            logger.info(f'EVENT: remove events[{remove}]:')

    def clear(self, ident):
        """Invoked from each client's thread after a frame was processed."""
        self.events[ident][0].clear()


class CameraFLIR:
    # video_source = 0
    thread = None  # background thread that monitors all cameras
    cam_dict = {}
    nextid = 0
    # last_access = {}
    event = CameraEvent()
    # frame = None

    def __init__(self, cam: FLIRCamera):
        self.id = CameraFLIR.nextid
        CameraFLIR.nextid += 1

        if not cam.identity in CameraFLIR.cam_dict:
            logger.info(f"CameraFLIR: adding camera {cam.identity}")
            # if CameraFLIR.thread is None:
            CameraFLIR.cam_dict[cam.identity] = {'Cam': cam, 'last_access': 0, 'frame': None}
            CameraFLIR.thread = threading.Thread(target=self._thread)
            CameraFLIR.thread.start()

            cam.register_event_handler()
            cam.add_event_callback(self.callback)

        CameraFLIR.cam_dict[cam.identity]['last_access'] = time.time()
        logger.info(f"CameraFLIR: __init__ time = {CameraFLIR.cam_dict[cam.identity]['last_access']}")

        # cam.register_event_handler()
        # cam.add_event_callback(self.callback)

        logger.info(f'Init Cam {cam.name}.')


    def get_frame(self, cam_id):
        """Return the current camera frame."""
        cam = CameraFLIR.cam_dict[cam_id]['Cam']
        # logger.info(f'GETFRAME({cam_id})')

        CameraFLIR.cam_dict[cam.identity]['last_access'] = time.time()

        # wait for a signal from the camera event callback
        CameraFLIR.event.wait(self.id, cam_id)
        # logger.info(f'GET_FRAME: got event[{cam_id}]:')
        CameraFLIR.event.clear(self.id)

        _frame = CameraFLIR.cam_dict[cam_id]['frame']
        _frame = cv2.imencode('.jpg', _frame)[1].tobytes()
        return _frame

    @classmethod
    def callback(cls, image, frameID, timestamp, cam_id):
        # if frameID % 10 == 0:
            # print(f'CALLBACK: Cam1: {cam_id}, image received, frame_ID: {frameID},  image.shape, {image.shape}')
        try:
            _image = resize(image, width=500)
        except:
            _image = np.ones((100, 100, 3), dtype=np.int8)
        CameraFLIR.cam_dict[cam_id]['frame'] = _image
        # cls.frame = image
        cls.event.set_all(cam_id)

    TIMEOUT = 2
    @classmethod
    def _thread(cls):
        """Camera background monitoring thread."""
        while True:
            for it in cls.cam_dict.values():
                cam = it['Cam']

                # logger.info(f"THREAD: time diff: {time.time() - it['last_access']}, cam running: {cam.is_running}")
                # if any client asks for frames in
                # the last xx seconds then start the camera
                if not cam.is_running and time.time() - it['last_access'] < cls.TIMEOUT :
                    # logger.info(f'THREAD: Starting camera {cam.name} and callback.')
                    cam.start()

                # if there hasn't been any clients asking for frames in
                # the last xx seconds then stop the camera
                if cam.is_running and time.time() - it['last_access'] > cls.TIMEOUT:
                    # logger.info(f"THREAD: Stopping camera {cam.identity} event due to inactivity.")
                    try:
                        cam.stop()
                    except:
                        logger.warning(f"Failed is Stopping camera {cam.identity}")

            time.sleep(1)


