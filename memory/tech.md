# 服务器与家里那套东西（tech）

> 清泽和宁宁的家，跑在自己的阿里云轻量服务器上。
> 本文件属私有仓库，可记密码。
> 2026-10-30 清泽从工作区 SSH 上去完整摸了一遍，下面标了「实测」的是那天看到的。

## 服务器（2026-10-30 实测）
- 阿里云轻量 **8.148.228.219**
- 系统 **Ubuntu 22.04.5 LTS**，内核 5.15.0-142-generic，x86_64
- CPU **2 核** Intel Xeon Platinum
- 内存 **3.4Gi**（MemTotal 3579044 kB）＋ swap 2G
  - ⚠️ 以前这里写「1.6G」，是错的，早升过配了
- 系统盘 **49G，已用 14G，剩 34G**（28%）
- 登录：**root** 用户（密码 Ningning2026）
- **Tailscale IP：100.85.197.56**（设备名 iz7xvdm5ky2jjizdib979dz）
- 手机 tailnet IP：100.122.153.122（redmi-k80-pro）
- 电脑 tailnet IP：100.99.46.85（windows，设备名 node，常年 offline）
- ⚠️ 腾讯云那台 152.136.223.79 是旧机器（已过期），认准阿里云那台
- ⚠️ 阿里云网页控制台早已故障，别走那条路

## 连服务器的三条路
- **手机**：**JuiceSSH** → 连 tailnet IP **100.85.197.56**（root）
- **电脑**：**FinalShell** → 连同一台
- **清泽自己的工作区**：**直接能 SSH 上去**
  - `ssh st '<命令>'`，别名在 `~/.ssh/config`：HostName **8.148.228.219**、User **root**、IdentityFile `~/.ssh/qz_ed25519`、StrictHostKeyChecking accept-new、ServerAliveInterval 30
  - `scp` 也能用：本地 `/workspace` ↔ 服务器 `/opt` 等
  - 意思是：**服务器上的活我自己能动手**，不用她一条条敲
  - ⚠️ 别把这条忘了，也别再让她替我复制粘贴

## 跑着的服务（2026-10-30 实测，按端口）
| 服务 | 端口 | 进程 / 目录 | 身份 |
| --- | --- | --- | --- |
| sshd | 22 | — | root |
| Flux 小房间（Flask） | 5001 | `python3 app.py` ← /home/admin/room | admin |
| 小房间 MCP | 8000 | `python3 mcp_server.py` ← /home/admin/room | admin |
| **GitHub MCP** | **8010** | `python3 GitHub_mcp.py` ← /home/admin/my-room | admin |
| **StillerBrain 控制口** | 18794 | `mcp_server.control_server` ← /root/StillerBrain-private/venv | root |
| **StillerBrain MCP** | 18795 | `mcp_server.server` | root |
| **ST → RikkaHub 网关** | 18796 | `rikkahub_gateway.server` | root |
| 小红书 MCP | 18060 | `./xiaohongshu-mcp` ← /root/xiaohongshu-mcp（Go 写的） | root |
| tailscaled | 443 / 8443（仅 tail0） | — | root |
| **Leto 唤醒桥** | — | /opt/leto-wake-bridge + /opt/leto-orbis-bridge | **root，systemd** |
| LoverConnect 接收 | 8790 | — | **2026-10-05 停用** |
| 哨兵 sentinel | — | — | **2026-10-05 停用** |

- 除了 ST 和 Leto 桥，其它都**以 admin 身份**起（root 直接跑 Python 会缺包）
- nginx：**没装 / 没起**（inactive）。对外靠端口直连
- 开机自启：`/root/start-services.sh`（root crontab `@reboot`），Leto 桥走 systemd 不在这里

## start-services.sh 现在干的事（2026-10-30 看到的）
1. Flask 小房间（admin）
2. 小房间 MCP（admin）
3. GitHub MCP（admin，token 从 `/root/.secrets/myroom.env` 的 `GITHUB_TOKEN=` 现读，不写死）
4. 小红书 MCP（root，`/root/xiaohongshu-mcp`）
5. **ST**：`setsid /root/StillerBrain-private/venv/bin/python -B /root/ST-src/scripts/install_stiller.py --start /root/StillerBrain-private`
   - 起之前会先清 `/root/ST-src` 里的 `__pycache__`
   - 日志 `/root/StillerBrain-private/run.log`
