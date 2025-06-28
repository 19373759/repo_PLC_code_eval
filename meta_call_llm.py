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
def project_struct_generate(common_context):
    code_messages = [{"role": "system", "content":prompt.design_system_prompt}]

    natural_language_requirement = common_context.requirement
    data_struct = common_context._data_structure
    task_prompt = f"""
    自然语言需求：{natural_language_requirement}
    数据结构：{data_struct}
    你需要根据自然语言需求和提供的数据结构用形式化语言描述项目结构。
    """

    task_prompt = f"""
    自然语言需求：{natural_language_requirement}
    数据结构：{data_struct}
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

    你要严格遵循我给出的项目结构原则来设计，并将每个模块的需求描述详细写在每个模块内，以如下的形式给出：
    <module>
        "你对此模块的功能和需求描述"
    <module_end>
    <module>
        "你对此模块的功能和需求描述"
    <module_end>
    <module>
        "你对此模块的功能和需求描述"
    <module_end>
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

if __name__ == "__main__":
    dataset = "task"
    data = pre_func(dataset)
    cont = build_context(data)
    project_struct_generate(cont)
    
    # project_struct_generate(data)
    # project_struct_generate(dataset)      #首先生成项目结构