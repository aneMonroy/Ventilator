import os
import sys
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFrame
import pyqtgraph as pg
import time
from datetime import datetime
import serial
import numpy as np

from threadEncoder import*
from alarmPage import*
from arduinoSerial import*



current_dir = os.path.dirname(os.path.abspath(__file__))
Form, Base = uic.loadUiType(os.path.join(current_dir, "ui/main.ui"))

# pg.setConfigOption('background', '052049')
pg.setConfigOption('leftButtonPan', False)
        
class MainWindow(Base, Form):
    '''MAIN CLASS TO CONTROL GUI'''

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.data = loadData()
        #------ Serial ------
        self._actSerial = self.data['comms']['activeSerial']
        if self._actSerial==1:
            self.ser = arduinoSerial()
            self.ser.start()
            self.ser.newData.connect(self.serialRead)
        #------ GRAPHS ------
        self.myCurve = [0, 0, 0]
        self.chunkSize = 200
        self.split = 100
        self.xAxis = np.arange(self.chunkSize)
        self.data1 = np.zeros((self.chunkSize, 4))
        self.plot(0, self.graphFlow, "C", self.xAxis, self.data1[:, 0])
        self.plot(1, self.graphPressure, "P", self.xAxis, self.data1[:, 1])
        self.plot(2, self.graphVolume, "V", self.xAxis, self.data1[:, 2])
        self.myCurve[0].setPen(pg.mkPen('fbcca7', width=2))
        self.myCurve[1].setPen(pg.mkPen('a3dade', width=2))
        self.myCurve[2].setPen(pg.mkPen('ffaa00', width=2))#ffaa00
        self.pointer = 0
        self.firstCycle = 1
        #--------- Variables ---------
        
        
        self._pres1 = 0
        self._pres2 = 0
        self._pip = 20
        self._dflow =0
        self._dvol = 0
        self._dpres = 0
        
        #--- Configuration VARS --- #
        self._peep = self.data['config']['peep']
        self._fr = self.data['config']['bpm']
        self._vol = self.data['config']['vol']
        self._ratio = self.data['config']['ratio']

        #---- STARTED ---
        self.update()

        self.menuObs = {1:self.bpm,2:self.tidalVol,
                        3:self.ieConf,4:self.peepConf,
                        5:self.alarmConf}
        self.ratioOps = {1:'1:1',2:'1:2',3:'1:3',4:'1:4'}
        
        self.rotaryEncoder = signalEncoder()
        self.rotaryEncoder.buttonPressed.connect(self.pressed)
        self.rotaryEncoder.rotatedCW.connect(self.rotCW)
        self.rotaryEncoder.rotatedCCW.connect(self.rotCCW)
        

        self.confSelection = 0


        self.selectionEvent()
        self.ignoreCall = False
        self.nowM=1
        self.togglePress=0
    
    def serialSend(self,indexN):
        try:
            if indexN==1:
                self.ser.writeData('BPM {}'.format(self._fr))
            elif indexN==2:
                self.ser.writeData('VOL {}'.format(self._vol))
            elif indexN == 3:
                self.ser.writeData('IRE {}'.format(self._ratio))
            elif indexN == 4:
                self.ser.writeData('PEEP {}'.format(self._peep))
            else:
                pass
        except:
            print('COM ERROR')
            
    @pyqtSlot(int,int,int)
    def serialRead(self,fl,vl,pr):
        self._dflow = fl
        self._dvol = vl
        self._dpres = pr
        self.update()
        #print('RECV: {} {} {}'.format(fl,vl,pr))
        
    def flush(self):
        self.ser.flush()
        self.ser.flush()
    
    @pyqtSlot(int)
    def pressed(self,pin):
        if self.togglePress==0:
            self.menuObs[self.nowM].setStyleSheet("background-color: rgb(0,144,211)")
            self.togglePress=1
            self.ignoreCall=True
            if self.nowM == 5:
                self.rotaryEncoder.stopEncoder()
                self.pageAlarm = alarmWidget()
                self.pageAlarm.move(250,250)
                self.pageAlarm.exec_()
                self.rotaryEncoder = signalEncoder()
                self.rotaryEncoder.buttonPressed.connect(self.pressed)
                self.rotaryEncoder.rotatedCW.connect(self.rotCW)
                self.rotaryEncoder.rotatedCCW.connect(self.rotCCW)
                self.menuObs[self.nowM].setStyleSheet("background-color: rgb(85, 85, 127)")
                self.togglePress=0
                self.ignoreCall=False
        else:
            self.menuObs[self.nowM].setStyleSheet("background-color: rgb(85, 85, 127)")
            self.togglePress=0
            self.ignoreCall=False
            if self._actSerial==1:
                self.serialSend(self.nowM)

    @pyqtSlot(int)
    def rotCW(self,pin):
        if not self.ignoreCall:
            if self.confSelection>0:
                self.confSelection-=1
            self.selectionEvent()
        else:
            if self.nowM == 1:
                self._fr-=1
                self.changeBPM()              
            elif self.nowM == 2:
                self._vol-=50
                self.changeVol()
            elif self.nowM == 3:
                self._ratio-=1
                self.changeRatio()
            elif self.nowM == 4:
                self._peep-=1
                self.changePeep()
                
    @pyqtSlot(int)
    def rotCCW(self,pin):
        if not self.ignoreCall:
            if self.confSelection<6:
                self.confSelection+=1
            self.selectionEvent()
        else:
            if self.nowM == 1:
                self._fr+=1
                self.changeBPM()
            elif self.nowM == 2:
                self._vol+=50
                self.changeVol()
            elif self.nowM == 3:
                self._ratio+=1
                self.changeRatio()
            elif self.nowM == 4:
                self._peep+=1
                self.changePeep()
                
    def changeBPM(self):
        if self._fr < 2:
            self._fr=30
        elif self._fr > 30:
            self._fr=2
        self.actualBPM.setText('{} BPM'.format(self._fr))
        
    def changeVol(self):
        if self._vol < 50:
            self._vol=2000
        elif self._vol > 2000:
            self._vol=50
        self.actualVolume.setText('{} mL'.format(self._vol))    
    
    def changeRatio(self):
        if self._ratio < 2:
            self._ratio=4
        elif self._ratio >4:
            self._ratio=2
        self.actualRatio.setText(self.ratioOps[self._ratio])
    
    def changePeep(self):
        if self._peep < 2:
            self._peep=10
        elif self._peep > 10:
            self._peep=2
        self.actualPEEP.setText('{} cmH2O'.format(self._peep))
    
    def setSelected(self,objT):
        objT.setStyleSheet("background-color: rgb(85, 85, 127)")
    
    def setDeselect(self,objT):
        objT.setStyleSheet("")
    
    def selectionEvent(self):
        self.ignoreCall=True
        if self.confSelection<2:
            self.setSelected(self.bpm)
            self.setDeselect(self.tidalVol)
            self.nowM=1
        elif self.confSelection==2:
            self.setDeselect(self.bpm)
            self.setDeselect(self.ieConf)
            self.setSelected(self.tidalVol)
            self.nowM=2
        elif self.confSelection==3:
            self.setDeselect(self.tidalVol)
            self.setDeselect(self.peepConf)
            self.setSelected(self.ieConf)
            self.nowM=3
        elif self.confSelection==4:
            self.setDeselect(self.ieConf)
            self.setDeselect(self.alarmConf)
            self.setSelected(self.peepConf)
            self.nowM=4
        elif self.confSelection==5:
            self.setDeselect(self.peepConf)
            self.setSelected(self.alarmConf)
            self.nowM=5
        self.ignoreCall=False
    
    
    def plot(self, chartIndex, widget, title, hour, temperature):
        self.myCurve[chartIndex] = widget.plot(hour, temperature, title=title)
        widget.setXRange(0, self.chunkSize, padding=0)
        if chartIndex == 0:
            widget.setYRange(0, 100)
        elif chartIndex ==1:
            widget.setYRange(0, 100)
        else :
            widget.setYRange(0,100)
            
        widget.setMouseEnabled(False, False)
        widget.disableAutoRange()
        widget.showGrid(True, True, 1)
    
    def update(self):
        pres = self._dpres
        flow = self._dflow
        vol = self._dvol
        self.i = self.pointer % (self.chunkSize)
        if self.i == 0 and self.firstCycle == 0:
            tmp = np.empty((self.chunkSize, 4))
            tmp[:self.split] = self.data1[self.chunkSize - self.split:]
            self.data1 = tmp
            self.pointer = self.split
            self.i = self.pointer
        self.data1[self.i, 0] = float(flow)
        self.data1[self.i, 1] = float(pres)
        self.data1[self.i, 2] = float(vol)
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
    
    def closeEvent(self,event):
        self.rotaryEncoder.stopEncoder()
        self.ser.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
    
