import os
import time
from datetime import datetime

class dump_log:

    def __init__(self):
        self.dump_dir = ""
    def dumplog_init(self, log_name, output_dir="output"):
        """
        初始化日志系统，创建时间戳目录和日志文件
        
        参数:
        log_name (str): 日志文件名（不包含扩展名）
        output_dir (str): 输出目录，默认为"output"
        
        返回:
        str: 日志文件的完整路径，便于后续写入
        """
        try:
            # 获取当前时间戳并格式化为目录名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamp_dir = os.path.join(output_dir, timestamp)
            self.dump_dir = timestamp_dir
            
            # 创建时间戳目录
            os.makedirs( self.dump_dir)
            
            # 构建日志文件路径
            log_file = os.path.join(timestamp_dir, f"{log_name}.txt")
            
            # 创建日志文件（如果不存在）
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"# 日志创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("#" * 50 + "\n\n")  # 分隔线
            
            print(f"日志系统初始化完成，日志文件: {log_file}")
            return log_file
        
        except Exception as e:
            print(f"初始化日志系统失败: {str(e)}")
            return None

    def dumplog_append(self, log_name, content):
        """
        向日志文件追加内容，每次添加空两行
        
        参数:
        log_file (str): 日志文件路径
        content (str): 要追加的内容
        
        返回:
        bool: 追加是否成功
        """
        log_file =  os.path.join(self.dump_dir, f"{log_name}.txt")

        if not log_file or not os.path.exists(log_file):
            print("错误: 无效的日志文件路径")
            return False
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write("\n\n")  # 空两行
                f.write(content)
                f.write("\n")  # 确保内容以换行结尾
            return True
        except Exception as e:
            print(f"追加日志失败: {str(e)}")
            return False
        
    