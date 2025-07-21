FUNCTION_BLOCK FB_气缸操作块
VAR_INPUT
	CheckTime: TIME := T#3S;
	OpenSensor: BOOL;
	CloseSensor: BOOL;
	
	OpenSensorCheck: BOOL;
	CloseSensorCheck: BOOL;
	
	OpenDelayTime: REAL;
	CloseDelayTime: REAL;
	
	Cylinder: BOOL;
END_VAR


VAR_OUTPUT
	Q_CylinderError1: BOOL;
	Q_CylinderError2: BOOL;
	OpenDelay: BOOL;
	CloseDelay: BOOL;
END_VAR
VAR
	Delay1: TON;
	Delay2: TON;
	TON0: TON;
	TON1: TON;
END_VAR
