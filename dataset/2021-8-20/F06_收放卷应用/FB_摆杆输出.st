FUNCTION_BLOCK FB_摆杆输出
VAR_INPUT
	Enable:BOOL;
    摆臂的当前值:REAL;
    摆臂最小值:REAL;
    摆臂中间停止时最小值:REAL;
    摆臂中间停止时最大值:REAL;
    摆臂位置最大值:REAL;
    放卷的比例系数:REAL;
    收卷比例K值:REAL;
END_VAR
VAR_OUTPUT
	摆臂超过最大值报警:BOOL;
    放卷的输出值:REAL;
END_VAR
VAR
	正极片放卷值的变化:REAL;
    正极片临界值:DINT;
    摆臂收卷中间最大值:REAL;
    左边收卷区间:REAL;
    右边收卷区间:REAL;
END_VAR

IF Enable THEN
    摆臂收卷中间最大值:= (摆臂中间停止时最小值+摆臂最小值)/2;
	
    IF (摆臂的当前值<摆臂最小值) OR 摆臂的当前值<=0 THEN              
         放卷的输出值:=0;(*停止输出*) 
	
	      ELSIF (摆臂的当前值>=摆臂收卷中间最大值) AND (摆臂的当前值<摆臂中间停止时最小值) THEN
                  左边收卷区间:=摆臂中间停止时最小值-摆臂的当前值;
	              放卷的输出值:=左边收卷区间*收卷比例K值;  (*反转*)
	 
          ELSIF (摆臂的当前值<摆臂收卷中间最大值) AND (摆臂的当前值>摆臂最小值) THEN
	              右边收卷区间:=摆臂的当前值-摆臂最小值;
	              放卷的输出值:=右边收卷区间*收卷比例K值;  (*反转*)
    						  
	      ELSIF (摆臂中间停止时最小值<=摆臂的当前值) AND (摆臂的当前值<摆臂中间停止时最大值) THEN        
	              放卷的输出值:=0;  (*停止输出*)
							 
          ELSIF (摆臂中间停止时最大值<=摆臂的当前值) AND (摆臂的当前值<摆臂位置最大值) THEN
		          放卷的输出值:=(放卷的比例系数*(摆臂的当前值-摆臂中间停止时最大值));  (*正转输出*int_to_real(正极片值-470)*正极片放卷值的变化*)
         
          ELSIF 摆臂位置最大值<=摆臂的当前值 THEN 
			     摆臂超过最大值报警:=TRUE;
	       
	END_IF;
	
END_IF;