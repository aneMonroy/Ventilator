import os
import time
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFrame
from PyQt5.QtCore import QObject,pyqtSignal,pyqtSlot
from threadEncoder import*

from varsFuncs import*

current_dir = os.path.dirname(os.path.abspath(__file__))
Form, Base = uic.loadUiType(os.path.join(current_dir, "ui/alarms.ui"))


class alarmWidget(Base, Form):
    def __init__(self, parent=None):
        super(alarmWidget, self).__init__(parent)
        self.setupUi(self)
        
        self.data = loadData()
            
        self._Apress = self.data['alarms']['apress']
        self._Avol = self.data['alarms']['avol']
        self._Abpm = self.data['alarms']['arate']
        self._Aapnea = self.data['alarms']['aapnea']
        self.exit = False
        
        self.menuObs = {1:self.pressure,2:self.volume,
                            3:self.rate,4:self.apnea,
                            5:self.exitL}
        
        self.rotaryEncoder = signalEncoder()
        self.rotaryEncoder.buttonPressed.connect(self.pressed)
        self.rotaryEncoder.rotatedCW.connect(self.rotCW)
        self.rotaryEncoder.rotatedCCW.connect(self.rotCCW)
            
        self.nowM=5
        self.togglePress=0
        self.alarmSelection = 5
        self.selectionEvent()
        self.ignoreCall=False
        
        
        self.changeApress()
        self.changeAvol()
        self.changeArate()
        self.changeAapnea()
    
    @pyqtSlot(int)
    def pressed(self,pin):
        if self.togglePress==0:
            self.menuObs[self.nowM].setStyleSheet("background-color: rgb(170,85,0)")
            self.togglePress=1
            self.ignoreCall=True
            if self.nowM == 5:
                time.sleep(0.1)
                self.close()
        else:
            self.menuObs[self.nowM].setStyleSheet("background-color: rgb(85,170,170)")
            self.togglePress=0
            self.ignoreCall=False
    
    @pyqtSlot(int)
    def rotCW(self,pin):
        if not self.ignoreCall:
            if self.alarmSelection>0:
                self.alarmSelection-=1
            self.selectionEvent()
        else:
            if self.nowM == 1:
                if self._Apress == -1:
                    self._Apress = 40
                elif self._Apress < 6:
                    self._Apress = -1
                else:
                    self._Apress -= 1
                self.changeApress()
            elif self.nowM == 2:
                if self._Avol == -1:
                    self._Avol = 750
                elif self._Avol < 150:
                    self._Avol = -1
                else:
                    self._Avol -= 50
                self.changeAvol()
            elif self.nowM == 3:
                if self._Abpm == -1:
                    self._Abpm = 35
                elif self._Abpm < 2:
                    self._Abpm = -1
                else:
                    self._Abpm -= 1
                self.changeArate()
            elif self.nowM == 4:
                if self._Aapnea == -1:
                    self._Aapnea = 20
                elif self._Aapnea < 2:
                    self._Aapnea = -1
                else:
                    self._Aapnea -= 1
                self.changeAapnea()
                
    @pyqtSlot(int)
    def rotCCW(self,pin):
        if not self.ignoreCall:
            if self.alarmSelection<6:
                self.alarmSelection+=1
            self.selectionEvent()
        else:
            if self.nowM == 1:
                if self._Apress == -1:
                    self._Apress = 5
                elif self._Apress >39:
                    self._Apress = -1
                else:
                    self._Apress +=1
                self.changeApress()
                
            elif self.nowM == 2:
                if self._Avol == -1:
                    self._Avol = 100
                elif self._Avol >700:
                    self._Avol = -1
                else:
                    self._Avol +=50
                self.changeAvol()
            elif self.nowM == 3:
                if self._Abpm == -1:
                    self._Abpm = 1
                elif self._Abpm >34:
                    self._Abpm = -1
                else:
                    self._Abpm +=1
                self.changeArate()
            elif self.nowM == 4:
                if self._Aapnea == -1:
                    self._Aapnea = 1
                elif self._Aapnea >19:
                    self._Aapnea = -1
                else:
                    self._Aapnea +=1
                self.changeAapnea()
                    
    def changeApress(self):
        if self._Apress == -1:
            self.pressureData.setText("OFF")
        else:
            self.pressureData.setText("{} cmH2O".format(self._Apress))
 
    def changeAvol(self,):
        if self._Avol == -1:
            self.volumeData.setText("OFF")
        else:
            self.volumeData.setText("{} mL".format(self._Avol))

    def changeArate(self):
        if self._Abpm == -1:
            self.rateData.setText("OFF")
        else:
            self.rateData.setText("{} rpm".format(self._Abpm))
    
    def changeAapnea(self):
        if self._Aapnea == -1:
            self.apneaData.setText("OFF")
        else:
            self.apneaData.setText("{} s.".format(self._Aapnea))
        
    def setSelected(self,objT):
        if objT == self.exitL:
            objT.setStyleSheet("background-color: rgb(85,170,170);\ncolor: rgb(255, 255, 255);\nborder-style: outset;\nborder-width: 2px;\nborder-radius: 10px;\nborder-color: white;")
        else:
            objT.setStyleSheet("background-color: rgb(85,170,170)")
    
    def setDeselect(self,objT):
        if objT == self.exitL:
            objT.setStyleSheet("color: rgb(255, 255, 255);\nborder-style: outset;\nborder-width: 2px;\nborder-radius: 10px;\nborder-color: white;")
        else:
            objT.setStyleSheet("")
    
    def selectionEvent(self):
        if self.alarmSelection<1:
            self.setSelected(self.pressure)
            self.setDeselect(self.volume)
            self.nowM=1
        elif self.alarmSelection==2:
            self.setDeselect(self.pressure)
            self.setDeselect(self.rate)
            self.setSelected(self.volume)
            self.nowM=2
        elif self.alarmSelection==3:
            self.setDeselect(self.volume)
            self.setDeselect(self.apnea)
            self.nowM=3
            self.setSelected(self.rate)
        elif self.alarmSelection==4:
            self.setDeselect(self.rate)
            self.setDeselect(self.exitL)
            self.nowM=4
            self.setSelected(self.apnea)
        elif self.alarmSelection==5:
            self.setDeselect(self.apnea)
            self.nowM=5
            self.setSelected(self.exitL)
    
    def closeEvent(self,event):
        self.rotaryEncoder.stopEncoder()
        print(self._Apress,self._Avol,self._Abpm,self._Aapnea)
        self.data['alarms']['apress'] = self._Apress
        self.data['alarms']['avol'] = self._Avol
        self.data['alarms']['arate'] = self._Abpm
        self.data['alarms']['aapnea'] = self._Aapnea
        updateData(self.data)
        event.accept()

if __name__ == '__main__':
    import sys
    app = QApplication([])
    app.setStyle("fusion")
    w = alarmWidget()
    w.show()
    sys.exit(app.exec_())