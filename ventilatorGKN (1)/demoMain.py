import os
import sys
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFrame
import pyqtgraph as pg
import time
from datetime import datetime

import copy
import numpy as np

import RPi.GPIO as GPIO
from KY040 import KY040
from RPi_GPIO_Rotary import rotary
from alarmPage import*

current_dir = os.path.dirname(os.path.abspath(__file__))
Form, Base = uic.loadUiType(os.path.join(current_dir, "ui/main.ui"))

# pg.setConfigOption('background', '052049')
pg.setConfigOption('leftButtonPan', False)

CLOCKPIN = 5
DATAPIN = 6
SWITCHPIN = 13





        
class MainWindow(Base, Form):
    '''MAIN CLASS TO CONTROL GUI'''

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        #------ GRAPHS ------
        self.timer = pg.QtCore.QTimer()
        # self.timer.timeout.connect(self.serial_read)
        self.myCurve = [0, 0, 0]
        self.chunkSize = 200
        self.split = 100
        self.xAxis = np.arange(self.chunkSize)
        self.data1 = np.zeros((self.chunkSize, 4))
        self.plot(0, self.graphPressure, "P", self.xAxis, self.data1[:, 0])
        self.plot(1, self.graphFlow, "C", self.xAxis, self.data1[:, 1])
        self.plot(2, self.graphVolume, "V", self.xAxis, self.data1[:, 2])
        self.myCurve[0].setPen(pg.mkPen('fbcca7', width=2))
        self.myCurve[1].setPen(pg.mkPen('a3dade', width=2))
        self.myCurve[2].setPen(pg.mkPen('a3dade', width=2))
        self.pointer = 0
        self.firstCycle = 1
        #--------- Variables ---------
        self._pres1 = 0
        self._pres2 = 0
        self._pip = 20
        self._peep = 5
        self._fr = 15
        self._flow = 0
        self._vol = 200
        self._ratio = 2

        #---- STARTED ---
        self.update()

        #Other
#         self.bpm.mousePressEvent = self.bpmEvent
#         self.tidalVol.mousePressEvent = self.tidalVolumeEvent
#         self.ieConf.mousePressEvent = self.ieRatioSelect
#         self.peepConf.mousePressEvent = self.peepEvent

        self.menuObs = {1:self.bpm,2:self.tidalVol,
                        3:self.ieConf,4:self.peepConf,
                        5:self.alarmConf}
        self.ratioOps = {1:'1:1',2:'1:2',3:'1:3',4:'1:4'}
        self.clockPin = 5
        self.dataPin = 6
        self.switchPin = 13
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.clockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.dataPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.confSelection = 0
#         self.timerKY = QtCore.QTimer(self)
#         self.timerKY.timeout.connect(self._clockCallback)
#         self.timerKY.start(0.3)

        self.timerRotary = QtCore.QTimer(self)
        self.timerRotary.timeout.connect(self.loop)
        
        
