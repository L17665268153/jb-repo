# 自用插件源（personal-jb-repo）

个人越狱插件源，当前以**局域网模式**运行（本机 + 手机同一 WiFi），也可随时切换到 GitHub Pages / 其他静态托管。

## 目录结构

| 文件/目录 | 作用 |
|---|---|
| `debs/` | 存放插件 .deb 文件（新增插件丢这里） |
| `Packages` / `Packages.bz2` / `Packages.xz` | 插件索引，由 `build_repo.py` 自动生成 |
| `Release` | 仓库元信息 + 全部索引的校验和 |
| `build_repo.py` | 构建脚本：扫描 debs/ → 重建索引（等价于 dpkg-scanpackages） |
| `CydiaIcon.png` | 仓库图标（可选） |

## 日常使用：添加新插件（两步）

1. 把 `xxx.deb` 放进 `debs/` 文件夹
2. 在仓库目录运行一次 `python build_repo.py`（自动重算索引与校验和，服务无需重启）

## 手机上添加源（局域网模式）

Sileo / Zebra → 底部「源 / Sources」→ 右上角「+」→ 输入：

```
http://192.168.3.218:8123/
```

说明：
- 出现「不安全 / 未使用 HTTPS」的警告时点**继续 / I accept the risks**即可（个人自用源，仅在家庭 WiFi 内，无风险）
- 手机必须和电脑连**同一个 WiFi**
- 电脑必须开机（已设置开机自启，登录后自动运行）
- 如果电脑 IP 变了（路由器 DHCP），用 `ipconfig` 查看新的 IPv4 地址，把上面的 IP 替换掉即可

## 本地服务的启停

- 自动启动：开机登录后自动运行（Startup 文件夹里的 `jb-repo-server.bat`）
- 手动启动：运行 `python -m http.server 8123 --directory C:\Users\Administrator\jb-repo`
- 停止：任务管理器结束 `pythonw` 进程

## 可选：切换到公网托管（以后需要外网访问时）

仓库已按标准源结构构建，任意支持 HTTPS 的静态托管都能直接用：
- GitHub Pages：`https://<用户名>.github.io/jb-repo/`
- 或 Netlify / Vercel / Cloudflare Pages 拖拽上传 `jb-repo` 文件夹即可
