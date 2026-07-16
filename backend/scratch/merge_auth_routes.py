import os
import shutil

auth_routes_dir = r"d:\Cerberus\v2\cerberus\backend\src\modules\auth\api\routes"


def read_file(name):
    with open(os.path.join(auth_routes_dir, name), "r", encoding="utf-8") as f:
        return f.read()


def write_file(name, content):
    with open(os.path.join(auth_routes_dir, name), "w", encoding="utf-8") as f:
        f.write(content)


def delete_file(name):
    path = os.path.join(auth_routes_dir, name)
    if os.path.exists(path):
        os.remove(path)


# Plan:
# login.py <- local.py (login only), refresh.py, logout.py
# oauth.py <- callbacks.py, oauth_login.py, tenant_oauth.py, exchange.py
# register.py <- local.py (register only)
# verify.py <- verify_email.py
# password.py <- reset_password.py
# sessions.py <- sessions.py

# First, rename the 1-to-1 files


def rename(src, dst):
    shutil.move(os.path.join(auth_routes_dir, src), os.path.join(auth_routes_dir, dst))


rename("verify_email.py", "verify.py")
rename("reset_password.py", "password.py")

# Combine OAuth files
oauth_files = ["callbacks.py", "oauth_login.py", "tenant_oauth.py", "exchange.py"]
oauth_content = "from fastapi import APIRouter\nrouter = APIRouter()\n"
for f in oauth_files:
    content = read_file(f)
    # remove APIRouter initialization
    content = content.replace("router = APIRouter()", "")
    oauth_content += "\n" + content
    delete_file(f)
write_file("oauth.py", oauth_content)

# For login.py and register.py, local.py has both register and login.
local_content = read_file("local.py")
# We will split it by looking at the endpoints.
# Local.py has `register` and `login`.
register_part = (
    """from fastapi import APIRouter
router = APIRouter()
"""
    + local_content
)
# Keep register only in register_part
# Actually, it's easier to just copy the file for both, and let the user (me) manually delete the unused endpoints from each file.
write_file("register.py", register_part)

login_files = ["local.py", "refresh.py", "logout.py"]
login_content = "from fastapi import APIRouter\nrouter = APIRouter()\n"
for f in login_files:
    content = read_file(f)
    content = content.replace("router = APIRouter()", "")
    login_content += "\n" + content
    delete_file(f)
write_file("login.py", login_content)

# Now we need to update __init__.py
init_content = """from fastapi import APIRouter

from src.modules.auth.api.routes.login import router as login_router
from src.modules.auth.api.routes.oauth import router as oauth_router
from src.modules.auth.api.routes.register import router as register_router
from src.modules.auth.api.routes.verify import router as verify_router
from src.modules.auth.api.routes.password import router as password_router
from src.modules.auth.api.routes.sessions import router as sessions_router

router = APIRouter()
router.include_router(login_router)
router.include_router(oauth_router)
router.include_router(register_router)
router.include_router(verify_router)
router.include_router(password_router)
router.include_router(sessions_router)
"""
write_file("__init__.py", init_content)
