# 自用插件源（personal-jb-repo）

个人越狱插件源。已上线 **GitHub Pages 公网托管**，同时保留**局域网模式**作为离线备用。

## 目录结构

| 文件/目录 | 作用 |
|---|---|
| `debs/` | 存放插件 .deb 文件（新增插件丢这里） |
| `Packages` / `Packages.bz2` / `Packages.xz` | 插件索引，由 `build_repo.py` 自动生成 |
| `Release` | 仓库元信息 + 全部索引的校验和 |
| `build_repo.py` | 构建脚本：扫描 debs/ → 重建索引（等价于 dpkg-scanpackages） |
| `publish_repo.py` | 发布脚本：把本地变更同步到 GitHub（Contents API，不依赖网页通道） |
| `CydiaIcon.png` | 仓库图标（可选） |

## 手机上添加源（公网，推荐）

Sileo / Zebra → 底部「源 / Sources」→ 右上角「+」→ 输入：

```
https://tlzypjy.github.io/jb-repo/
```

公网地址全球可访问：手机用流量、在外面都能装，电脑不用开机。

## 手机上添加源（局域网备用）

电脑开机且手机连同一 WiFi 时，也可以加：

```
http://192.168.3.218:8123/
```

出现「不安全 / 未使用 HTTPS」警告时点**继续**即可（仅家庭 WiFi 内使用）。

## 日常使用：添加新插件（三步）

1. 把 `xxx.deb` 放进 `debs/` 文件夹
2. 运行 `python build_repo.py`（重建索引与校验和）
3. 运行 `python publish_repo.py`（同步到 GitHub，约 10 秒完成）

发布脚本的令牌读取顺序：环境变量 `GH_TOKEN` → `C:\Users\Administrator\jb-repo.token` → 仓库内 `.token`。令牌 7 天过期，过期后重新生成并更新对应位置即可。

## 本地服务（局域网源）的启停

- 自动启动：开机登录后自动运行（Startup 文件夹 `jb-repo-server.bat`），监听 8123 端口
- 手动启动：`python -m http.server 8123 --directory C:\Users\Administrator\jb-repo`
- 停止：任务管理器结束 `pythonw` 进程
