import random
import string


def generate_name(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


def generate_username(length: int = 20) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()", k=length))


def generate_digits(length: int = 10) -> int:
    return int("".join(random.choices(string.digits, k=length)))
