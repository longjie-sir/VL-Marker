import os
import time
import dashscope
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化DashScope
api_key = os.getenv('DASHSCOPE_API_KEY')
if api_key:
    dashscope.api_key = api_key
else:
    print("警告: 未设置DASHSCOPE_API_KEY环境变量")

def get_prompt(rule_type: str) -> str:
    """根据规则类型生成Prompt"""
    if rule_type == "in_bounds":
        area_desc = "合法停车/行驶区域"
        violation_desc = "超出了红线范围（完全在红线外或压线均算越界）"
    else:  # no_entry
        area_desc = "禁止进入区域"
        violation_desc = "进入了红线范围"
    
    prompt = f"你是一个严肃的安防监控AI。图中已用**红色粗线条**画出了一个【{area_desc}】。请仔细观察图中是否有任何车辆（如轿车、货车等）的车身或轮胎**{violation_desc}**。请严格以 JSON 格式输出，包含字段：`has_violation` (布尔值) 和 `reason` (不超过30字的中文理由)。"
    
    return prompt

def call_qwen_vl(image_base64: str, prompt: str) -> Dict[str, Any]:
    """调用Qwen-VL模型进行违规检测"""
    start_time = time.time()
    
    try:
        # 使用传入的prompt
        
        # 确保base64字符串不包含任何换行符或空格
        image_base64 = image_base64.strip()
        
        # 调用模型 - 使用更简单的格式
        # print(f"开始调用模型，prompt长度: {len(prompt)}")
        # print(f"图片Base64长度: {len(image_base64)} 字符")
        
        # 确保API Key已设置
        if not dashscope.api_key:
            print("API Key未设置")
            return {
                "has_violation": False,
                "violation_desc": "API Key未设置",
                "model_latency_ms": int((time.time() - start_time) * 1000)
            }
        
        try:
            response = dashscope.MultiModalConversation.call(
                model="qwen3-vl-flash",
                messages=[
                    {
                        "role": "user",
                        "content":[
                            {"image": f"data:image/jpeg;base64,{image_base64}"},
                            {"text": f"{prompt}"}
                        ] 
                    }
                ],
                extra_body={"enable_thinking":False},
                result_format="message"
            )
        except Exception as api_error:
            print(f"API调用异常: {str(api_error)}")
            return {
                "has_violation": False,
                "violation_desc": f"API调用异常: {str(api_error)}",
                "model_latency_ms": int((time.time() - start_time) * 1000)
            }
        
        # print(f"模型响应状态码: {response.status_code}")
        # print(f"模型响应: {response}")
        
        # 计算模型延迟
        model_latency_ms = int((time.time() - start_time) * 1000)
        
        # 解析响应
        if response.status_code == 200:
            # 提取模型输出
            try:
                # 检查响应结构
                if not hasattr(response, 'output'):
                    print("响应中没有output属性")
                    return {
                        "has_violation": False,
                        "violation_desc": "响应中没有output属性",
                        "model_latency_ms": model_latency_ms
                    }
                
                if not hasattr(response.output, 'choices'):
                    print("响应output中没有choices属性")
                    return {
                        "has_violation": False,
                        "violation_desc": "响应output中没有choices属性",
                        "model_latency_ms": model_latency_ms
                    }
                
                if len(response.output.choices) == 0:
                    print("响应choices为空")
                    return {
                        "has_violation": False,
                        "violation_desc": "响应choices为空",
                        "model_latency_ms": model_latency_ms
                    }
                
                choice = response.output.choices[0]
                if not hasattr(choice, 'message'):
                    print("响应choice中没有message属性")
                    return {
                        "has_violation": False,
                        "violation_desc": "响应choice中没有message属性",
                        "model_latency_ms": model_latency_ms
                    }
                
                message = choice.message
                if not hasattr(message, 'content'):
                    print("响应message中没有content属性")
                    return {
                        "has_violation": False,
                        "violation_desc": "响应message中没有content属性",
                        "model_latency_ms": model_latency_ms
                    }
                
                content = message.content
                # print(f"content类型: {type(content)}")
                # print(f"content值: {content}")
                # print(f"content长度: {len(str(content))}")
                
                # 检查content的结构
                if isinstance(content, list):
                    # 找到text类型的内容
                    model_output = ""
                    # print(f"content是列表，长度: {len(content)}")
                    for i, item in enumerate(content):
                        # print(f"列表项{i}类型: {type(item)}")
                        # print(f"列表项{i}值: {item}")
                        if isinstance(item, dict):
                            # print(f"列表项{i}是字典，键: {list(item.keys())}")
                            if item.get('type') == 'text':
                                model_output = item.get('text', '')
                                print(f"找到text类型的内容: {model_output}")
                                break
                        elif hasattr(item, 'text'):
                            model_output = item.text
                            # print(f"找到带text属性的内容: {model_output}")
                            break
                    if not model_output:
                        # 如果没有找到text类型的内容，尝试直接获取
                        model_output = str(content)
                        # print(f"没有找到text类型的内容，使用str(content): {model_output}")
                elif hasattr(content, 'text'):
                    model_output = content.text
                    # print(f"content有text属性: {model_output}")
                else:
                    model_output = str(content)
                    # print(f"content 是其他类型，使用str(content): {model_output}")
                
                # print(f"最终model_output: {model_output}")
                # print(f"最终model_output长度: {len(model_output)}")
                
                # 解析JSON格式的输出
                import json
                import ast
                import re
                try:
                    #print(f"原始model_output: {model_output}")
                    #print(f"model_output类型: {type(model_output)}")
                    
                    # 处理空输出
                    if not model_output:
                        print("模型返回空内容")
                        return {
                            "has_violation": False,
                            "violation_desc": "模型返回空内容",
                            "model_latency_ms": model_latency_ms
                        }
                    
                    # 处理字符串类型的model_output
                    if isinstance(model_output, str):
                        # 尝试解析为列表
                        parsed_list = None
                        try:
                            parsed_list = ast.literal_eval(model_output)
                            print(f"成功解析为列表: {type(parsed_list)}")
                        except Exception as e:
                            print(f"解析列表失败: {str(e)}")
                        
                        # 如果解析成功，尝试提取text字段
                        if isinstance(parsed_list, list) and len(parsed_list) > 0:
                            first_item = parsed_list[0]
                            if isinstance(first_item, dict) and 'text' in first_item:
                                print("从列表中提取text字段")
                                model_output = first_item['text']
                                print(f"提取后的text内容: {model_output[:200]}...")
                        
                        # 尝试提取JSON代码块
                        #print(f"处理前的model_output: {model_output[:200]}...")
                        # 尝试多种格式的代码块提取
                        json_match = re.search(r'```json\n(.*?)\n```', model_output, re.DOTALL)
                        if json_match:
                            model_output = json_match.group(1).strip()
                            #print(f"提取JSON代码块后: {model_output}")
                        # 尝试提取普通代码块
                        elif model_output.startswith('```json') and model_output.endswith('```'):
                            model_output = model_output[7:-3].strip()
                            #print(f"移除JSON代码块后: {model_output}")
                        elif model_output.startswith('```') and model_output.endswith('```'):
                            model_output = model_output[3:-3].strip()
                            #print(f"移除代码块后: {model_output}")
                        # 尝试提取没有代码块标记的JSON
                        elif '{' in model_output and '}' in model_output:
                            # 尝试找到第一个{和最后一个}之间的内容
                            start_idx = model_output.find('{')
                            end_idx = model_output.rfind('}')
                            if start_idx < end_idx:
                                model_output = model_output[start_idx:end_idx+1].strip()
                                #print(f"提取无代码块标记的JSON: {model_output}")
                        #print(f"处理后的model_output: {model_output}")
                    
                    # 再次检查空输出
                    if not model_output:
                        #print("处理后内容为空")
                        return {
                            "has_violation": False,
                            "violation_desc": "处理后内容为空",
                            "model_latency_ms": model_latency_ms
                        }
                    
                    # 尝试解析JSON
                    try:
                        result = json.loads(model_output)
                        #print(f"解析后的JSON: {result}")
                        
                        # 检查result结构
                        if not isinstance(result, dict):
                            print("解析结果不是字典")
                            return {
                                "has_violation": False,
                                "violation_desc": "解析结果不是字典",
                                "model_latency_ms": model_latency_ms
                            }
                        
                        return {
                            "has_violation": result.get("has_violation", result.get("result", False)),
                            "violation_desc": result.get("reason", result.get("message", "")),
                            "model_latency_ms": model_latency_ms
                        }
                    except json.JSONDecodeError as json_error:
                        print(f"JSON解析错误: {str(json_error)}")
                        print(f"尝试解析的内容: {model_output}")
                        
                        # 尝试清理JSON字符串
                        try:
                            # 移除可能的无效字符
                            clean_json = model_output.strip()
                            # 尝试处理单引号
                            clean_json = clean_json.replace("'", '"')
                            # 尝试处理没有引号的键
                            clean_json = re.sub(r'(\w+)\s*:', r'"\1":', clean_json)
                            # 尝试处理多余的逗号
                            clean_json = re.sub(r',\s*}', '}', clean_json)
                            clean_json = re.sub(r',\s*\]', ']', clean_json)
                            
                            print(f"清理后的JSON: {clean_json}")
                            result = json.loads(clean_json)
                            print(f"清理后解析成功: {result}")
                            if isinstance(result, dict):
                                return {
                                    "has_violation": result.get("has_violation", result.get("result", False)),
                                    "violation_desc": result.get("reason", result.get("message", "")),
                                    "model_latency_ms": model_latency_ms
                                }
                        except Exception as clean_error:
                            print(f"清理JSON失败: {str(clean_error)}")
                        
                        # 尝试直接从原始文本中提取JSON
                        try:
                            # 再次尝试提取JSON代码块
                            json_match = re.search(r'\{[\s\S]*?\}', model_output)
                            if json_match:
                                json_str = json_match.group(0)
                                print(f"直接提取JSON字符串: {json_str}")
                                result = json.loads(json_str)
                                print(f"直接提取后解析成功: {result}")
                                if isinstance(result, dict):
                                    return {
                                        "has_violation": result.get("has_violation", result.get("result", False)),
                                        "violation_desc": result.get("reason", result.get("message", "")),
                                        "model_latency_ms": model_latency_ms
                                    }
                        except Exception as direct_error:
                            print(f"直接提取JSON失败: {str(direct_error)}")
                        
                        # 尝试使用更宽松的解析方式
                        try:
                            # 尝试移除可能的额外字符
                            clean_output = model_output.strip()
                            if clean_output:
                                print(f"尝试使用ast.literal_eval解析: {clean_output[:100]}...")
                                # 尝试使用ast.literal_eval
                                result = ast.literal_eval(clean_output)
                                print("使用ast.literal_eval解析成功")
                                
                                # 直接处理列表情况
                                if isinstance(result, list) and len(result) > 0:
                                    first_item = result[0]
                                    if isinstance(first_item, dict) and 'text' in first_item:
                                        print("从列表中提取text字段")
                                        text_content = first_item['text']
                                        print(f"提取后的text内容: {text_content[:200]}...")
                                        
                                        # 直接搜索JSON格式
                                        try:
                                            # 搜索大括号包围的内容
                                            json_match = re.search(r'\{[\s\S]*?\}', text_content)
                                            if json_match:
                                                json_str = json_match.group(0)
                                                print(f"直接提取JSON字符串: {json_str}")
                                                json_result = json.loads(json_str)
                                                print("解析JSON成功")
                                                if isinstance(json_result, dict):
                                                    return {
                                                        "has_violation": json_result.get("has_violation", json_result.get("result", False)),
                                                        "violation_desc": json_result.get("reason", json_result.get("message", "")),
                                                        "model_latency_ms": model_latency_ms
                                                    }
                                        except Exception as direct_error:
                                            print(f"直接提取JSON失败: {str(direct_error)}")
                                
                                # 如果结果是字典，直接使用
                                if isinstance(result, dict):
                                    return {
                                        "has_violation": result.get("has_violation", result.get("result", False)),
                                        "violation_desc": result.get("reason", result.get("message", "")),
                                        "model_latency_ms": model_latency_ms
                                    }
                        except Exception as eval_error:
                            print(f"ast.literal_eval解析错误: {str(eval_error)}")
                        
                        # 尝试更强大的JSON提取方法
                        try:
                            # 搜索所有可能的JSON结构
                            print("尝试搜索所有可能的JSON结构")
                            # 匹配完整的JSON对象
                            json_patterns = [
                                r'\{\s*"[^"]+"\s*:\s*[^,]+(\s*,\s*"[^"]+"\s*:\s*[^,]+)*\s*\}',
                                r'\{[\s\S]*?has_violation[\s\S]*?reason[\s\S]*?\}',
                                r'\{[\s\S]*?result[\s\S]*?reason[\s\S]*?\}'
                            ]
                            
                            for pattern in json_patterns:
                                json_matches = re.findall(pattern, model_output, re.DOTALL)
                                if json_matches:
                                    for match in json_matches:
                                        try:
                                            # 构建完整的JSON字符串
                                            if not match.startswith('{'):
                                                # 找到匹配的大括号开始位置
                                                start_pos = model_output.find(match)
                                                if start_pos > 0:
                                                    # 向前搜索开始的大括号
                                                    for i in range(start_pos, -1, -1):
                                                        if model_output[i] == '{':
                                                            start_pos = i
                                                            break
                                            else:
                                                start_pos = model_output.find(match)
                                            
                                            # 找到匹配的大括号结束位置
                                            end_pos = start_pos
                                            brace_count = 0
                                            found_start = False
                                            for i in range(start_pos, len(model_output)):
                                                if model_output[i] == '{':
                                                    brace_count += 1
                                                    found_start = True
                                                elif model_output[i] == '}':
                                                    brace_count -= 1
                                                    if found_start and brace_count == 0:
                                                        end_pos = i + 1
                                                        break
                                            
                                            json_str = model_output[start_pos:end_pos]
                                            print(f"尝试解析JSON字符串: {json_str}")
                                            
                                            # 清理JSON字符串
                                            json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                                            
                                            # 尝试解析
                                            result = json.loads(json_str)
                                            print(f"解析成功: {result}")
                                            if isinstance(result, dict):
                                                return {
                                                    "has_violation": result.get("has_violation", result.get("result", False)),
                                                    "violation_desc": result.get("reason", result.get("message", "")),
                                                    "model_latency_ms": model_latency_ms
                                                }
                                        except Exception as e:
                                            print(f"解析JSON字符串失败: {str(e)}")
                                            continue
                        except Exception as e:
                            print(f"搜索JSON结构失败: {str(e)}")
                        
                        # 尝试最基本的解析 - 直接查找关键字段
                        try:
                            print("尝试直接查找关键字段")
                            # 查找has_violation或result字段
                            has_violation_match = re.search(r'(has_violation|result)\s*[:=]\s*(true|false|True|False)', model_output)
                            has_violation = False
                            if has_violation_match:
                                has_violation_str = has_violation_match.group(2).lower()
                                has_violation = has_violation_str == 'true'
                                print(f"直接提取has_violation: {has_violation}")
                            
                            # 查找reason字段
                            reason_match = re.search(r'reason\s*[:=]\s*["\']([^"\']*)["\']', model_output)
                            violation_desc = ""
                            if reason_match:
                                violation_desc = reason_match.group(1)
                                print(f"直接提取reason: {violation_desc}")
                            elif has_violation_match:
                                # 如果找到了has_violation但没有找到reason，使用默认值
                                violation_desc = "模型检测到违规" if has_violation else "模型未检测到违规"
                            
                            # 如果成功提取了关键字段，返回结果
                            if has_violation_match:
                                print("成功直接提取关键字段")
                                return {
                                    "has_violation": has_violation,
                                    "violation_desc": violation_desc,
                                    "model_latency_ms": model_latency_ms
                                }
                        except Exception as e:
                            print(f"直接查找关键字段失败: {str(e)}")
                        
                        # 尝试使用更简单的方法 - 基于prompt的预期格式
                        try:
                            print("尝试基于prompt预期格式解析")
                            # 查找result和reason字段
                            result_match = re.search(r'result\s*[:=]\s*(true|false|True|False)', model_output)
                            reason_match = re.search(r'reason\s*[:=]\s*["\']([^"\']*)["\']', model_output)
                            
                            if result_match:
                                has_violation = result_match.group(1).lower() == 'true'
                                if reason_match:
                                    violation_desc = reason_match.group(1)
                                else:
                                    violation_desc = "模型检测到违规" if has_violation else "模型未检测到违规"
                                print(f"基于预期格式解析成功: has_violation={has_violation}, reason={violation_desc}")
                                return {
                                    "has_violation": has_violation,
                                    "violation_desc": violation_desc,
                                    "model_latency_ms": model_latency_ms
                                }
                        except Exception as e:
                            print(f"基于预期格式解析失败: {str(e)}")
                        
                        # 解析失败，返回错误信息
                        return {
                            "has_violation": False,
                            "violation_desc": f"JSON解析失败: {str(json_error)}",
                            "model_latency_ms": model_latency_ms
                        }
                except Exception as e:
                    # 打印模型输出内容，以便调试
                    print(f"模型返回的内容: {model_output}")
                    print(f"错误详情: {str(e)}")
                    return {
                        "has_violation": False,
                        "violation_desc": f"响应解析失败: {str(e)}",
                        "model_latency_ms": model_latency_ms
                    }
            except Exception as e:
                print(f"响应处理异常: {str(e)}")
                return {
                    "has_violation": False,
                    "violation_desc": f"响应处理失败: {str(e)}",
                    "model_latency_ms": model_latency_ms
                }
        else:
            print(f"模型调用失败，状态码: {response.status_code}")
            return {
                "has_violation": False,
                "violation_desc": f"模型调用失败: {response.message if hasattr(response, 'message') else str(response)}",
                "model_latency_ms": model_latency_ms
            }
            
    except Exception as e:
        print(f"模型调用总异常: {str(e)}")
        model_latency_ms = int((time.time() - start_time) * 1000)
        return {
            "has_violation": False,
            "violation_desc": f"模型调用异常: {str(e)}",
            "model_latency_ms": model_latency_ms
        }