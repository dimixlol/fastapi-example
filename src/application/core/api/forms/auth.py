from pydantic import BaseModel, EmailStr


class SignUpForm(BaseModel):
    username: str
    password: str
    email: EmailStr


class CodeConfirmationForm(BaseModel):
    username: str
    code: str


class SignInForm(BaseModel):
    username: str
    password: str
