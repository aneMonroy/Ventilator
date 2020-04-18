#ifndef _VENTILATION_H
#define _VENTILATION_H

#include "defaults.h"
//---- States of mechanical ventilation ---------
enum ventilationState
{
	initInsufflation = 1,
	insufflation = 2, //Control of insufflation
	initExsufflation = 3,
	exsufflation = 4, // Return of position 0
	homeMotor = 0,
	errorState = -1
};

class Ventilation
{
	public:
	Ventilation();
	
	boolean startTriggeredPatient(); //
	void startVent(void); //
	void stopVent(void); //
	void updateVent(void); //
	
	
	uint8_t getRPM(void); //
	short getExsuflationTime(void); //
	short getInsuflationTime(void); //
	ventilationState getState(void); //
	
	void setRPM(uint8_t rpm); //
	void setState(ventilationState state);
	
	private:
	void _init();
	int _calculateInsuflationPosition(void);
	void _setAlarm(Alarm alarm);
	
	void _increaseInsuflationSpeed(byte factor);
	void _decreaseInsuflationSpeed(byte factor);
	void _increaseInsuflation(byte factor);
	void _decreaseInsuflation(byte factor);
	
	void _setInspiratoryCycle(void); //
	//Trigger por presión **Definir Valor
	float _triggerThreshold;
	//  Insufflation timeout in seconds. 
    unsigned short volatile _timeoutIns;
    // Exsufflation timeout in seconds. 
    unsigned short _timeoutEsp;
	// Breaths per minute 
    uint8_t _rpm;
	uint8_t _ieRatio;
	
	ventilationState _currentState = homeMotor;
	Alarm _currentAlarm = noAlarm;
	
	bool _running = false;
	bool _sensorError;
	bool _startTriggeredPatiend = false;
	float _currentPressure = 0.0;
	float _currentFlow = 0.0;
	float _currentVolume = 0.0;
};
	
#endif /* _VENTILATION_H */