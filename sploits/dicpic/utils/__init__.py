import random, string

def generate_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_email() -> str:
    return f'{generate_string(8)}@{generate_string(5)}.{generate_string(3)}'

def generate_upper_hex(length: int) -> str:
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))