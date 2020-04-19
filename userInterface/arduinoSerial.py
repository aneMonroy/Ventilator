import datetime
import glob
import os
import sys
import threading
import time

import serial

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject,pyqtSignal,pyqtSlot

class arduinoSerial(QObject):
    newData = pyqtSignal(int,int,int)
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self._serial = serial.Serial('/dev/ttyUSB0',115200,timeout=10,
                                     write_timeout=10)
        self.flush()
        
        self._mp = None
        self._stop = False
        self._start = False
    
    def start(self):
        try:
            self._mp = threading.Thread(target=self.update,args=())
            self._mp.start()
            self._start=True
        except:
            print('ERROR')
    
    def showData(self,data):
        if len(data):
            if data[0] != 'D':
                print(data[0])
            else:
                dat,flow,vol,pre=data.split(",")
                print(flow,vol,pre)
                self.newData.emit(int(flow),int(vol),int(pre))
            
    def update(self):
        while True:
            if self._stop :
                return
            if self._serial.inWaiting()==0:
                continue
            data = self._serial.readline().decode("utf-8")
            
            self.showData(data)
    
    def flush(self):
        self._serial.flushInput()
        self._serial.flushOutput()
    
    def writeData(self,data):
        try:
            self._serial.write(data.encode())
        except:
            print('ERROR IN FUNC INNER')
    
    def close(self):
        self._stop = True
        self._serial.close()
        self._mp.join()
        