from pydantic import BaseModel
from typing import List


# Listing model for submissions
class Listing(BaseModel):
    title: str
    description: str
    price: float


# Rule model
class Rule(BaseModel):
    content: str
