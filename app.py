#!/usr/bin/env python
import logging
import logging.config
from logging.handlers import RotatingFileHandler
import os
import atexit
from time import sleep
from flask import Flask, render_template, Response, request
# import json
#
# print('Setting up logging')
# if not os.path.exists('logs'):
#     os.mkdir('logs')
#
# with open('logging.json') as f:
#     config = json.load(f)
# logging.config.dictConfig(config)
# # logging.config.dictConfig(config)
# # from logging.config import fileConfig
# # # create logger
# # logger = logging.getLogger('applog')
# logger = logging.getLogger(__name__)

import os
import json
import logging.config
from pathlib import Path
def setup_logging(default_path='logging.json',
                  default_level=logging.INFO):
    """Setup logging configuration"""
    path = Path(default_path)
    Path('logs').mkdir(parents=True, exist_ok=True)

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
setup_logging()

logger = logging.getLogger(__name__)

# from camera_opencv import Camera
from camera_FLIR import CameraFLIR
from FLIRCam.USB_camera import Camera as FLIRCamera
cam_1 = FLIRCamera(model='ptgrey', identity='19312753', name='FrontLeft')
cam_2 = FLIRCamera(model='ptgrey', identity='19312752', name='FrontRight')


app = Flask(__name__)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()



@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

from imutils.video import FPS

def gen1():
    """Video streaming generator function."""
    cam1 = CameraFLIR(cam_1)
    fps = FPS().start()
    # app.logger.info('Starting Gen 1')
    while True:
        frame = cam1.get_frame(cam_1.identity)
        fps.update()
        fps.stop()
        # print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen2():
    """Video streaming generator function."""
    cam2 = CameraFLIR(cam_2)
    # app.logger.info('Starting Gen 2')
    fps = FPS().start()
    while True:
        frame = cam2.get_frame(cam_2.identity)
        fps.update()
        fps.stop()
        # print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/cam1_video')
def cam1_video():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # return Response(gen1(Camera_FLIR(cam_1)),
    return Response(gen1(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cam2_video')
def cam2_video():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # return Response(gen2(Camera_FLIR(cam_2)),
    return Response(gen2(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cam_1_settings')
def cam_1_settings():
    """Return Camera settings."""
    props = cam_1.getprops(['BinningHorizontal', 'BinningVertical',
                    'OffsetX', 'OffsetY', 'Width', 'Height', 'WidthMax', 'HeightMax',
                    'ExposureTime', 'ExposureAuto', 'AcquisitionFrameRateEnable', 'AcquisitionFrameRate'])
    return props

@app.route('/cam_2_settings')

def cam_2_settings():
    """Return Camera settings."""
    props = cam_2.getprops(['BinningHorizontal', 'BinningVertical',
                    'OffsetX', 'OffsetY', 'Width', 'Height', 'WidthMax', 'HeightMax',
                    'ExposureTime', 'ExposureAuto', 'AcquisitionFrameRateEnable', 'AcquisitionFrameRate'])
    return props


@app.route('/shutdown')
def shutdown() -> str:
    cam_1.stop()
    cam_2.stop()
    # sleep(1)
    shutdown_server()
    return 'Server shutting down...'


if __name__ == '__main__':


    logger.info('APP Startup')

    # defining function to run on shutdown
    def atexit_close_cameras():
        logger.info('ATEXIT, close cameras')
        cam_1.stop()
        cam_1.__del__()
        cam_2.stop()
        cam_2.__del__()
    # Register the function to be called on exit
    atexit.register(atexit_close_cameras)

    cam_1.binning = 1
    cam_1.exposure_time_auto = True

    cam_2.binning = 1
    cam_2.exposure_time_auto = True


    # from werkzeug.middleware.profiler import ProfilerMiddleware
    #
    # app.config['PROFILE'] = True
    # app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    app.run(host='0.0.0.0', threaded=True, use_reloader=False, debug=True)
