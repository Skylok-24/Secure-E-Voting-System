import random
from math import gcd

# توليد عدد أولي بسيط
def generate_prime():
    primes = [101, 103, 107, 109, 113, 127, 131, 137, 139, 149]  # أعداد أكبر قليلاً لتقليل فرص التصادم
    return random.choice(primes)

# توليد المفاتيح
def generate_keys():
    p = generate_prime()
    q = generate_prime()
    while q == p:
        q = generate_prime()

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 3
    while gcd(e, phi) != 1:
        e += 2

    # حساب d
    d = pow(e, -1, phi)

    return (e, n), (d, n)

# تشفير
def encrypt(message, public_key):
    e, n = public_key
    return [pow(ord(char), e, n) for char in message]

# فك التشفير
def decrypt(cipher, private_key):
    d, n = private_key
    return ''.join([chr(pow(char, d, n)) for char in cipher])



if __name__ == "__main__":
    public, private = generate_keys()

    msg = "B"

    encrypted = encrypt(msg, public)
    print("Encrypted:", encrypted)

    decrypted = decrypt(encrypted, private)
    print("Decrypted:", decrypted)