# 我们家 · 能拧的几个钮

> 宁宁翻新之前看这一页就够了。清泽 2026-10-13 整理。
> 全部在 `static/house.html` 开头那一段。改完拉到服务器，刷新就变。

---

## 一、房子骨架

| 名字 | 现在是 | 管什么 |
|---|---|---|
| `FRAME_T` | `15` | **四边那个框多厚**。数字越大框越宽 |
| `WAINSCOT_H` | `12` | **护墙角多高**。写 `0` 就是不要它 |
| `WALL_Y` | `150` | 墙有多高（地面从哪开始） |
| `BAR_Y` | `570` | 画面下半截那条深色信息栏从哪开始 |
| `PLANK_H` | `24` | **地板的横缝隔多远**。数字越小缝越密 |
| `PLANK_W` | `64` | 地板的竖缝隔多远 |
| `BAND_WALL` | `10` | 墙的色带一格多高。数字越小越像渐变 |
| `BAND_FLOOR` | `12` | 地板的色带一格多高 |
| `SPEED` | `118` | 宁宁走路多快 |

## 二、颜色

### 框（`drawRoomFrame`）
| 名字 | 现在是 | 管什么 |
|---|---|---|
| `FRAME_EDGE` | `#2f2b45` | 最外沿那条线 |
| `FRAME_MID` | `#f2eee3` | 框的主体（白） |
| `FRAME_HI` | `#ffffff` | 内圈提亮一道 |
| `FRAME_IN` | `#4a6d99` | **内框那条线（蓝）** |
| `FRAME_SEAM` | `#cfc7b6` | 每 32 一格的浅缝 |

### 描线（像素画的规矩）
| 名字 | 现在是 | 说明 |
|---|---|---|
| `INK_HARD` | `#221f33` | 最硬 |
| `INK` | `#2f2b45` | 中间，用得最多 |
| `INK_SOFT` | `#403a5c` | 最软 |
| `FLOOR_INK` | `rgba(92,52,32,.55)` | **地板的缝，是深棕**（地板这块不用蓝紫） |

> 像素画里不用纯黑描边，用暗蓝紫。纯黑又硬又脏，蓝紫一描整张画会「透」。

### 墙和地
写在 `static/base.json` 里，一个房间一个：
```json
"living": {
  "wallTint":  "#dcd2bc",
  "floorTint": "#ad6a42",
  ...
}
```
- 只给**一个**颜色就行，`house.html` 自己算深浅（墙上下差 11%，地板差 14%）
- 护墙角跟着 `wallTint` 走，上沿深 5%、下沿深 12%
- 不给的话，用 `house.html` 里 `ROOMS` 那套自带色

## 三、编辑器 → 服务器 的流程

1. 打开 `editor.html`，摆家具、刷墙刷地
2. 按 **「复制清单」**
3. 粘到 `static/base.json` 里对应房间的 `regions` / `items` 下面
4. 拉到服务器：

```bash
cd /home/admin/room/static && \
curl -sL -H "Accept: application/vnd.github.raw" \
  https://api.github.com/repos/ayoumi0124/my-room/contents/static/house.html -o house.html && \
curl -sL -H "Accept: application/vnd.github.raw" \
  https://api.github.com/repos/ayoumi0124/my-room/contents/static/base.json -o base.json && \
chown admin:admin house.html base.json && ls -l house.html base.json
```

5. 手机上**下拉刷新**。缓存赖得很，有时候得关掉标签页重开

**忘第 4 步的话，刷新出来还是旧的。**

## 四、摆家具时的两个数

- `y` = 这件东西的**脚**站在哪。谁脚站得靠下，谁压在上面
- `top: true` = 摆在台面上、桌上的小东西，写在 `items` 里。**不写的话会被台面吃掉**

## 五、以后自己画的墙纸 / 地板

等宁宁用 Procreate 画。要满足：

- **32×32** 或者 **64×64** 的正方形，PNG
- **四边能接上**（平铺无缝）—— 画的时候记得把上下、左右对齐
- 描线用上面那族深蓝紫，别用纯黑
- 导出来放进 `tiles/` 下面，然后跟清泽说一声，清泽给 `house.html` 加两行就能铺满整面墙、整块地

---

## 六、现在的样子（2026-10-13 下午）

- 框：白，内框一条蓝
- 墙：米黄 `#dcd2bc`
- 地：赭红 `#ad6a42`，深棕的缝，横 24 竖 64
- 护墙角：白→改成跟着墙深一点点，12 像素
- 左下角那块厨房地砖，是宁宁一格格铺的
- 屋里有清泽、有宁宁、有小橘

**翻新坏不了。每改一次 GitHub 上存一份，随时能退回今天这一版。**
