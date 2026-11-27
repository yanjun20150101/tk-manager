"""
加密工具模块
用于加密敏感数据（如TikTok令牌）
"""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import base64
from app.core.config import settings


class EncryptionService:
    """加密服务类"""
    
    def __init__(self):
        # 从配置中获取主密钥，并派生加密密钥
        self.master_key = settings.SECRET_KEY.encode()
        self.key = self._derive_key(self.master_key)
    
    def _derive_key(self, master_key: bytes, salt: bytes = None) -> bytes:
        """
        从主密钥派生加密密钥
        
        Args:
            master_key: 主密钥
            salt: 盐值（可选）
        
        Returns:
            派生的32字节密钥
        """
        if salt is None:
            # 使用固定盐值（生产环境应使用随机盐值并存储）
            salt = b'tiktok_manager_salt_v1'
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(master_key)
    
    def encrypt_token(self, token: str) -> dict:
        """
        加密令牌
        
        Args:
            token: 要加密的令牌字符串
        
        Returns:
            包含加密数据、IV和认证标签的字典
        """
        # 生成随机IV（12字节用于GCM模式）
        iv = os.urandom(12)
        
        # 创建AESGCM实例
        aesgcm = AESGCM(self.key)
        
        # 加密数据
        token_bytes = token.encode('utf-8')
        ciphertext = aesgcm.encrypt(iv, token_bytes, None)
        
        # ciphertext包含密文和认证标签（最后16字节）
        # 分离密文和认证标签
        auth_tag = ciphertext[-16:]
        encrypted_data = ciphertext[:-16]
        
        return {
            'encrypted': base64.b64encode(encrypted_data).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'auth_tag': base64.b64encode(auth_tag).decode('utf-8')
        }
    
    def decrypt_token(self, encrypted: str, iv: str, auth_tag: str) -> str:
        """
        解密令牌
        
        Args:
            encrypted: Base64编码的加密数据
            iv: Base64编码的IV
            auth_tag: Base64编码的认证标签
        
        Returns:
            解密后的令牌字符串
        """
        try:
            # 解码Base64
            encrypted_data = base64.b64decode(encrypted)
            iv_bytes = base64.b64decode(iv)
            auth_tag_bytes = base64.b64decode(auth_tag)
            
            # 重组密文（密文 + 认证标签）
            ciphertext = encrypted_data + auth_tag_bytes
            
            # 创建AESGCM实例
            aesgcm = AESGCM(self.key)
            
            # 解密数据
            plaintext = aesgcm.decrypt(iv_bytes, ciphertext, None)
            
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")


# 创建全局加密服务实例
encryption_service = EncryptionService()


def encrypt_token(token: str) -> dict:
    """
    加密令牌的便捷函数
    
    Args:
        token: 要加密的令牌字符串
    
    Returns:
        包含加密数据、IV和认证标签的字典
    """
    return encryption_service.encrypt_token(token)


def decrypt_token(encrypted: str, iv: str, auth_tag: str) -> str:
    """
    解密令牌的便捷函数
    
    Args:
        encrypted: Base64编码的加密数据
        iv: Base64编码的IV
        auth_tag: Base64编码的认证标签
    
    Returns:
        解密后的令牌字符串
    """
    return encryption_service.decrypt_token(encrypted, iv, auth_tag)
