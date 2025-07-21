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
from typing import Dict

load_dotenv()
autoplc_client_anthropic = Anthropic(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

autoplc_client_openai = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def read_directory_contents(directory: str) -> Dict[str, str]:
    """
    读取指定目录下的所有文件内容及其对应文件名
    
    参数:
        directory: 目录路径（字符串形式）
    
    返回:
        字典，键为文件路径（相对于指定目录），值为文件内容
    """
    result = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            result[relative_path] = content
    return result



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
    
def pre_func(dataset):          #从指定的目录下读取全部的文件
    dataset_path = r"D:\graduate_project\repo_case\2021-8-20-case"
    project_path = os.path.join(dataset_path, dataset)
    test_data = read_file(project_path)
    return test_data

def fill_fewshot(natural_language_requirement, scl_code):
    return f"""
    自然语言需求：{natural_language_requirement}

    代码：{scl_code}
    你需要根据自然语言需求生成能够为后续的代码生成提供指导的算法流程描述，并根据提供的代码流程进行适当调整。
    """ 


tem_sys_prompt = f"""
    你是一个ST项目需求逆向提取专家，你需要根据提供的prg，找到其引用的数据结构块(DUT)，以及使用到的全局变量(GVL)，以及很关键的：使用到的FB或者FUN块，结合prg的代码逻辑，逆向出一个需求。
    以下是ST项目结构的介绍：
    项目结构：
    -  前言：对于ST项目而言，它们的项目结构比较简单，往往几个文件就是一个完整的项目。下面将阐述具体的文件和对应的功能：
    -  文件与模块：
        - 数据结构与全局变量：  
            从一个项目自底向上的角度来看，项目的最底层是数据结构和全局变量。数据结构伴随着需求一起提供，它包含了这个项目需要用到的特定的数据结构。
            全局变量则是对项目中需要全局使用的一些变量的定义。例如，一个变量只需要在一个函数中使用，那它是一个局部变量应当定义在函数内部；如果它在多个流程中被使用，那么它就有必要被定义为一个全局变量。
        - 函数块(FB / FUN)：
            在 PLC 编程中，有函数块FB和函数FUN两个概念。
            Function Block (FB) 和Function (FUN) 的核心区别在于状态保持
            Function Block (FB) 有状态，内部变量可保存数据（如 PID 的积分项），需实例化（如myPID: FB_PID），适合需要记忆历史状态的控制逻辑（如 PID、计数器、状态机）；
            Function (FUN) 无状态，纯计算单元输入相同则输出相同，可直接调用（如result := SQRT(value)），适合确定性数学运算（如三角函数、数据转换）。选择原则：逻辑需依赖历史数据用 FB，固定算法用 FUN。
        - 程序块(PRG)：
            程序块是最上层的块，它们可以调用函数块和函数，不同的程序块之间还可以互相调用实现更复杂的功能。
"""
def project_struct_generate(dut_json, gvl_json, st_json, prg_json):
    code_messages = [{"role": "system", "content":tem_sys_prompt}]

    task_prompt = f"""
        以下为全部的DUT块,注意：只有一部分会被prg块使用到。
        {dut_json}
        以下为全部的GVL块,注意：只有一部分会被prg块使用到。
        {gvl_json}
        以下为全部的ST块,注意：只有一部分会被prg块使用到。
        {st_json}
        以下为prg块。请根据已知信息逆向出完整的关于prg的需求描述。
        {prg_json}    
    """

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
    print(response)
    return response



if __name__ == "__main__":
    dataset = "case1"
    dut_map = {}
    gvl_map = {}
    st_map = {}
    prg_map = {}
    dut_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\DUT"))
    gvl_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\GVL_FB103"))
    gvl_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\GVL_FB104"))
    st_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\F01_时钟脉冲"))
    st_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\F02_模拟滤波"))
    st_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\F03_气缸操作"))
    st_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\F04_轴控操作"))
    st_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\F05_系统操作"))
    st_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\F06_收放卷应用"))
    st_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\FB102"))
    prg_map.update(read_directory_contents(r"D:\graduate_project\repo_PLC_code_eval\dataset\2021-8-20\FB105_轴控制"))


    dut_json_array = [
        {"block_name": file_path, "content": content}
        for file_path, content in dut_map.items()
    ]
    gvl_json_array = [
        {"block_name": file_path, "content": content}
        for file_path, content in gvl_map.items()
    ]
    st_json_array = [
        {"block_name": file_path, "content": content}
        for file_path, content in st_map.items()
    ]
    prg_json_array = [
        {"block_name": file_path, "content": content}
        for file_path, content in prg_map.items()
    ]
    for prg_json in prg_json_array:
        project_struct_generate(dut_json_array, gvl_json_array, st_json_array, prg_json)
    # print(dut_map)



    # module_list = parse_modules(modules)
    # cont.modules = module_list
    # dut_blocks = data_structure_agent.module_generate(cont)
    # func_blocks = func_agent.module_generate(cont, dut_blocks)
    # program_blocks = program_agent.module_generate(cont, dut_blocks, func_blocks)