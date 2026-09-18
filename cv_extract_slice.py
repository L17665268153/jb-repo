# -*- coding: utf-8 -*-
"""提取 fat 中的 arm64e slice，并定位 IntroduceCopyVaultController 引用"""
import struct, sys

fat = open('/tmp/cv_main.dylib', 'rb').read()
magic = struct.unpack('<I', fat[:4])[0]
print('magic: 0x%x' % magic)

slices = []
if magic == 0xcafebabe:  # FAT_MAGIC (big-endian)
    nfat = struct.unpack('>I', fat[4:8])[0]
    off = 8
    for i in range(nfat):
        cputype, cpusubtype, offset, size, align = struct.unpack('>IIIII', fat[off:off+20])
        off += 20
        slices.append((cputype, cpusubtype, offset, size))
        print('fat: cputype=%d subtype=%d off=0x%x size=0x%x' % (cputype, cpusubtype, offset, size))
elif magic == 0xbebafeca:  # FAT_CIGAM (little-endian stored)
    nfat = struct.unpack('<I', fat[4:8])[0]
    off = 8
    for i in range(nfat):
        cputype, cpusubtype, offset, size, align = struct.unpack('<IIIII', fat[off:off+20])
        off += 20
        slices.append((cputype, cpusubtype, offset, size))
        print('fat(cigam): cputype=%d subtype=%d off=0x%x size=0x%x' % (cputype, cpusubtype, offset, size))
else:
    print('not fat, single slice at 0')

# arm64e = cputype 0x0100000c | subtype 0x80000002
for cputype, cpusubtype, offset, size in slices:
    if cputype == 0x0100000C and cpusubtype == 0x80000002:
        data = fat[offset:offset+size]
        open('/tmp/cv_arm64e.dylib', 'wb').write(data)
        print('saved arm64e slice: %d bytes' % len(data))
        # 找字符串
        kw = b'IntroduceCopyVaultController'
        pos = 0
        while True:
            i = data.find(kw, pos)
            if i < 0: break
            print('  IntroduceCopyVaultController @0x%x' % i)
            pos = i + 1
        break
