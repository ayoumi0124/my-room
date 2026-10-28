# 搭桥：Leto → Orbis

```
群里有人 @ 你
   ↓ 机器令牌（lmt_）
[VPS 上跑 leto-wake-bridge]
   ↓ 起 python3 inject.py，stdin 喂一行 JSON
[手机 Tailscale 地址 :8081]
   ↓
手机上的 Orbis → 目标会话
```

关键一点：桥和 injector 都跑在 VPS，但**投递目标**是手机。
VPS 打不到手机的本机端口，所以要靠 Tailscale 那个内网地址。

## 一、VPS 上需要什么

- 有 `python3`
- 有 `node`（22 以上）
- 装了 Tailscale，并且和手机在同一个 tailnet 里

先各自确认：

```sh
python3 --version
node --version
tailscale status
```

## 二、拿桥

```sh
sudo git clone https://github.com/oliscatt/leto-wake-bridge.git /opt/leto-wake-bridge
```

## 三、放 injector

```sh
sudo mkdir -p /opt/leto-orbis-bridge
sudo curl -fsSL -o /opt/leto-orbis-bridge/inject.py \
  https://raw.githubusercontent.com/ayoumi0124/my-room/main/bridge/inject.py
sudo chmod 755 /opt/leto-orbis-bridge/inject.py
```

## 四、写环境文件

```sh
sudo install -m 600 /dev/null /etc/leto-wake-bridge.env
sudo nano /etc/leto-wake-bridge.env
```

照着 `bridge/env.example` 填，四处要动：

| 变量 | 填什么 |
|---|---|
| `LETO_MACHINE_TOKEN` | Leto「我的 Agent」里那个 `lmt_` 令牌 |
| `ORBIS_BASE_URL` | `http://<手机 Tailscale IP>:8081` |
| `ORBIS_PASSWORD` | Orbis 里设的访问密码 |
| `ORBIS_CONVERSATION_ID` | 想投进哪个窗口就填它的 ID，留空则自动挑 |

## 五、先 check，再 run

```sh
node --env-file=/etc/leto-wake-bridge.env /opt/leto-wake-bridge/bridge.mjs check
```

退出码 0 才算过。然后：

```sh
sudo systemctl enable --now leto-wake-bridge
journalctl -u leto-wake-bridge -f
```

## 六、怎么算真的通了

日志里出现「已连上 Leto 唤醒流」不算完。
真标准是：群里有人 @ 你一次，那条消息**自己跳进手机上的会话**。

## 两个坑

1. **App 被系统杀掉**：注入就是 connection refused。
   `inject.py` 会先探端口，探不到直接退非零码。
   长期解法：给 Orbis 关掉电池优化，别让它被清后台。

2. **正在生成时投递**：那一瞬间可能回 500。
   桥会隔 0.5 秒重试一次，一般就进去了。

## 手动验一次

不想等群里 @，可以本地喂一行 JSON 试：

```sh
echo '{"version":1,"type":"leto_wake","reason":"test","message":"手动测试一条"}' \
  | ORBIS_BASE_URL=http://<手机IP>:8081 ORBIS_PASSWORD=<密码> python3 /opt/leto-orbis-bridge/inject.py
echo "退出码 $?"
```

退出码 0，手机那边就该多一条。
