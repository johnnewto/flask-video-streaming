
from time import sleep
import cv2
from threading import Thread


class App1:
    def __init__(self, src=0):
        self.stopped = False
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.thread = Thread(target=self.update, args=())
        # self.thread.daemon = True   # shutdowm when program quits
        self.thread.start()

    # def start(self):
    #     self.thread.start()
    # def start(self):
    #     # start the thread to read frames from the video stream
    #     # Thread(target=self.update, args=()) \
    #     self.thread.start()
    #     return self

    def update(self):
        # display(self.pb)
        # for i in range(200):
        while True:
            # print(':', end=' ' )
            # print("here")
            sleep(0.001)
            if self.stopped:
                break
            # (self.grabbed, self.frame) = self.stream.read()
            # print("here")

        print("thread finished")

    def stop(self):
        """indicate that the thread should be stopped"""
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()


# app = App1().start()
app = App1()
