"""
加密模块 - AES-256-GCM
用于报价数据的加密和解密
"""
import base64
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config.settings import ENCRYPTION_KEY


class CryptoManager:
    """加密管理器"""

    def __init__(self, key: str = None):
        """
        初始化加密管理器
        :param key: 64 字符的十六进制密钥 (32 字节)
        """
        if key is None:
            key = ENCRYPTION_KEY
        
        # 将十六进制字符串转换为字节
        self.key = bytes.fromhex(key)
        self.aesgcm = AESGCM(self.key)

    def encrypt_price(self, price: float, metadata: dict = None) -> str:
        """
        加密报价
        :param price: 报价金额
        :param metadata: 附加元数据 (可选)
        :return: Base64 编码的密文
        """
        # 生成随机 nonce (12 字节)
        nonce = os.urandom(12)
        
        # 构建明文数据
        data = {
            "price": price,
            "metadata": metadata or {}
        }
        plaintext = json.dumps(data).encode('utf-8')
        
        # 加密
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        
        # 组合 nonce + 密文，并 Base64 编码
        encrypted_data = nonce + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')

    def decrypt_price(self, encrypted_data: str) -> dict:
        """
        解密报价
        :param encrypted_data: Base64 编码的密文
        :return: 包含 price 和 metadata 的字典
        """
        # Base64 解码
        data = base64.b64decode(encrypted_data)
        
        # 提取 nonce (前 12 字节) 和密文
        nonce = data[:12]
        ciphertext = data[12:]
        
        # 解密
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        
        # 解析 JSON
        return json.loads(plaintext.decode('utf-8'))

    def encrypt_data(self, data: dict) -> str:
        """
        加密任意数据
        :param data: 要加密的字典
        :return: Base64 编码的密文
        """
        nonce = os.urandom(12)
        plaintext = json.dumps(data).encode('utf-8')
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        encrypted_data = nonce + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')

    def decrypt_data(self, encrypted_data: str) -> dict:
        """
        解密任意数据
        :param encrypted_data: Base64 编码的密文
        :return: 解密后的字典
        """
        data = base64.b64decode(encrypted_data)
        nonce = data[:12]
        ciphertext = data[12:]
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(plaintext.decode('utf-8'))


# 全局加密管理器实例
crypto_manager = CryptoManager()
