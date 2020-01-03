#!/usr/bin/env python

from time import sleep
from flask import Flask, render_template, Response
# from camera_opencv import Camera
from camera_FLIR import Camera_FLIR
from FLIRCam.USB_camera import Camera as FLIRCamera
cam_1 = FLIRCamera(model='ptgrey', identity='19312753', name='FrontLeft')

app = Flask(__name__)
from flask import request


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()



@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera_FLIR(cam_1)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/shutdown')
def shutdown():
    cam_1.stop()
    # sleep(1)
    shutdown_server()
    return 'Server shutting down...'


if __name__ == '__main__':

    app.run(host='0.0.0.0', threaded=True, use_reloader=False)



    # from multiprocessing import Process
    #
    # server = Process(target=app.run)
    # server.start()
    # # # ...
    # # server.terminate()
    # # server.join()