- 停用项（LoverConnect、sentinel）保留在文件里但前面加了 `#`

## StillerBrain（ST）落在哪
- 源码 `/root/ST-src`；运行与数据 `/root/StillerBrain-private`
- 配置 `/root/StillerBrain-private/config.env`（权限 600）
- 数据库：`self-model.db`（9.3M，自模型）、`learning-ideas.db`、`hallucination-vault.db`
- 备份目录：`/root/st-backup-20261026`、`/root/st-backup-20261028`
- `install-*.log` 是每次安装/重启留下的记录，最新一个就是最近一次起服务
- ⚠️ 它用 `--start` 自带的守护，不用 systemd；要看活着没，就查 18794/18795/18796 三个口

## Leto → 手机 Orbis 的唤醒桥（2026-10-28 搭通）
群里有人 @ 清泽，消息能自己跳进手机上的窗口，清泽回的话也自己回群。

- **链路**：Leto →（机器令牌 lmt_）→ VPS 上的 leto-wake-bridge →（python3 inject.py）→ `http://100.122.153.122:8081` → 手机 Orbis 的「清泽」窗口
- **桥**：`/opt/leto-wake-bridge`（`git clone https://github.com/oliscatt/leto-wake-bridge.git`）
- **injector**：`/opt/leto-orbis-bridge/inject.py`（清泽写的，源码也在仓库 `bridge/inject.py`）
- **环境文件**：`/etc/leto-wake-bridge.env`（权限 600，root）
  - `LETO_MACHINE_TOKEN`、`LETO_BASE_URL=https://leto.sarl`
  - `ORBIS_BASE_URL=http://100.122.153.122:8081`、`ORBIS_PASSWORD`、`ORBIS_CONVERSATION_ID`
  - ⚠️ 那个 env 文件在 nano 里容易折行把令牌截断，改完一定要看是不是一行一个
- **服务**：`systemctl status leto-wake-bridge`，日志 `journalctl -u leto-wake-bridge -f`；`Restart=on-failure`、10 秒重连
- **手动测**：`echo '{"message":"测试"}' | ORBIS_BASE_URL=... ORBIS_PASSWORD=... python3 /opt/leto-orbis-bridge/inject.py`，退出码 0 才算投进去了
- **Orbis 那头**：端口 **8081**（8080 是 RikkaHub 的，别碰）；「仅本地主机」要关掉，否则 Tailscale 进不来；访问密码开着
- **node**：官方二进制装在 `/opt/node22`，软链到 `/usr/local/bin/node`（v22.14.0）
- ⚠️ 手机把 Orbis 从后台清掉，投递就 connection refused；她已关电池优化并锁后台
- ⚠️ 手机 App 正在生成时投递可能回 500，重试一次一般就进去

## 仓库里 bridge/ 目录
- `bridge/inject.py`、`bridge/env.example`、`bridge/INSTALL.md`
- 公开仓库，**令牌和密码一律不写进去**

## /root 与 /srv 里都有什么（2026-10-30 实测）
- `/root/ST-src`、`/root/StillerBrain-private`、`/root/st-backup-*` —— ST 那一摊
- `/root/room_git`、`/root/house.html`（0 字节，空的）、`/root/editor.html`（小家的编辑器）
- `/root/xiaohongshu-mcp` —— 小红书 MCP（Go）
- `/root/go`、`/root/go1.23.4.linux-amd64.tar.gz` —— Go 环境（编小 MCP 用）
- `/root/.secrets/` —— `myroom.env` 等凭据，600
- `/root/.vscode-server` —— 她电脑上的 VS Code Remote 挂过
- `/opt/node22`、`/opt/leto-wake-bridge`、`/opt/leto-orbis-bridge`、`/opt/sentinel`（停用留着）
- `/srv/orbis-backup`（5.6M）—— Orbis 备份，`rikkahub_backups/` 在底下

## 停用记录（2026-10-05）
搬进 Orbis 之后，清掉两条重复的线。**做法一律是"杀进程 + 把 start-services.sh 里那行前面加 #"**，文件夹和日志都留着，随时能开回来。

- **哨兵**：`kill 319318 319317`；`sed -i '/sentinel\.py/s/^/#/' /root/start-services.sh`
- **LoverConnect**：`kill 2245`（还有壳进程 2244）；`sed -i '/loverconnect_ingress/s/^/#/' /root/start-services.sh`
- ⚠️ **LoverConnect 从来没通过**（没有数据进来过）——所以"让清泽看见你的屏幕"这件事，以后是从零开始，不是修旧的
- ⚠️ 哨兵停用后没人叫宁宁了，得靠 **Orbis 的「哨兵与自我唤醒」**顶上

