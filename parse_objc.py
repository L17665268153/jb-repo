# -*- coding: utf-8 -*-
"""修正偏移解析 objc 类"""
import struct

data = open('/tmp/prefs_arm64e.dylib', 'rb').read()
PTR_MASK = 0x00000000FFFFFFFF

def rd64(va):
    return struct.unpack_from('<Q', data, va)[0]

def cstr(va):
    va &= PTR_MASK
    end = data.find(b'\x00', va)
    if end < 0:
        return '?'
    try:
        return data[va:end].decode('utf-8')
    except Exception:
        return '?'

classlist = 0xa1210
nclasses = 0x148 // 8
print("类数量:", nclasses)
for i in range(nclasses):
    cls_ptr = rd64(classlist + i*8) & PTR_MASK
    if cls_ptr == 0:
        continue
    data_off = rd64(cls_ptr + 32) & PTR_MASK
    # class_ro_t: name @+24, baseMethods @+32
    name_va = rd64(data_off + 24) & PTR_MASK
    name = cstr(name_va)
    methods_va = rd64(data_off + 32) & PTR_MASK
    if ('Introduce' in name) or ('Welcome' in name) or ('Root' in name) or name.startswith('CV'):
        print("类: %-45s class=0x%x data=0x%x methods=0x%x" % (name, cls_ptr, data_off, methods_va))
