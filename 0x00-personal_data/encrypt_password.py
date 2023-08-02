#!/usr/bin/env python3
""" Password encrytpion """
import bcrypt


def hash_password(password: str) -> bytes:
    """ Takes in a password string and returns a
    hashed password
    Args:
        password: Byte string
    """
    encoded_password = password.encode()
    return bcrypt.hashpw(encoded_password, bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """ Validate that the password matches the hashed
    password
    """
    encoded_password = password.encode()
    if bcrypt.checkpw(encoded_password, hashed_password):
        return True
    return False