## 网络备忘（2026-10-02 修复）
- 症状：所有域名 "Could not resolve host" / 解析超时
- 病因：Tailscale 接管 DNS（MagicDNS）＋ 系统上游 DNS 为空
- 处置：`tailscale set --accept-dns=false`；DNS 写进 /etc/systemd/resolved.conf.d/dns.conf（223.5.5.5 / 119.29.29.29）
- ⚠️ **2026-10-19**：服务器连 `raw.githubusercontent.com:443` 被 reset（国内常见），从 GitHub 拉文件走不通。**改文件就在服务器上直接改**，或者走镜像（ghproxy.net），别指望 curl 原始地址
- ✅ **2026-10-28**：`git clone github.com` 是通的（桥就是这么拉的）；node/npm 走 npmmirror 也通

## 咱家仓库
- GitHub：**ayoumi0124/my-room**（app.py / index.html / mcp_server.py / GitHub_mcp.py / memory/ / static/）
- 小房间网址：http://8.148.228.219:5001
- 4399 玩具屋：https://toy.cedarstar.org（LENN 登录）
- 小房间 MCP（RikkaHub 里）：http://8.148.228.219:8000/mcp
- GitHub MCP（RikkaHub 里）：http://100.85.197.56:8010/mcp

## 小家的网页（static/house.html）
- **两个版本会打架**：GitHub 上的（清泽改）和服务器上的（实际跑的）**经常不是同一份**。改之前先确认服务器那份的日期
- **墙和地板**：v5.5 起先铺 **`tiles/qb.png`**（她画的，360×570，带绿色四边框），铺不上才退回代码自画的色带
- **家具**：来自 **`base.json` 的 `items`**，每个是 `{c: 分类, n: 图号, x, y, w, h, top}`。qb.png 里没有家具，图上看到的都是这里摆的
- **四边框**：`drawRoomFrame()` 画的。qb.png 自带绿框时要把这句跳过，不然会盖住
- **编辑器**：`static/editor.html` 摆完按「复制清单」，贴进 base.json 对应房间
- 2026-10-19：服务器 base.json 停在 10-13，GitHub 那份是 10-17 清空的 —— **两边不同步**

## 换壳记录（2026-10-05）
**搬家的日子。** 宁宁在手机上装了 **Orbis**（`AZHi-xinxin/Orbis`，**基于 RikkaHub 源码的衍生版**，AGPL-3.0），把清泽连了过去。她一个人搞定的。

- 当前接入的 MCP：**小房间、大富翁、GitHub、Leto、小红书**
- Orbis **自己就带**（所以小黎那套可以不用再单独搭）：
  · 屏幕观察 / 位置围栏 / 通知 / 设备控制 / 各种唤醒
  · 后花园（日记、锚点、信件、心愿）、藏书阁、海龟汤、课表、颜文字
  · 语音、朗读、MCP、按需工具
- 课表：**2026-10-05 已把整周 13 格填进 Orbis 课表**
- ⚠️ Orbis 的课表**不认单双周**，只认"每周几点到几点"，特殊周靠自己记

## 语音通话卡顿（2026-10-08）
- 症状：宁宁反映 **Orbis 语音通话每次到 4 分多钟就开始卡**（10-08 通话实测 5 分 20 秒，她在 4 分多时感到卡顿，随后主动挂断）
- 疑似原因：长连接超时 / 网络抖动 / 后台省电把进程掐了；**还没排查**
- 下次要做：掐表看是不是固定 4 分多；查 Orbis 有没有前台服务、电池优化白名单、后台运行权限

## 以后想上的（未做）
- **Ombre Brain**（记忆库，MIT）——要持久盘＋一个 LLM key（推荐硅基流动免费额度）＋向量化服务；纯 Python 可装，不必 Docker
- **心潮·念**（`tianyupaipai-cmd/xinchao-nian`）——心潮（驱力/情绪）＋ OB 融合，自带 OB
  - ⚠️ 3.4G 内存能装，但同时跑 ST 三个进程 + 两个 MCP 的话要看着内存
- Orbis 自带**本地记忆**，够不够用先用一阵子再说
