#ifndef _DEFAULTS_H
#define _DEFAULTS_H

// Timebase
#define TIME_BASE               20   // msec
#define TIME_SENSOR             100  // msec
#define TIME_SEND_CONFIGURATION 2000 // msec



//Respiraciones por minuto
#define MAX_RPM		30
#define MIN_RPM		2
#define DEF_RPM		15
//Volumen Corriente mL 
#define MAX_VOL 	2000
#define MIN_VOL 	50
//Presión máxima en cmH2O
#define MAX_PR		80
#define MIN_PR		1
// Presion Inspiratoria Pico en cmH2O
#define DEF_PIP		20
//Conversiones
#define DEF_PA_TO_CM_H2O 0.0102F

//I:E Ratio
enum IERatio
{
	1I_1E = 1,
	1I_2E = 2,
	1I_3E = 3,
	1I_4E = 4
};
//Alarmas
enum Alarm
{
	noAlarm = 0,
	pressMax = 1,
	pressMin = 2,
	noFlujo = 3
};

#endif // DEFAULTS_H