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


# ==================== 响应模型（response_model，规范化接口文档） ====================

class VersionOut(BaseModel):
    game_version: str = ""


class Best3Out(BaseModel):
    name: str = ""
    quality: str = ""
    icon: str = ""


class ChampOut(BaseModel):
    """排行榜：单英雄（list 元素）"""
    id: str
    name: str = ""
    wins: int = 0
    games: int = 0
    wr: float = 0.0
    wilson: float = 0.0
    image: str = ""
    best3: List[Best3Out] = []


class AugBrief(BaseModel):
    """单个符文简述（全局符文 id→name）"""
    id: str
    name: str = ""


class AugFull(BaseModel):
    """单个符文全量（所有符文页）"""
    id: str = ""
    name: str = ""
    en: str = ""
    desc: str = ""
    icon: str = ""
    quality: str = ""


class AugGroup(BaseModel):
    """按品质分组的一档"""
    quality: str = ""
    items: List[AugFull] = []


class CommentOut(BaseModel):
    name: str = ""
    text: str = ""
    ts: int = 0


class CommentsOut(BaseModel):
    ok: bool = True
    comments: List[CommentOut] = []
