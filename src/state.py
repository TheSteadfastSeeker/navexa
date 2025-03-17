import operator
from typing import TypedDict, Annotated, List
from pydantic import BaseModel

class Step(BaseModel):
    """Each Tool invocation Step"""
    order: int
    """order in which this step must be performed"""
    tool: str
    reason: str

class Steps(BaseModel):
    """Steps"""
    steps: List[Step]

class WorkflowState(TypedDict):
    output: str
    user_query: str
    current_step: int
    steps: Annotated[List[Step], operator.add]
