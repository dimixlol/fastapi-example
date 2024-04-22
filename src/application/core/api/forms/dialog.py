from pydantic import BaseModel


class DialogForm(BaseModel):
    message: str
