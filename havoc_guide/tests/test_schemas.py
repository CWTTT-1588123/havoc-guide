"""test_schemas.py —— 请求体 pydantic 模型校验测试（纯 pydantic，无需 FastAPI）。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from pydantic import ValidationError
from schemas import RegisterPubBody, LoginBody, PrefsBody, PhoneBody, ResetBody


def test_register_pub_valid():
    m = RegisterPubBody(contact="a@qq.com", name="A", password="123456")
    assert m.contact == "a@qq.com"


def test_register_pub_short_password_rejected():
    with pytest.raises(ValidationError):
        RegisterPubBody(contact="a@qq.com", password="123")


def test_register_pub_missing_password_rejected():
    with pytest.raises(ValidationError):
        RegisterPubBody(contact="a@qq.com", name="A")


def test_login_optional_code_password():
    m = LoginBody(contact="a@qq.com", password="secret")
    assert m.password == "secret"
    m2 = LoginBody(contact="a@qq.com", code="123456")
    assert m2.code == "123456"


def test_login_missing_contact_rejected():
    with pytest.raises(ValidationError):
        LoginBody(password="secret")


def test_prefs_lists_ok():
    m = PrefsBody(bg="linear-gradient(...)", pets=["ahri_pet.png"], theme="dark")
    assert m.pets == ["ahri_pet.png"]


def test_phone_default_empty():
    m = PhoneBody()
    assert m.phone == ""


def test_reset_short_code_rejected():
    with pytest.raises(ValidationError):
        ResetBody(contact="a@qq.com", code="12", password="123456")
