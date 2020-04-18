import RPi.GPIO as GPIO
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject,pyqtSignal,pyqtSlot

class signalEncoder(QObject):
    
    buttonPressed = pyqtSignal(int)
    rotatedCW = pyqtSignal(int)
    rotatedCCW = pyqtSignal(int)
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.clockPin = 5
        self.dataPin = 6
        self.switchPin = 13
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.clockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.dataPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        GPIO.add_event_detect(self.switchPin, GPIO.FALLING,
                              callback=self.switchCallback, bouncetime=50)
        GPIO.add_event_detect(self.clockPin, GPIO.FALLING,
                              callback=self.clockCallback, bouncetime=50)
        
    def switchCallback(self,pin):
        self.buttonPressed.emit(pin)
        
    def clockCallback(self,pin):
        if GPIO.input(self.clockPin) == 0:
            if GPIO.input(self.dataPin):
                self.rotatedCW.emit(GPIO.input(self.dataPin))
            else:
                self.rotatedCCW.emit(GPIO.input(self.dataPin))
    
    def stopEncoder(self):
        GPIO.remove_event_detect(self.clockPin)
        GPIO.remove_event_detect(self.switchPin)
        GPIO.cleanup()
        

        
        
        
    
    