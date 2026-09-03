"""schemas.py —— 请求体 pydantic 模型（入口校验：缺字段/类型错直接拦下，返回统一报错）。"""
from typing import List, Optional
from pydantic import BaseModel, Field


class RegisterBody(BaseModel):
    contact: str = Field(..., min_length=3)
    name: str = Field("", max_length=30)
    password: str = Field(..., min_length=6)
    code: str = Field("", min_length=0)


class RegisterPubBody(BaseModel):
    contact: str = Field(..., min_length=3)
    name: str = Field("", max_length=30)
    password: str = Field(..., min_length=6)


class LoginBody(BaseModel):
    contact: str = Field(..., min_length=3)
    password: Optional[str] = None
    code: Optional[str] = None


class SendCodeBody(BaseModel):
    contact: str = Field(..., min_length=3)


class ForgotBody(BaseModel):
    contact: str = Field(..., min_length=3)


class ResetBody(BaseModel):
    contact: str = Field(..., min_length=3)
    code: str = Field(..., min_length=4)
    password: str = Field(..., min_length=6)


class PhoneBody(BaseModel):
    phone: str = ""


class NameBody(BaseModel):
    name: str = Field(..., min_length=1)


class PasswordBody(BaseModel):
    password: str = Field(..., min_length=4)


class PrefsBody(BaseModel):
    bg: str = ""
    bgImg: str = ""
    pets: List[str] = []
    theme: str = ""


class AvatarBody(BaseModel):
    avatar: str = Field(..., min_length=5)
