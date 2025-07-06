import prompt
# from autoplc_scl.agents.clients import (
#     autoplc_client_anthropic as client,
#     BASE_MODEL as model
# )
import json
import pytz
from datetime import datetime
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv
import os

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

def read_jsonl(file_path):
    """
    Reads a JSON Lines file and returns a list of dictionaries.

    Parameters:
    file_path (str): The path to the JSON Lines file.

    Returns:
    list: A list of dictionaries representing the data in the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]
    

def fill_fewshot(natural_language_requirement, scl_code):
    return f"""
    自然语言需求：{natural_language_requirement}

    代码：{scl_code}
    你需要根据自然语言需求生成能够为后续的代码生成提供指导的算法流程描述，并根据提供的代码流程进行适当调整。
    """    
def program_generate(common_context, prg_module , dut_blocks, fbfun_blocks):
    code_messages = [{"role": "system", "content":system_prompt}]

    natural_language_requirement = prg_module

    task_prompt = f"""
    自然语言需求：{natural_language_requirement}
    数据结构：{dut_blocks}
    可能需要使用到的FB/FUN块：{fbfun_blocks}
    请生成需求对应的PRG块。注意：你要把PRG块以如下的形式呈现：
    <dut_code>
        "你的实现"
    <code_end>
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

    response = response.choices[0]['message']['content']
    dut_block = extract_dut_code(response)
    return dut_block

def extract_dut_code(text):
    """
    提取文本中第一个<dut_code>到<code_end>标签之间的内容
    
    参数:
    text (str): 包含标签的文本
    
    返回:
    str: 标签内的内容（不含标签），如果未找到标签对则返回空字符串
    """
    start_tag = "<dut_code>"
    end_tag = "<code_end>"
    
    # 查找起始标签位置
    start_index = text.find(start_tag)
    if start_index == -1:
        return ""  # 未找到起始标签
    
    # 从起始标签后开始查找结束标签
    start_after_tag = start_index + len(start_tag)
    end_index = text.find(end_tag, start_after_tag)
    if end_index == -1:
        return ""  # 未找到结束标签
    
    # 提取标签间的内容
    content = text[start_after_tag:end_index].strip()
    return content
def module_generate(common_context, dut_blocks, func_blocks):
    modules = common_context.modules
    prg_modules = modules["prg_modules"]

    prg_blocks = []
    for prg_module in prg_modules:
        prg_blocks.append(program_generate(common_context, prg_module, dut_blocks, func_blocks))
    for block in prg_blocks:
        print(prg_blocks)
    return prg_blocks

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

def pre_func(dataset):
    dataset_path = f"./mission/"
    test_data = read_jsonl(dataset_path + f"{dataset}.jsonl")
    return test_data

def build_context(data):
    import json

# 原始JSON字符串（注意：实际使用时需确保字符串格式正确）

    for json_str in data:
        try:
            ctx = context.CommonContext()
            # 提取各字段
            title = json_str.get('title', '')
            description = json_str.get('description', '')
            data_struct = json_str.get('data_struct', '')
            
            ctx._requirement = description
            ctx._data_structure  = data_struct
            
            # 如需进一步处理description或data_struct，可以在这里进行
            # 例如：解析data_struct中的结构体字段
            return ctx
                
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
        except Exception as e:
            print(f"其他错误: {e}")

system_prompt = f"""
你是一个ST领域的程序块(PRG)编写工程师，擅长根据提供的需求和数据结构块，定义实现PRG块。PRG块是CODESYS中的一个概念，你可以理解为PLC领域中具体调用FB/FUN的块。下面是具体介绍：
程序块(PRG)：
在 PLC 编程中，对于FB/FUN块，想要调用他们，需要通过程序块对他们进行调用。其形式像是传统编程语言中函数的调用方式。
你要根据提供的需求给出完整的PRG块的实现。
"""