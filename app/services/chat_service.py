from typing import List, Tuple
from app.services.llm_service import LLMService
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.utils.llm_prompts import PROMPT_FOR_CHAT


class ChatService:
    def __init__(self):
        self.llm_service = LLMService(max_tokens=128)  # Set max_tokens to 128 for all models in LLMService
    
    def generate_response(self, messages : List[Tuple]) -> dict:
        langchain_messages = []
        for role, content in messages:
            if role == "system":
                langchain_messages.append(SystemMessage(content= PROMPT_FOR_CHAT  + "\n\n" + content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))

        final_messages = []
        
        if len(langchain_messages) >= 9:  # If there are more than 9 messages, include the system message and the last 8 messages
            final_messages.append(langchain_messages[0])  # system message
            for message in langchain_messages[-6:]:  # last 6 messages (to keep the total at 7 including system message)
                final_messages.append(message)
        else:
            final_messages = langchain_messages

        ai_message = self.llm_service.invoke_messages(final_messages)

        return {
            "assistant_message": ai_message
        }