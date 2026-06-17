from Crypto.Cipher import AES
import os

class AESDecryptor:
    def __init__(self, key, iv=None):
        if isinstance(key, str):
            key = bytes.fromhex(key)
        
        # 检查密钥长度
        key_len = len(key)
        if key_len not in [16, 24, 32]:
            # 尝试自动填充到16字节
            if key_len < 16:
                key = key + b'\x00' * (16 - key_len)
            elif key_len > 16 and key_len < 24:
                key = key + b'\x00' * (24 - key_len)
            elif key_len > 24 and key_len < 32:
                key = key + b'\x00' * (32 - key_len)
            else:
                raise ValueError(f"密钥长度为{key_len}字节，必须是16、24或32字节。当前密钥已自动填充到{len(key)}字节。")
        
        self.key = key
        
        if iv:
            if isinstance(iv, str):
                if iv.startswith('0x'):
                    iv = bytes.fromhex(iv[2:])
                else:
                    iv = bytes.fromhex(iv)
        else:
            iv = b'\x00' * 16
        
        self.iv = iv
    
    def decrypt(self, encrypted_data):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        padding_len = decrypted_data[-1]
        if padding_len > 0 and padding_len <= AES.block_size:
            return decrypted_data[:-padding_len]
        
        return decrypted_data
    
    def decrypt_file(self, input_path, output_path):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
    
    @staticmethod
    def load_key_from_file(key_file_path):
        if not os.path.exists(key_file_path):
            raise FileNotFoundError(f"密钥文件不存在: {key_file_path}")
        
        with open(key_file_path, 'rb') as f:
            key_data = f.read()
        
        if len(key_data) == 16 or len(key_data) == 24 or len(key_data) == 32:
            return key_data
        
        hex_str = key_data.decode('utf-8').strip()
        if len(hex_str) % 2 == 0:
            return bytes.fromhex(hex_str)
        
        raise ValueError("无法解析密钥文件内容")