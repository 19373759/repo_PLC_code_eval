FUNCTION_BLOCK FB_轴停止触发块
VAR_IN_OUT
	StopExcute: BOOL;
END_VAR
VAR
	TON0: TON;
END_VAR


TON0(IN:= StopExcute, PT:= T#0.3S, Q=> , ET=> );

IF TON0.Q THEN
	StopExcute:=FALSE;
END_IF


