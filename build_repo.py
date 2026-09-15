# -*- coding: utf-8 -*-
"""
个人越狱源构建脚本（等价于 dpkg-scanpackages + Release 生成）
用法：
  1. 把 .deb 放进 debs/ 文件夹
  2. 运行  python build_repo.py
  3. 把整个文件夹推到 GitHub Pages 即可
重跑即增量更新：新包加进 debs/ 再跑一次，索引自动重算。
"""
import os, io, tarfile, hashlib, bz2, lzma, glob, sys, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DEBS = os.path.join(ROOT, 'debs')
REPO_NAME = 'personal-jb-repo'
REPO_LABEL = '自用插件源'

# 字段名大小写规范化（兼容部分作者写的小写 control，如 冰蓝 dynamicfx）
CANON = {
    'package': 'Package', 'version': 'Version', 'name': 'Name',
    'architecture': 'Architecture', 'depends': 'Depends',
    'description': 'Description', 'author': 'Author', 'maintainer': 'Maintainer',
    'section': 'Section', 'icon': 'Icon', 'sileodepiction': 'SileoDepiction',
    'sileo': 'Sileo', 'depiction': 'Depiction', 'conflicts': 'Conflicts',
    'provides': 'Provides', 'replaces': 'Replaces', 'priority': 'Priority',
    'installed-size': 'Installed-Size', 'sponsor': 'Sponsor', 'dev': 'Dev',
    'tag': 'Tag', 'essential': 'Essential', 'filename': 'Filename',
    'size': 'Size', 'md5sum': 'MD5sum', 'sha1': 'SHA1', 'sha256': 'SHA256',
}

def parse_ar(path):
    """解析 .deb (ar 归档)，返回 member 名 -> 字节 的字典"""
    data = open(path, 'rb').read()
    if data[:8] != b'!<arch>\n':
        return None
    pos, members = 8, {}
    while pos + 60 <= len(data):
        hdr = data[pos:pos + 60]
        name = hdr[0:16].decode('latin1').rstrip(' /')
        if not name:  # 空名 = 归档结束标记
            break
        try:
            size = int(hdr[48:58].decode('latin1').strip().rstrip('`'))
        except ValueError:
            break
        members[name] = data[pos + 60:pos + 60 + size]
        pos += 60 + size + (size % 2)
    return members

def read_control(deb_path):
    """从 .deb 里读出 control 文件文本"""
    members = parse_ar(deb_path)
    if not members:
        return None
    for k, v in members.items():
        if k.startswith('control.tar'):
            try:
                with tarfile.open(fileobj=io.BytesIO(v), mode='r:*') as tf:
                    for m in tf.getmembers():
                        if m.name.rstrip('/') == 'control' or m.name.endswith('/control'):
                            ctl = tf.extractfile(m)
                            if ctl is not None:
                                return ctl.read().decode('utf-8', 'replace')
            except Exception:
                continue
    return None

def parse_control_fields(text):
    """把 control 文本解析为字段字典（保留多行 Description），字段名统一规范大小写"""
    fields, cur = {}, None
    for line in text.splitlines():
        if line[:1] in (' ', '\t'):
            if cur:
                fields[cur] += '\n' + line
            continue
        if ':' in line:
            k, _, v = line.partition(':')
            k = k.strip()
            if k:
                k = CANON.get(k, k)
                fields[k] = v.strip()
                cur = k
    return fields

def clean_deb_name(fields):
    pkg = re_sub(fields.get('Package', 'package'))
    ver = re_sub(fields.get('Version', '0'))
    arch = re_sub(fields.get('Architecture', 'iphoneos-arm64'))
    return '%s_%s_%s.deb' % (pkg, ver, arch)

def re_sub(s):
    import re
    s = s.strip().replace(' ', '_')
    s = re.sub(r'[^A-Za-z0-9._+~-]', '_', s)
    return s

def sha(mode, data):
    h = hashlib.new(mode)
    h.update(data)
    return h.hexdigest()

def main():
    os.makedirs(DEBS, exist_ok=True)
    # 允许把外部 deb 复制进来： python build_repo.py "C:/path/to/a.deb" "C:/path/to/b.deb"
    if len(sys.argv) > 1:
        for src in sys.argv[1:]:
            if os.path.exists(src):
                fields = parse_control_fields(read_control(src) or '')
                target = os.path.join(DEBS, clean_deb_name(fields))
                shutil.copy2(src, target)
                print('导入:', os.path.basename(src), '->', os.path.basename(target))

    debs = sorted(glob.glob(os.path.join(DEBS, '*.deb')))
    if not debs:
        print('debs/ 里没有 .deb，请先把插件放进去。')
        return 1

    entries = []
    archs = set()
    for deb in debs:
        rel = os.path.relpath(deb, ROOT).replace('\\', '/')
        data = open(deb, 'rb').read()
        ctl = read_control(deb)
        if not ctl:
            print('警告：无法读取 control，跳过', deb)
            continue
        fields = parse_control_fields(ctl)
        archs.add(fields.get('Architecture', 'iphoneos-arm64'))
        lines = []
        for k, v in fields.items():
            lines.append('%s: %s' % (k, v))
        lines.append('Filename: %s' % rel)
        lines.append('Size: %d' % len(data))
        lines.append('MD5sum: %s' % sha('md5', data))
        lines.append('SHA1: %s' % sha('sha1', data))
        lines.append('SHA256: %s' % sha('sha256', data))
        entries.append('\n'.join(lines))
        print('已收录:', rel)

    packages = '\n\n'.join(entries) + '\n'
    with open(os.path.join(ROOT, 'Packages'), 'w', encoding='utf-8') as f:
        f.write(packages)
    with open(os.path.join(ROOT, 'Packages.bz2'), 'wb') as f:
        f.write(bz2.compress(packages.encode('utf-8'), 9))
    with open(os.path.join(ROOT, 'Packages.xz'), 'wb') as f:
        f.write(lzma.compress(packages.encode('utf-8'), preset=9))

    # Release 文件
    rel_lines = []
    rel_lines.append('Origin: %s' % REPO_NAME)
    rel_lines.append('Label: %s' % REPO_LABEL)
    rel_lines.append('Suite: stable')
    rel_lines.append('Version: 1.0')
    rel_lines.append('Codename: %s' % REPO_NAME)
    rel_lines.append('Architectures: %s' % ' '.join(sorted(archs)))
    rel_lines.append('Components: main')
    rel_lines.append('Description: %s（个人自用，插件由本人维护）' % REPO_LABEL)
    rel_lines.append('')
    for mode, algo in (('MD5Sum', 'md5'), ('SHA1', 'sha1'), ('SHA256', 'sha256')):
        rel_lines.append('%s:' % mode)
        for fn in ('Packages', 'Packages.bz2', 'Packages.xz'):
            fp = os.path.join(ROOT, fn)
            if os.path.exists(fp):
                rel_lines.append(' %s %d %s' % (sha(algo, open(fp, 'rb').read()),
                                                os.path.getsize(fp), fn))
        rel_lines.append('')
    with open(os.path.join(ROOT, 'Release'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(rel_lines))

    print('完成：Packages / Packages.bz2 / Packages.xz / Release 已生成，共 %d 个插件。' % len(entries))
    return 0

if __name__ == '__main__':
    sys.exit(main())
