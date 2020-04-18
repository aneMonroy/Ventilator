#include "calculations.h"

long volume2pos(int volume)
{
//Change formula to fit (50mL or 100mL increments)
 float x=volume/100.0; 
 return (long(100*( ((-1.0/20) * x * x)  +((27.0/20) * x) +3.0/2)));
}
