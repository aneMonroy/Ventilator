from RPi_GPIO_Rotary import rotary

## Define Callback functions
def cwTurn():
    print("CW Turn")

def ccwTurn():
    print("CCW Turn")

def buttonPushed():
    print("Button Pushed")

def valueChanged(count):
    print(count) ## Current Counter value

## Initialise (clk, dt, sw, ticks)
obj = rotary.Rotary(5,6,13,2)

 ## Register callbacks
obj.register(increment=cwTurn, decrement=ccwTurn)

## Register more callbacks
obj.register(pressed=buttonPushed, onchange=valueChanged) 

## Start monitoring the encoder
obj.start()