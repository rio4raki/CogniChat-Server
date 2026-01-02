import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class SecurityService:
    def __init__(self, secret_key):
        # 对应 Flutter: sha256.convert(utf8.encode(key)).bytes
        self.key = hashlib.sha256(secret_key.encode('utf-8')).digest()
        self.block_size = AES.block_size # 16 bytes

    def encrypt(self, plain_text):
        """
        加密: 明文 -> base64(iv):base64(cipher)
        """
        try:
            # 1. 生成随机 IV
            cipher = AES.new(self.key, AES.MODE_CBC)
            iv = cipher.iv
            
            # 2. 补码并加密
            # 对应 Flutter: encrypter.encrypt(plainText, iv: iv)
            encrypted_bytes = cipher.encrypt(pad(plain_text.encode('utf-8'), self.block_size))
            
            # 3. 拼接结果
            iv_b64 = base64.b64encode(iv).decode('utf-8')
            cipher_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
            
            return f"{iv_b64}:{cipher_b64}"
        except Exception as e:
            print(f"Encryption Error: {e}")
            return None

    def decrypt(self, encrypted_str):
        """
        解密: base64(iv):base64(cipher) -> 明文
        """
        try:
            # 1. 拆分 IV 和 密文
            parts = encrypted_str.split(':')
            if len(parts) != 2:
                raise ValueError("Invalid encrypted format")
            
            iv = base64.b64decode(parts[0])
            cipher_bytes = base64.b64decode(parts[1])
            
            # 2. 解密并去码
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted_text = unpad(cipher.decrypt(cipher_bytes), self.block_size).decode('utf-8')
            
            return decrypted_text
        except Exception as e:
            print(f"Decryption Error: {e}")
            return None