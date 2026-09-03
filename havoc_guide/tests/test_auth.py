"""test_auth.py —— 认证/权限接口测试（FastAPI TestClient，用临时数据库，不污染真实数据）。

需在装有 fastapi + pytest + httpx 的环境运行（服务器 venv 安装后执行 pytest）。
"""
import os, tempfile, shutil

# 必须放在 import webapp 之前，让 webapp 用临时数据库
_TMP = tempfile.mkdtemp(prefix="dsh_test_")
os.environ["DSH_DB_PATH"] = os.path.join(_TMP, "test.db")
os.environ["DSH_USERS_PATH"] = os.path.join(_TMP, "never.json")  # 空库，不触发 JSON 迁移
# 强制关闭 SMTP：测试时不忘真发邮件，且 forgot/send_code 走"未配置"分支
os.environ["SMTP_USER"] = ""
os.environ["SMTP_PASS"] = ""

import pytest
from fastapi.testclient import TestClient
from webapp import app, USERS, _save_users


@pytest.fixture()
def client():
    USERS.clear()
    _save_users()
    return TestClient(app)


def test_register_first_is_admin(client):
    r = client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"})
    assert r.status_code == 200 and r.json()["ok"]
    assert r.json()["user"]["is_admin"] is True
    assert r.json()["user"]["owner"] is True


def test_register_second_not_admin(client):
    client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"})
    r = client.post("/api/auth/register_pub", json={"contact": "b@qq.com", "name": "B", "password": "123456"})
    assert r.json()["user"]["is_admin"] is False
    assert r.json()["user"]["owner"] is False


def test_register_duplicate(client):
    client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"})
    r = client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"})
    assert r.status_code == 400


def test_register_invalid_email(client):
    r = client.post("/api/auth/register_pub", json={"contact": "不是邮箱", "name": "X", "password": "123456"})
    assert r.status_code == 400


def test_login_ok(client):
    client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"})
    r = client.post("/api/auth/login", json={"contact": "a@qq.com", "password": "123456"})
    assert r.status_code == 200 and r.json()["ok"]
    assert "token" in r.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"})
    r = client.post("/api/auth/login", json={"contact": "a@qq.com", "password": "wrong"})
    assert r.status_code == 400


def test_login_unknown_account(client):
    r = client.post("/api/auth/login", json={"contact": "nobody@qq.com", "password": "123456"})
    assert r.status_code == 404


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_with_token(client):
    token = client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"}).json()["token"]
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200 and r.json()["ok"]


def test_admin_denied_for_normal_user(client):
    client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"})
    token = client.post("/api/auth/register_pub", json={"contact": "b@qq.com", "name": "B", "password": "123456"}).json()["token"]
    r = client.get("/api/admin/users", headers={"Authorization": "Bearer " + token})
    assert r.status_code == 403


def test_admin_owner_can_list(client):
    token = client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"}).json()["token"]
    r = client.get("/api/admin/users", headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200 and "users" in r.json()


def test_phone_bind_unique(client):
    client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"})
    token1 = client.post("/api/auth/login", json={"contact": "a@qq.com", "password": "123456"}).json()["token"]
    token2 = client.post("/api/auth/register_pub", json={"contact": "b@qq.com", "name": "B", "password": "123456"}).json()["token"]
    assert client.post("/api/auth/phone", json={"phone": "13800138000"}, headers={"Authorization": "Bearer " + token1}).status_code == 200
    r2 = client.post("/api/auth/phone", json={"phone": "13800138000"}, headers={"Authorization": "Bearer " + token2})
    assert r2.status_code == 400  # 手机号已被绑


def test_forgot_without_smtp_errors(client):
    client.post("/api/auth/register_pub", json={"contact": "a@qq.com", "name": "A", "password": "123456"})
    r = client.post("/api/auth/forgot", json={"contact": "a@qq.com"})
    # SMTP 未配置 → 不返回验证码，应报错
    assert r.status_code == 500 or r.json().get("ok") is False
    assert "code" not in r.json()
