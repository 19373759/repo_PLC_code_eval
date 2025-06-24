from autoplc_scl.prompts import plan_gen_prompt
from config import Config
# from autoplc_scl.agents.clients import (
#     autoplc_client_anthropic as client,
#     BASE_MODEL as model
# )
import json
import pytz
from datetime import datetime
from autoplc_scl.agents.clients import LLMClient, autoplc_client_anthropic
from dotenv import load_dotenv
import os
from utils import PromptResultUtil


def fill_fewshot(natural_language_requirement, scl_code):
    return f"""
    自然语言需求：{natural_language_requirement}

    代码：{scl_code}
    你需要根据自然语言需求生成能够为后续的代码生成提供指导的算法流程描述，并根据提供的代码流程进行适当调整。
    """    

def plan_gen(current_task_requirement, current_task_code):
    
    code_messages = [{"role": "system", "content":plan_gen_prompt.system_prompt_state_machine}]
    
    # fewshot_context1 = fill_fewshot(plan_gen_prompt.fewshot_prompt_req_1, plan_gen_prompt.fewshot_prompt_code_1)
    # code_messages.append({"role": "user", "content": fewshot_context1})
    # code_messages.append({"role": "assistant", "content": plan_gen_prompt.fewshot_prompt_plan_1})

    natural_language_requirement = current_task_requirement
    scl_code = current_task_code

    task_prompt = f"""
    自然语言需求：{natural_language_requirement}

    代码：{scl_code}
    你需要根据自然语言需求生成能够为后续的代码生成提供指导的算法流程描述，并根据提供的代码流程进行适当调整。
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
    str1 = PromptResultUtil.message_to_file_str(code_messages)
    print(str1)

    response = response.choices[0]['message']['content']
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


def gen_plan_dataset(case_requirement_dir, case_code_dir, case_plan_dir):
    """
    根据用例需求和代码生成计划数据集。

    遍历需求目录下的所有文件，读取每个需求文件的内容，并尝试读取对应代码文件的内容（如果存在），
    然后将两者作为输入生成一个计划，并将该计划写入计划目录下的相应文件中。

    参数:
    case_requirement_dir (str): 用例需求文件所在的目录路径。
    case_code_dir (str): 用例代码文件所在的目录路径。
    case_plan_dir (str): 生成的计划文件将要存放的目录路径。
    """
    #创建一个关于时间戳的文件夹
    tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(tz)
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")

    base_folder = os.path.join(
        case_plan_dir, f"{date_folder}_{time_folder}"
    )
    print(base_folder)
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    # 遍历需求目录及其子目录
    for root, dirs, files in os.walk(case_requirement_dir):
        files.sort()
        for file in files:
            # 构建需求文件的完整路径
            requirement_file_path = os.path.join(root, file)

            # 读取第一个目录下文件的内容
            with open(requirement_file_path, 'r', encoding='utf-8') as req_file:
                requirement_content = req_file.read()
            # 获取文件名（不带后缀）
            base_name = os.path.splitext(file)[0]
            # 构建对应的.scl文件名
            scl_file_name = base_name + '.scl'
            print(scl_file_name)

            # 构建第二个目录中对应的文件路径
            code_file_path = os.path.join(case_code_dir, scl_file_name)
            # 检查对应的代码文件是否存在
            if os.path.exists(code_file_path):
                # 读取第二个目录下对应文件的内容
                with open(code_file_path, 'r', encoding='utf-8') as code_file:
                    code_content = code_file.read()
            else:
                # 如果未找到对应的代码文件，打印提示信息并设置code_content为空字符串
                print(f"在 {case_code_dir} 中未找到对应的文件: {file}")
                code_content = ""

            # 根据需求内容和代码内容生成计划
            case_plan = plan_gen(requirement_content, code_content)
            
            # 将生成的计划内容写入计划文件
            # 构建计划文件名和路径
            plan_file_name = base_name + '.plan'
            plan_file_path = os.path.join(base_folder, plan_file_name)
            with open(plan_file_path, 'w', encoding='utf-8') as plan_file:
                plan_file.write(case_plan)

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
    