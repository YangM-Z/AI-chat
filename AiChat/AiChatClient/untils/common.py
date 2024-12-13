'''
文件名: common.py
描述: 包含一些工具函数
'''

import hashlib
import uuid

def md5(data):
    """
    获取md5加密密文
    :param data: 明文
    :return: 加密后的密文
    """
    m = hashlib.md5()
    b = data.encode(encoding='utf-8')
    m.update(b)
    return m.hexdigest()

def get_uuid():
    """
    使用主机ID, 序列号, 和当前时间来生成UUID, 可保证全球范围的唯一性.
    :return: 唯一ID号
    """
    return str(uuid.uuid1()).replace('-', '')

# 测试
if __name__ == '__main__':
    print(md5('pass'))
    print(get_uuid())