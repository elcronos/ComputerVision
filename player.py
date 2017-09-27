#!/usr/bin/env python

import cv2, numpy as np
import sys
import time
import threading
from scipy.spatial import distance as dist


class PlayerState(object):
    PLAYING = 0
    PAUSED  = 1
    STOPPED = 2

class PlayerCmd(object):
    PLAY       = 0
    FREEZE     = 1
    NEXT_FRAME = 2
    PREV_FRAME = 3
    SCREENSHOT = 4

class InfoVideo(object):
    def __init__(self, filename):
        self._capture = cv2.VideoCapture(filename)
    def GetTotalFrames(self):
        return self._capture.get(cv2.CAP_PROP_FRAME_COUNT)
    def GetFramerate(self):
        return self._capture.get(cv2.CAP_PROP_FPS)
    def GetCurFrame(self):
        return self._capture.read()
    def SetPosInFrame(self, pos):
        self._capture.set(cv2.CAP_PROP_POS_FRAMES, pos)

class Player(object):
    def __init__(self, filename):
        self._filename  = filename
        self._framerate = 5
        self._cur_pos   = 0
        self._state     = PlayerState.PAUSED
        self._lock      = threading.RLock()
        self._win       = "SmartVision"
        self.refPt      = None
        # Distances in Pixeles
        self.dist_road  = None
        self.dist_obj   = None
        # Distances in meters
        self.DISTANCE_ROAD   = 2
        self.DISTANCE_OBJ   = None
        assert(self._Init())

    def _Init(self):
        cv2.namedWindow(self._win)
        cv2.setMouseCallback(self._win, self.click_event)
        cv2.moveWindow(self._win, 250, 150)
        self._info      = InfoVideo(self._filename)
        self._total_frames = self._info.GetTotalFrames()
        self._framerate    = self._info.GetFramerate()
        return True

    def __del__(self):
        cv2.destroyWindow(self._window)

    def _OnProgressBarChanged(self, x):
        pass

    def _OnSpeedBarChanged(self, x):
        with self._lock:
            self._framerate = x

    def Start(self):
        with self._lock:
            self._thread = threading.Thread(
                target = self._ThreadProc,
                args =  ())
            self._thread.start()
            self.Play()

    def Stop(self):
        print 'stop'
        with self._lock:
            self._state = PlayerState.STOPPED
            self._thread.join()

    def Play(self):
        print 'play'
        with self._lock:
            self._state = PlayerState.PLAYING

    def Pause(self):
        print 'pause'
        with self._lock:
            self._state = PlayerState.PAUSED

    def SetFramerate(self, framerate):
        with self._lock:
            self._framerate = framerate

    def GetCurPos(self):
        with self._lock:
            return self._cur_pos

    def SeekTo(self, pos_in_frame):
        print 'seek'
        with self._lock:
            self._cur_pos   = pos_in_frame
            self._ShowCurFrame()

    def SaveCurFrame(self):
        with self._lock:
            ret, im = self._info.GetCurFrame()
            filename = "./" + "Frame_" + str(self.GetCurPos())+".jpg"
            cv2.imwrite(filename, im)
            print "Saved Frame: " + filename

    def _ThreadProc(self):
        while self._state in [PlayerState.PLAYING, PlayerState.PAUSED]:
            with self._lock:
                self._OneLoopLocked()
            time.sleep(1.0 / self._framerate)

    def _OneLoopLocked(self):
        try:
            if self._state == PlayerState.PLAYING:
                if self._cur_pos == self._total_frames - 1:
                    self._cur_pos = 0
                self._ShowCurFrame()
                self._cur_pos += 1
            elif self._state == PlayerState.PAUSED:
                self._ShowCurFrame()
                pass
            else:
                assert(False)
        except:
            pass

    def _ShowCurFrame(self):
        self._info.SetPosInFrame(self._cur_pos)
        ret, im = self._info.GetCurFrame()
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(im, '%s' % self._StateText(self._state), (50, 50), font, 1.2, (0, 255, 0), 2)
        # Two Points - First Line
        if self.refPt is not None:
            if len(self.refPt) > 1:
                cv2.line(im, (self.refPt[0][0], self.refPt[0][1]), (self.refPt[1][0], self.refPt[0][1]), (255, 100, 255), 2)
                self.dist_road = dist.euclidean((self.refPt[0][0], self.refPt[0][1]), (self.refPt[1][0], self.refPt[0][1]))
                cv2.putText(im, 'Distance Lane Road: %s(m)' % self.DISTANCE_ROAD, (50, 100), font, 1.2, (255, 100, 255), 2)
            # Three points - Second Line
            if len(self.refPt) > 2:
                cv2.line(im, (self.refPt[1][0], self.refPt[0][1]), (self.refPt[2][0], self.refPt[0][1]), (255, 255, 0), 2)
                self.dist_obj = dist.euclidean( (self.refPt[1][0], self.refPt[0][1]), (self.refPt[2][0], self.refPt[0][1]))
                self.DISTANCE_OBJ = (self.dist_obj * self.DISTANCE_ROAD) / self.dist_road
                cv2.putText(im, 'Distance Roadside Hazard: %s(m)' % self.DISTANCE_OBJ, (50, 150), font, 1.2, (255, 255, 0), 2)
        cv2.imshow(self._win, im)

    def _StateText(self, x):
        return {
            0: 'PLAYING',
            1: 'PAUSED',
            2: 'STOPPED',
        }.get(x, 'INVALID')

    def click_event(self, event, x, y, flags, param):
    	# if the left mouse button was clicked, record the starting
    	# (x, y) coordinates and indicate that cropping is being
    	# performed
    	if event == cv2.EVENT_LBUTTONDOWN:
		if self.refPt is None:
			self.refPt = [(x, y)]

    		elif len(self.refPt) > 0:
                	self.refPt.append((x, self.refPt[0][1]))

        '''
    	# check to see if the left mouse button was released
    	elif event == cv2.EVENT_LBUTTONUP:
    		# record the ending (x, y) coordinates and indicate that
    		# the cropping operation is finished
    		self.refPt.append((x, y))
        '''
