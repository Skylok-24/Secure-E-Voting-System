import hashlib
import json
from rsa_utils import generate_keys

# hash
def hash_data(data):
    # استخدام json.dumps لضمان توحيد شكل البيانات قبل التشفير (تجنب المسافات المختلفة)
    serialized_data = json.dumps(data, separators=(',', ':'), sort_keys=True)
    return hashlib.sha256(serialized_data.encode()).hexdigest()

# توقيع
def sign(data, private_key):
    d, n = private_key
    hashed = int(hash_data(data), 16) % n  # التأكد من أن القيمة أصغر من n
    return pow(hashed, d, n)

# تحقق
def verify(data, signature, public_key):
    e, n = public_key
    hashed = int(hash_data(data), 16) % n  # التأكد من أن القيمة أصغر من n
    result = pow(signature, e, n)
    return result == hashed


if __name__ == "__main__":
    pub, priv = generate_keys()

    data = [123, 456]

    sig = sign(data, priv)

    print(verify(data, sig, pub))  # True