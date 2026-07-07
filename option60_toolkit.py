# -*- coding:utf-8 -*-
"""
DHCP Option 60 工具包
基于中国电信IPTV技术规范实现

功能：
1. 解密Option 60字段
2. 生成Option 60字段
3. 验证Password是否正确
"""

import binascii
import struct
import time
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes

class Option60Handler:
    """Option 60 处理器"""
    
    # 固定头
    ENTERPRISE_CODE = b'\x00\x00'
    FIELD_TYPE = b'\x1f\x39'
    SUB_TYPE = b'\x01'
    
    def __init__(self, password):
        """
        初始化
        
        参数:
            password: VoIP密码
        """
        self.password = password.encode('utf-8')
    
    def generate(self, userid):
        """
        生成Option 60信息域
        
        参数:
            userid: IPTV用户名
        
        返回:
            十六进制字符串形式的信息域
        """
        # 1. 生成随机数R (8字节)
        R = get_random_bytes(8)
        
        # 2. 生成时间戳TS (8字节)
        # TS = 86400 + 当前时间的秒数部分 (模拟开机时间)
        # 使用小端序存储，并设置标志位
        current_seconds = 9
        TS_int = 86400 + 9
        TS = struct.pack('<Q', TS_int)  # 使用小端序
        
        # 3. 计算Key = MD5(R + Password + TS)
        hash_input = R + self.password + TS
        md5 = MD5.new()
        md5.update(hash_input)
        Key = md5.digest()
        
        # 4. 加密UserID
        # 密钥 = R + TS + 0x00*8 (24字节)
        encrypt_key = R + TS + b'\x00' * 8
        userid_bytes = userid.encode('utf-8')
        userid_padded = pad(userid_bytes, 8)  # PKCS7填充
        
        cipher = DES3.new(encrypt_key, DES3.MODE_ECB)
        C = cipher.encrypt(userid_padded)
        
        # 5. 拼接信息域
        info_field = (
            self.ENTERPRISE_CODE +
            self.FIELD_TYPE +
            self.SUB_TYPE +
            R +
            TS +
            Key +
            C
        )
        
        return binascii.hexlify(info_field).decode().upper()
    
    def parse(self, info_hex):
        """
        解析Option 60信息域
        
        参数:
            info_hex: 十六进制字符串形式的信息域
        
        返回:
            解析后的字典
        """
        if len(info_hex) % 2 != 0:
            info_hex = info_hex[:-1]
        
        data = binascii.unhexlify(info_hex)
        
        if len(data) < 37:
            raise ValueError("信息域长度不足")
        
        # 解析各字段
        enterprise = data[0:2]
        field_type = data[2:4]
        sub_type = data[4:5]
        R = data[5:13]
        TS_bytes = data[13:21]
        Key = data[21:37]
        C = data[37:]
        
        # 解析时间戳
        TS_int = struct.unpack('>Q', TS_bytes)[0]
        
        return {
            'enterprise': binascii.hexlify(enterprise).decode().upper(),
            'field_type': binascii.hexlify(field_type).decode().upper(),
            'sub_type': binascii.hexlify(sub_type).decode().upper(),
            'R': R,
            'R_hex': binascii.hexlify(R).decode().upper(),
            'TS': TS_bytes,
            'TS_int': TS_int,
            'TS_hex': binascii.hexlify(TS_bytes).decode().upper(),
            'Key': Key,
            'Key_hex': binascii.hexlify(Key).decode().upper(),
            'C': C,
            'C_hex': binascii.hexlify(C).decode().upper()
        }
    
    def verify_password(self, info_hex):
        """
        验证密码是否正确
        
        参数:
            info_hex: 十六进制字符串形式的信息域
        
        返回:
            (是否正确, 计算的Key, 样本中的Key)
        """
        parsed = self.parse(info_hex)
        
        # 计算Key
        hash_input = parsed['R'] + self.password + parsed['TS']
        md5 = MD5.new()
        md5.update(hash_input)
        calculated_key = md5.digest()
        
        return (
            calculated_key == parsed['Key'],
            binascii.hexlify(calculated_key).decode().upper(),
            parsed['Key_hex']
        )
    
    def decrypt(self, info_hex):
        """
        解密Option 60信息域
        
        参数:
            info_hex: 十六进制字符串形式的信息域
        
        返回:
            解密后的UserID
        """
        parsed = self.parse(info_hex)
        
        # 验证密码
        valid, _, _ = self.verify_password(info_hex)
        if not valid:
            raise ValueError("密码验证失败，无法解密")
        
        # 构造解密密钥
        encrypt_key = parsed['R'] + parsed['TS'] + b'\x00' * 8
        
        # 解密
        cipher = DES3.new(encrypt_key, DES3.MODE_ECB)
        decrypted = cipher.decrypt(parsed['C'])
        
        # 去除PKCS7填充
        try:
            userid = unpad(decrypted, 8).decode('utf-8')
        except:
            # 如果去填充失败，尝试直接解码
            userid = decrypted.decode('utf-8', errors='ignore').rstrip('\x00').strip()
        
        return userid


def main():   
        userid = "XXXXXXXXXXXX@vod"   #IPTV的账号，获取方式详见README.md
        password = "XXXXXX"  #六位密码，获取方式参见README.md
        handler = Option60Handler(password)

        encrypted = handler.generate(userid)
        print("Option60:", encrypted)
        
if __name__ == '__main__':
    main()