#         GPIO.add_event_detect(self.clockPin, GPIO.FALLING,
#                                callback=self._clockCallback)
        GPIO.add_event_detect(self.switchPin, GPIO.FALLING,
                              callback=self.switchCallback, bouncetime=200)
        self.selectionEvent()
        self.ignoreCall = False
        self.nowM=1
        self.togglePress=0
        
        self.actualCLK = GPIO.input(self.clockPin)
        self.actualDATA = GPIO.input(self.dataPin)
        self.prevCLK = 0
        self.prevDATA = 0
        self.timerRotary.start(0.1)
        self.timeLastDebounce = 0
        self.delayDebounce = 0.001
        
    
    def loop(self):
        now=time.time()/10        
        if (now-self.timeLastDebounce) > self.delayDebounce:            
            self.actualCLK = GPIO.input(self.clockPin)
            self.actualDATA = GPIO.input(self.dataPin)
            self.checkRotary()
            self.timeLastDebounce = time.time()/10
                    
                
    def changeBPM(self):
        if self._fr < 2:
            self._fr=2
        elif self._fr > 30:
            self._fr=30
        self.actualBPM.setText('{} BPM'.format(self._fr))
        
    def changeVol(self):
        if self._vol < 50:
            self._=50
        elif self._vol > 2000:
            self._vol=2000
        self.actualVolume.setText('{} mL'.format(self._vol))
    
    def changeRatio(self):
        if self._ratio < 2:
            self._ratio=2
        elif self._ratio >4:
            self._ratio=4
        self.actualRatio.setText(self.ratioOps[self._ratio])
    
    def changePeep(self):
        if self._peep < 2:
            self._peep=2
        elif self._peep > 10:
            self._peep=10
        self.actualPEEP.setText('{} cmH2O'.format(self._peep))
        
        
    def switchCallback(self,pin):
        if self.togglePress==0:
            self.menuObs[self.nowM].setStyleSheet("background-color: rgb(0,144,211)")
            self.togglePress=1
            self.ignoreCall=True
            if self.nowM == 5:
                GPIO.remove_event_detect(self.switchPin)
                self.pageAlarm = alarmWidget()
                self.pageAlarm.move(250,270)
                self.pageAlarm.exec_()
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.clockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(self.dataPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(self.switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(self.switchPin, GPIO.FALLING,
                              callback=self.switchCallback, bouncetime=200)
        else:
            self.menuObs[self.nowM].setStyleSheet("background-color: rgb(85, 85, 127)")
            self.togglePress=0
            self.ignoreCall=False
            
                   
    
    
    def setSelected(self,objT):
        objT.setStyleSheet("background-color: rgb(85, 85, 127)")
    
    def setDeselect(self,objT):
        objT.setStyleSheet("")
    
    def selectionEvent(self):

        print(self.confSelection)
        self.ignoreCall=True
        if self.confSelection<2:
            self.setSelected(self.bpm)
            self.setDeselect(self.tidalVol)
            self.nowM=1
        elif self.confSelection>=2 and self.confSelection <4:
            self.setDeselect(self.bpm)
            self.setDeselect(self.ieConf)
            self.setSelected(self.tidalVol)
            self.nowM=2
        elif self.confSelection>=4 and self.confSelection <6:
            self.setDeselect(self.tidalVol)
            self.setDeselect(self.peepConf)
            self.setSelected(self.ieConf)
            self.nowM=3
        elif self.confSelection>=6 and self.confSelection <8:
            self.setDeselect(self.ieConf)
            self.setDeselect(self.alarmConf)
            self.setSelected(self.peepConf)
            self.nowM=4
        elif self.confSelection>=8 and self.confSelection <10:
            self.setDeselect(self.peepConf)
            self.setSelected(self.alarmConf)
            self.nowM=5
            
        
        self.ignoreCall=False
    
    
    def plot(self, chartIndex, widget, title, hour, temperature):
        self.myCurve[chartIndex] = widget.plot(hour, temperature, title=title)
        widget.setXRange(0, self.chunkSize, padding=0)
        if chartIndex == 0:
            widget.setYRange(0, 50)
        elif chartIndex ==1:
            widget.setYRange(-20, 30)
        else :
            widget.setYRange(0,2)
        widget.setMouseEnabled(False, False)
        widget.disableAutoRange()
        widget.showGrid(True, True, 1)
    
    def update(self):
        pres = self._pres1
        flow = self._flow
        vol = self._vol
        self.i = self.pointer % (self.chunkSize)
        if self.i == 0 and self.firstCycle == 0:
            tmp = np.empty((self.chunkSize, 3))
            tmp[:self.split] = self.data1[self.chunkSize - self.split:]
            self.data1 = tmp
            self.pointer = self.split
            self.i = self.pointer
        self.data1[self.i, 0] = pres
        self.data1[self.i, 1] = float(flow) / 1000.0
        self.data1[self.i, 2] = float(vol)/1000.0
        self.myCurve[0].setData(
            x=self.xAxis[:self.i + 1],
            y=self.data1[:self.i + 1, 0],
            clear=True
        )
        self.myCurve[1].setData(
            x=self.xAxis[:self.i + 1],
            y=self.data1[:self.i + 1, 1],
            clear=True
        )
        self.myCurve[2].setData(
            x=self.xAxis[:self.i + 1],
            y=self.data1[:self.i + 1, 2],
            clear=True
        )
        QtGui.QApplication.processEvents()
        self.pointer += 1
        if self.pointer >= self.chunkSize:
            self.firstCycle = 0
    
    def checkRotary(self):
        if self.ignoreCall==False:
            if self.actualCLK ==0 and self.prevCLK ==1:
                if self.actualDATA==1:
                    if self.confSelection < 10:
                        self.confSelection+=1
                        self.selectionEvent()
                    else:
                        self.confSelection=10
                else:
                    if self.confSelection>0:
                        self.confSelection-=1
                        self.selectionEvent()
                    else:
                        self.confSelection=0
        else:
            if self.nowM == 1:
                if self.actualCLK ==0 and self.prevCLK ==1:
                    if self.actualDATA==1:
                        self._fr-=1
                    else:
                        self._fr+=1
                    self.changeBPM()
            elif self.nowM == 2:
                if self.actualCLK ==0 and self.prevCLK ==1:
                    if self.actualDATA==1:
                        self._vol-=1
                    else:
                        self._vol+=1
                    self.changeVol()
            elif self.nowM == 3:
                if self.actualCLK ==0 and self.prevCLK ==1:
                    if self.actualDATA==1:
                        self._ratio-=1
                    else:
                        self._ratio+=1
                    self.changeRatio()
            
            elif self.nowM == 4:
                if self.actualCLK ==0 and self.prevCLK ==1:
                    if self.actualDATA==1:
                        self._peep-=1
                    else:
                        self._peep+=1
                    self.changePeep()
                
        self.prevCLK = self.actualCLK
        
    
    def closeEvent(self,event):
        self.timerRotary.stop()

        GPIO.cleanup()
        event.accept()


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
    