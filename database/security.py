"""Password hashing shared by the whole team (Member 2 uses it in /register and /login).

    from database.security import hash_password, verify_password

We use PBKDF2-SHA256 through passlib: salted, slow on purpose, and it needs
no C compiler (bcrypt sometimes fails to install on student laptops).
"""
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return _pwd_context.verify(plain_password, password_hash)
