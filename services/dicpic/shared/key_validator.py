import re
import hashlib

def validate_key(key: str) -> bool:
    pattern = re.compile(r'^PREM-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-F0-9]{4}$')
    if not pattern.match(key):
        return False
    
    product_key = ''.join(key.split('-')[1:4])
    product_checksum = key.split('-')[4]

    calc_checksum = hashlib.sha256(product_key.encode()).hexdigest().upper()[:4]

    return calc_checksum == product_checksum
