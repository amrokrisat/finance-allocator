"""Local-auth helpers for the MVP.

The planner engine is the priority for this iteration, so auth is kept small:
password hashing and verification are implemented here and can later be wired to
API routes and persistent storage without changing the financial modules.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass


PBKDF2_ITERATIONS = 120_000


@dataclass
class AuthRecord:
    email: str
    password_hash: str


def hash_password(password: str, salt: bytes | None = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{salt.hex()}:{derived.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    salt_hex, hash_hex = password_hash.split(":")
    expected = hash_password(password, salt=bytes.fromhex(salt_hex))
    return hmac.compare_digest(expected.split(":")[1], hash_hex)

