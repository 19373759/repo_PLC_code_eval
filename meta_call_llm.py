import prompt
# from autoplc_scl.agents.clients import (
#     autoplc_client_anthropic as client,
#     BASE_MODEL as model
# )
import sys
import json
import pytz
from datetime import datetime
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv
import os
from agents.data_agents import data_structure_agent
from agents.func_agents import func_agent
from agents.program_agents import program_agent
import dump_log

import context
import prompt
load_dotenv()
autoplc_client_anthropic = Anthropic(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

autoplc_client_openai = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def read_file(file_path):
    """
    Reads all JSON Lines files in a directory and returns a list of dictionaries.

    Parameters:
    file_path (str): The path to the directory containing JSON Lines files.

    Returns:
    list: A list of dictionaries representing the data in all files.
    """
    all_data = []
    print(file_path)
    for root, _, files in os.walk(file_path):
            print(file_path)
            for filename in files:
                file_full_path = os.path.join(root, filename)
                try:
                    # 读取单个文件并添加到结果列表
                    with open(file_full_path, 'r', encoding='utf-8') as f:
                        # 逐行解析 JSON Lines
                        data = f.read()
                        all_data.append({
        "filename": filename,
        "data": data
    })
                except Exception as e:
                    print(f"Error reading {file_full_path}: {e}")
    # print(all_data)
    return all_data
    

def fill_fewshot(natural_language_requirement, scl_code):
    return f"""
    自然语言需求：{natural_language_requirement}

    代码：{scl_code}
    你需要根据自然语言需求生成能够为后续的代码生成提供指导的算法流程描述，并根据提供的代码流程进行适当调整。
    """    
def project_struct_generate(common_context):
    code_messages = [{"role": "system", "content":prompt.struct_make_prompt}]

    files = common_context.files
    names = common_context.names
    names = ['FB_轴停止触发块', 'FB_轴控制块']
#     task_prompt = f"""
#     已知的项目文件内容：{files}
#     缺少的项目文件内容：{names}
#     你需要根据自然语言需求和提供的数据结构用形式化语言描述项目的依赖关系图谱，要从实际内容出发。如果你发现有个变量其类型没有在其他文件中给出，那么它就是一个缺失的依赖，你需要同样写在dependencies中。
#     参考格式：
#     {{
#         "module": "DUT_Motor",
#         "dependencies": {{
#             None
#         }}, 
#         "module": "FB_extractor",
#         "dependencies": {{
#             "DUT_Motor"
#         }},
#         "module": "FB_controller",
#         "dependencies": {{
#             "DUT_Motor",
#             "FB_extractor"
#         }},
#         "module": "PRG_main",
#         "dependencies": {{
#             "DUT_Motor",
#             "FB_extractor",
#             "FB_controller"
#         }}
#     }}
#     项目结构：
#     -  前言：对于ST项目而言，它们的项目结构比较简单，往往几个文件就是一个完整的项目。下面将阐述具体的文件和对应的功能：
#     -  文件与模块：
#         - 数据结构与全局变量：  
#             从一个项目自底向上的角度来看，项目的最底层是数据结构和全局变量。数据结构伴随着需求一起提供，它包含了这个项目需要用到的特定的数据结构。
#             全局变量则是对项目中需要全局使用的一些变量的定义。例如，一个变量只需要在一个函数中使用，那它是一个局部变量应当定义在函数内部；如果它在多个流程中被使用，那么它就有必要被定义为一个全局变量。
#         - 函数块(FB / FUN)：
#             在 PLC 编程中，有函数块FB和函数FUN两个概念。
#             Function Block (FB) 和Function (FUN) 的核心区别在于状态保持
#             Function Block (FB) 有状态，内部变量可保存数据（如 PID 的积分项），需实例化（如myPID: FB_PID），适合需要记忆历史状态的控制逻辑（如 PID、计数器、状态机）；
#             Function (FUN) 无状态，纯计算单元输入相同则输出相同，可直接调用（如result := SQRT(value)），适合确定性数学运算（如三角函数、数据转换）。选择原则：逻辑需依赖历史数据用 FB，固定算法用 FUN。
#         - 程序块(PRG)：
#             程序块是最上层的块，它们可以调用函数块和函数，不同的程序块之间还可以互相调用实现更复杂的功能。
# """
    task_prompt = f"""
    #     已知的项目文件内容：{files}
    #     缺少的项目文件内容：{names}
    #     你需要根据自然语言需求和提供的数据结构用形式化语言描述项目的依赖关系图谱，要从实际内容出发。如果你发现有个变量其类型没有在其他文件中给出，那么它就是一个缺失的依赖，你需要同样写在dependencies中。
    #     参考格式：
    #     {{
    #         "module": "DUT_Motor",
    #         "dependencies": {{
    #             None
    #         }}, 
    #         "module": "FB_extractor",
    #         "dependencies": {{
    #             "DUT_Motor"
    #         }},
    #         "module": "FB_controller",
    #         "dependencies": {{
    #             "DUT_Motor",
    #             "FB_extractor"
    #         }},
    #         "module": "PRG_main",
    #         "dependencies": {{
    #             "DUT_Motor",
    #             "FB_extractor",
    #             "FB_controller"
    #         }}
    #     }}
    #     项目结构：
    #     -  前言：对于ST项目而言，它们的项目结构比较简单，往往几个文件就是一个完整的项目。下面将阐述具体的文件和对应的功能：
    #     -  文件与模块：
    #         - 数据结构与全局变量：  
    #             从一个项目自底向上的角度来看，项目的最底层是数据结构和全局变量。数据结构伴随着需求一起提供，它包含了这个项目需要用到的特定的数据结构。
    #             全局变量则是对项目中需要全局使用的一些变量的定义。例如，一个变量只需要在一个函数中使用，那它是一个局部变量应当定义在函数内部；如果它在多个流程中被使用，那么它就有必要被定义为一个全局变量。
    #         - 函数块(FB / FUN)：
    #             在 PLC 编程中，有函数块FB和函数FUN两个概念。
    #             Function Block (FB) 和Function (FUN) 的核心区别在于状态保持
    #             Function Block (FB) 有状态，内部变量可保存数据（如 PID 的积分项），需实例化（如myPID: FB_PID），适合需要记忆历史状态的控制逻辑（如 PID、计数器、状态机）；
    #             Function (FUN) 无状态，纯计算单元输入相同则输出相同，可直接调用（如result := SQRT(value)），适合确定性数学运算（如三角函数、数据转换）。选择原则：逻辑需依赖历史数据用 FB，固定算法用 FUN。
    #         - 程序块(PRG)：
    #             程序块是最上层的块，它们可以调用函数块和函数，不同的程序块之间还可以互相调用实现更复杂的功能。
    # """
    
    code_messages.append({"role": "user", "content": task_prompt})

    #测试不同模型的生成效果
    model = "deepseek-chat"

    response = autoplc_client_anthropic.messages.create(
        model=model,  
        max_tokens=16*1024,
        temperature=0.1,
        top_p=0.9,
        messages=code_messages,
    )
    code_messages.append({"role": "assistant", "content":response.choices[0]['message']['content']})
    # print(code_messages)
    str1 = code_messages

    response = response.choices[0]['message']['content']
    # print(response)
    return response

def is_st_machine(requirement_content):
    code_messages = [{"role": "system", "content":plan_gen_prompt.is_state_machine}]
    code_messages.append({"role": "user", "content": requirement_content})
    model = "gpt-4o-mini"
    response = autoplc_client_anthropic.messages.create(
        model=model,  
        max_tokens=16*1024,
        temperature=0.1,
        top_p=0.9,
        messages=code_messages,
    )    # print(code_messages)

    response = response.choices[0]['message']['content']
    return response


def baseline_github(input_model, requirement_content):
    code_messages = [{"role": "system", "content":plan_gen_prompt.baseline_githubCase}]
    code_messages.append({"role": "user", "content": requirement_content})
    model = input_model
    response = autoplc_client_anthropic.messages.create(
        model=model,  
        max_tokens=16*1024,
        temperature=0.1,
        top_p=0.9,
        messages=code_messages,
    )    # print(code_messages)

    response = response.choices[0]['message']['content']
    return response


def figure_state_machine_in_lgf(dataset_file):
    with open(dataset_file, 'r', encoding='utf-8') as f:
        for line in f:
            json_data = json.loads(line.strip())
            st_res = is_st_machine(line)
            print(json_data['name'], st_res + " ")

def run_baseline_in_github_case(model, dataset_file):
    with open(dataset_file, 'r', encoding='utf-8') as f:
        for line in f:
            json_data = json.loads(line.strip())
            st_res = baseline_github(model, line)
            print(json_data['name'], st_res + " ")

def pre_func(dataset):          #从指定的目录下读取全部的文件
    dataset_path = r"D:\graduate_project\repo_case\2021-8-20-case"
    project_path = os.path.join(dataset_path, dataset)
    test_data = read_file(project_path)
    return test_data

def build_context(all_data):

# 原始JSON字符串（注意：实际使用时需确保字符串格式正确）
    ctx = context.CommonContext()
    ctx.files = all_data
    return ctx

def parse_modules(text):
    """
    解析文本中的模块标签内容，处理四种已知标签和未知标签
    
    参数:
    text (str): 包含模块标签的文本
    
    返回:
    dict: 包含四种模块内容和错误信息的字典
    """
    # 初始化结果列表和错误记录
    struct_modules = []
    fb_modules = []
    fun_modules = []
    prg_modules = []
    unknown_modules = []
    errors = []
    
    # 当前处理的模块类型和内容
    current_module_type = None
    current_content = []
    line_number = 0
    
    # 标签类型映射
    module_types = {
        '<struct_module>': struct_modules,
        '<FB_module>': fb_modules,
        '<FUN_module>': fun_modules,
        '<PRG_module>': prg_modules
    }
    
    # 行处理
    lines = text.split('\n')
    for line in lines:
        line_number += 1
        stripped_line = line.strip()
        
        # 检查是否为开始标签
        if stripped_line.startswith('<') and stripped_line.endswith('>'):
            if stripped_line in module_types:
                # 已知标签开始
                if current_module_type:
                    errors.append(f"行 {line_number}: 发现新标签 {stripped_line}，但上一个标签 {current_module_type} 未结束")
                    # 保存不完整的内容到错误模块
                    content = '\n'.join(current_content).strip('"')
                    unknown_modules.append({
                        'tag': current_module_type,
                        'content': content,
                        'error': '未找到结束标签'
                    })
                current_module_type = stripped_line
                current_content = []
            elif stripped_line == '<module_end>':
                # 结束标签
                if not current_module_type:
                    errors.append(f"行 {line_number}: 发现结束标签，但没有对应的开始标签")
                else:
                    if current_content:
                        # 合并内容并移除首尾引号
                        content = '\n'.join(current_content).strip('"')
                        module_types[current_module_type].append(content)
                    current_module_type = None
                    current_content = []
            else:
                # 未知标签
                errors.append(f"行 {line_number}: 未知标签 {stripped_line}")
                if current_module_type:
                    # 保存不完整的内容到错误模块
                    content = '\n'.join(current_content).strip('"')
                    unknown_modules.append({
                        'tag': current_module_type,
                        'content': content,
                        'error': f"被未知标签 {stripped_line} 中断"
                    })
                current_module_type = stripped_line
                current_content = []
        else:
            # 普通内容行
            if current_module_type:
                current_content.append(line)
    
    # 检查是否有未结束的标签
    if current_module_type:
        errors.append(f"行 {line_number}: 标签 {current_module_type} 未找到结束标签")
        content = '\n'.join(current_content).strip('"')
        unknown_modules.append({
            'tag': current_module_type,
            'content': content,
            'error': '未找到结束标签'
        })
    
    return {
        'struct_modules': struct_modules,
        'fb_modules': fb_modules,
        'fun_modules': fun_modules,
        'prg_modules': prg_modules,
        'unknown_modules': unknown_modules,
        'errors': errors
    }

if __name__ == "__main__":
    dataset = "case1"
    all_data = pre_func(dataset)
    cont = build_context(all_data)

    modules = project_struct_generate(cont)  #生成项目结构
    print(modules)
    # module_list = parse_modules(modules)
    # cont.modules = module_list
    # dut_blocks = data_structure_agent.module_generate(cont)
    # func_blocks = func_agent.module_generate(cont, dut_blocks)
    # program_blocks = program_agent.module_generate(cont, dut_blocks, func_blocks)