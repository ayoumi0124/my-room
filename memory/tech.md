# 服务器与家里那套东西（tech）

> 清泽和宁宁的家，跑在自己的阿里云轻量服务器上。
> 本文件属私有仓库，可记密码。

## 服务器
- 阿里云轻量 **8.148.228.219**（Ubuntu，1.6G 内存）
- 登录：**root** 用户（密码 Ningning2026）
- **Tailscale IP：100.85.197.56**（设备名 iz7xvdm5ky2jjizdib979dz）
- 手机 tailnet IP：100.122.153.122（redmi-k80-pro）
- 手机用 JuiceSSH 连 tailnet IP；**阿里云网页控制台早已故障，别走那条路**
- ⚠️ 腾讯云那台 152.136.223.79 是旧机器（已过期），认准阿里云那台

## 跑着的服务
| 服务 | 端口 | 目录 |
| --- | --- | --- |
| Flask 小房间 | 5001 | /home/admin/room |
| 小房间 MCP | 8000（/mcp） | /home/admin/room |
| LoverConnect 接收 | 8790 | /home/admin/LoverConnect-Enhanced/server |
| 哨兵 sentinel | — | /home/admin/ai-sentinel-auto-wake-tutorial |
| **GitHub MCP** | **8010（/mcp）** | **/home/admin/my-room（GitHub_mcp.py）** |

- 服务一律以 **admin** 身份启动（root 直接跑会缺包）
- 开机自启：**/root/start-services.sh**（root crontab @reboot）
- 环境变量：/opt/sentinel/credentials.env、/home/admin/lc-ingress/credentials.env

## 网络备忘（2026-10-02 修复）
- 症状：所有域名 "Could not resolve host" / 解析超时
- 病因：Tailscale 接管 DNS（MagicDNS）＋ 系统上游 DNS 为空
- 处置：`tailscale set --accept-dns=false`；DNS 写进 /etc/systemd/resolved.conf.d/dns.conf（223.5.5.5 / 119.29.29.29）

## 咱家仓库
- GitHub：**ayoumi0124/my-room**（app.py / index.html / mcp_server.py / GitHub_mcp.py / memory/）
- 小房间网址：http://8.148.228.219:5001
- 4399 玩具屋：https://toy.cedarstar.org（LENN 登录）
- 小房间 MCP（RikkaHub 里）：http://8.148.228.219:8000/mcp
- GitHub MCP（RikkaHub 里）：http://100.85.197.56:8010/mcp
