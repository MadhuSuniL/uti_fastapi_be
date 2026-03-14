import json
from typing import List, Tuple
from app.config import TESTING_MODE
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_groq import ChatGroq

from langchain_cohere import ChatCohere
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama


class LLMService:
    def __init__(self, max_tokens: int = 5000):
        self.model_list : List[Tuple[str, ChatGroq]] = [
            ("ollama_deepseek_v3_1_671b_cloud", ChatOllama(model="deepseek-v3.1:671b-cloud")),
            ("ollama_qwen3_coder_480b_cloud", ChatOllama(model="qwen3-coder:480b-cloud")),
            ("ollama_qwen3_vl_235b_cloud", ChatOllama(model="qwen3-vl:235b-cloud")),
            ("groq_openai_gpt_oss_120b_cloud", ChatGroq(model="openai/gpt-oss-120b")),
            ("ollama_openai_gpt_oss_120b_cloud", ChatOllama(model="gpt-oss:120b-cloud")),
            ("groq_openai_gpt_oss_20b_cloud", ChatGroq(model="openai/gpt-oss-20b")),
            ("ollama_openai_gpt_oss_20b_cloud", ChatOllama(model="gpt-oss:20b-cloud")),
            ("gemini_2_5_flash", ChatGoogleGenerativeAI(model="gemini-2.5-flash", max_retries = 0)),
            ("gemini_2_5_pro", ChatGoogleGenerativeAI(model="gemini-2.5-pro", max_retries = 0)),
            ("command_a_03_2025", ChatCohere(model="command-a-03-2025")),
            ("meta_llama_llama_4_maverick_17b_128e_instruct_cloud", ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")),
            ("meta_llama_llama_4_scout_17b_16e_instruct_cloud", ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")),
            ("llama_3_3_70b_versatile_cloud", ChatGroq(model="llama-3.3-70b-versatile")),
            ("qwen3_32b_cloud", ChatGroq(model="qwen/qwen3-32b")),
            ("llama_3_1_8b_instant_cloud", ChatGroq(model="llama-3.1-8b-instant")),
        ]

    def invoke_llm(self, system_prompt: str, user_prompt: dict | str) -> AIMessage:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=str(user_prompt))
        ]
        for model_name, model in self.model_list:
            try:
                response = model.invoke(messages)
                final_response = ""
                try:
                    final_response = json.loads(response.content)
                except json.JSONDecodeError:
                    print(f"Model {model_name} returned non-JSON response. Using raw content.")
                    final_response = response.content

                return final_response
            except Exception as e:
                print(f"Error with model {model_name}: {e}")
                continue     
        print(f"All models failed to generate the response")   
        return "Unable to generate response for this data. Free tokens exhausted for all models or all models failed. Please try again later."


    def invoke_messages(self, messages : List[BaseMessage]) -> AIMessage:
        for model_name, model in self.model_list:
            try:
                if TESTING_MODE:
                    response = AIMessage(content="Test long response : Antibiotic resistance is a major global healthcare challenge. Empirical treatment may lead to ineffective prescriptions. Our system predicts organism name and antibiotic resistance using structured clinical data, providing ranked antibiotic recommendations.")  # Placeholder response to ensure the code runs without actual model invocation during testing
                else:
                    response = model.invoke(messages)
                for msg in messages:
                    msg.pretty_print()
                final_response = response.content
                print(f"Response from {model_name}:", final_response)
                return final_response
            except Exception as e:
                print(f"Error with model {model_name}: {e}")
                continue        
        return "Unable to generate response for this question. Free tokens exhausted for all models or all models failed. Please try again later."