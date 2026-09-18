# -*- coding: utf-8 -*-
"""prefs arm64e xref：找 IntroduceCopyVaultController / dismissWelcomeController 引用"""
import struct

data = open('/tmp/prefs_arm64e.dylib', 'rb').read()
CODE_START, CODE_END = 0, 0xa0000  # __TEXT

TARGETS = {
    "IntroduceCopyVaultController": 0x9d408,
    "dismissWelcomeController": 0x97dc0,
    "presentViewController:animated:completion:": 0x99c24,
}

def u32(pc):
    return struct.unpack_from('<I', data, pc)[0]

last = {}
found = {k: [] for k in TARGETS}
for pc in range(CODE_START, CODE_END, 4):
    w = u32(pc)
    if (w & 0x9F000000) == 0x90000000:
        immhi = (w >> 5) & 0x7FFFF
        immlo = (w >> 29) & 0x3
        imm = (immhi << 2) | immlo
        if imm & 0x100000:
            imm -= 0x200000
        page = (pc & ~0xFFF) + (imm << 12)
        last[w & 0x1F] = (pc, page)
        continue
    used = None
    if (w & 0xFF000000) == 0x91000000:  # ADD imm
        used = ((w >> 5) & 0x1F, (w >> 10) & 0xFFF, 'ADD')
    elif (w & 0xFFC00000) == 0xF9400000:  # LDR unsigned imm
        used = ((w >> 5) & 0x1F, ((w >> 10) & 0xFFF) * 8, 'LDR')
    if used:
        rn, imm, kind = used
        if rn in last:
            apc, page = last[rn]
            if 0 <= pc - apc <= 0x10000:
                target = page + imm
                for k, va in TARGETS.items():
                    if abs(target - va) <= 0x40:
                        found[k].append((pc, apc, target, kind))

for k, hits in found.items():
    print("%-45s %d 处引用:" % (k, len(hits)))
    for h in hits[:20]:
        print("  %s@0x%x (ADRP@0x%x → 0x%x)" % (h[3], h[0], h[1], h[2]))
