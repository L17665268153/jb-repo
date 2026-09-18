# -*- coding: utf-8 -*-
"""解析 relative method list（arm64e 优化格式）"""
import struct

data = open('/tmp/prefs_arm64e.dylib', 'rb').read()
PTR_MASK = 0x00000000FFFFFFFF

def rd32u(va):
    return struct.unpack_from('<I', data, va)[0]

def cstr_at_va(va):
    end = data.find(b'\x00', va)
    if end < 0:
        return '?'
    return data[va:end].decode('utf-8', errors='replace')

def dump_methods(name, methods_va):
    m = methods_va & PTR_MASK
    entsize = rd32u(m)
    count = rd32u(m + 4)
    print("\n=== %s (0x%x) count=%d entsize=0x%x relative=%s ===" % (name, m, count, entsize, bool(entsize & 0x80000000)))
    es = entsize & 0xFFFF
    off = m + 8
    for i in range(count):
        if entsize & 0x80000000:  # relative: name/imp int32 相对偏移
            name_rel = struct.unpack_from('<i', data, off)[0]
            imp_rel = struct.unpack_from('<i', data, off + 8)[0]
            sel_va = off + name_rel
            imp_va = off + 8 + imp_rel
        else:
            sel_ptr = struct.unpack_from('<Q', data, off)[0] & PTR_MASK
            imp_ptr = struct.unpack_from('<Q', data, off + 16)[0] & PTR_MASK
            sel_va, imp_va = sel_ptr, imp_ptr
        sel = cstr_at_va(sel_va)
        print("  [%2d] %-55s imp=0x%x" % (i, sel, imp_va))
        off += es

dump_methods('IntroduceCopyVaultController', 0xc31000092e18)
dump_methods('CVRootListController', 0xc31000092860)
dump_methods('IntroduceSquidGestureController', 0xc31000092e50)
