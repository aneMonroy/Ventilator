#include "ventilation.h"


boolean Ventilation::startTriggeredPatient()
{
	if(_startTriggeredPatient)
		return true;
	else
		return false;
}

void Ventilation::startVent(void)
{
	_running = true;
}

void Ventilation::stopVent(void)
{
	_running = false;
	
}

uint8_t Ventilation::getRPM(void)
{
	return _rpm;
}

short Ventilation::getExsuflationTime(void)
{
    return _timeoutEsp;
}
short Ventilation::getInsuflationTime(void)
{
    return _timeoutIns;
}

ventilationState Ventilation::getState(void)
{
	return _currentState;
}

void Ventilation::setRPM(uint8_t rpm)
{
    _rpm = rpm;
    _setInspiratoryCycle();
}

void MechVentilation::_setInspiratoryCycle(void)
{
    float timeoutCycle = ((float)60) * 1000 / ((float)_rpm); // Tiempo de ciclo en msegundos
    _timeoutIns = timeoutCycle / (_ieRatio+1);
    _timeoutEsp = _timeoutIns * _ieRatio;
}

void Ventilation::updateVent(void)
{
	static int totalCyclesInThisState = 0;
    static int currentTime = 0;
    static int flowSetpoint = 0;
	//_currentPressure = pressure.pressure1;
	//_currentVolume = volume.volume;
	//_currentFlow = flow.flow;
	/*if(pressure.state != stateOK)
	{
		_sensorError = true;
		Serial.println("PR ERR");
		setState(exsufflation);
	}*/
	//evaluatePressure();
	//refreshWatchDogTimer();
	switch(_currentState)
	{
		case initInsufflation:
		{
			//_sensors->resetVolume();
			totalCyclesInThisState = _timeoutIns / TIME_BASE;
			//Set MotorControl
			/* acceleration, speed and position*/
			setState(insufflation);
			currentTime=0;
		}break;
		
		case insufflation:
		{
			if(currentTime > totalCyclesInThisState)
			{
				//If motor doesnt get to position stopVent
				setState(initExsufflation);
				currentTime=0;
			}
			else
			{ 
				//Motor control HERE
				currentTime++;
			}
		}break;
		
		case initExsufflation:
		{
			totalCyclesInThisState = _timeoutEsp / TIME_BASE;
			//_sensors->saveVolume();
			//_sensors->resetVolumeIntegrator();
			
			//Motor set speed/acc/position
			
			setState(exsufflation);
			currentTime=0;
		}break;
		
		case exsufflation:
		{ 
			//If motor doesnt get to position stopVent
			/*
			if(currentPress < _triggerThreshold)
			{
				_startTriggeredPatient=true;
				setState(initInsufflation);
			}*/
			if(currentTime > totalCyclesInThisState)
			{
				//If motor doesnt get to position stopVent
				
				setState(initInsufflation);
				_startTriggeredPatient = false;
				currentTime=0;
			}
			else
			{
				//Motor control to return to position 0
				currentTime++;
			}
		}break;
		
		case homeMotor:
		{
			if(_sensorError)
			{
				_running = false;
				Serial.println("SR ERR");
			}
			//Motor control to set position home
			currentTime = 0;
			setState(initExsufflation);
		}break;
		
		case errorState:
		{
			Serial.println("SR ERR");
		}break;
		
		default:
		{
			//TODO
		}break;
	}
}

void Ventilation::setState(ventilationState state)
{
    _currentState = state;
}

void Ventilation::_setAlarm(Alarm alarm)
{
    _currentAlarm = alarm;
}
			
			
			
		
				
			
			
	