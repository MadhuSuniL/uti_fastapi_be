from pydantic import BaseModel
from typing import List, Tuple, Optional

class Messages(BaseModel):
    messages: List[Tuple[str, str]]  # List of tuples (role, content)
    answer: Optional[str] = None  # Optional field to store the assistant's response 

