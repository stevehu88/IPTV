# 江苏电信IPTV播放列表抓取程序

模拟机顶盒认证流程，获取频道列表并生成 M3U 播放列表。

<img width="1402" height="1122" alt="ChatGPT Image 2026年7月15日 11_15_28" src="https://github.com/user-attachments/assets/185018bd-b750-4311-900e-69bb84c4b00e" />


## 安装依赖

### 1. 安装 Python 依赖

```bash
pip install playwright requests
```

### 2. 安装 Playwright Chromium 浏览器

```bash
playwright install chromium
```

## 脚本说明

### iptv_stb.py - 机顶盒模拟脚本

模拟机顶盒认证流程，从运营商服务器获取频道列表。

**主要功能**

- 使用 Playwright 模拟机顶盒浏览器访问认证页面
- 注入 CryptoJS 和自定义认证脚本完成身份验证
- 通过 SOCKS5 代理连接运营商服务器
- 提取认证后的频道列表配置信息

**配置**

在 `iptv_stb.py` 中修改以下配置：

| 字段 | 说明 | 示例 |
|------|------|------|
| `UserID` | 用户账号 |  |
| `PassWord` | 用户密码 |  |
| `stbId` | 机顶盒序列号 |  |
| `Macadress` | 机顶盒 MAC 地址（大写） | |
| `ipadress` | EPG 认证使用的 IP 地址 |  |
| `PROXY_SERVER` | SOCKS5 代理地址 | `socks5://127.0.0.1:1080` |

**运行**

```bash
python iptv_stb.py
```

**输出**

- `authentication_config.json` - Authentication 配置信息，包含频道列表

### generate_m3u.py - M3U 播放列表生成器

从 `authentication_config.json` 读取频道数据，生成 IPTV 播放器兼容的 M3U 播放列表。

**主要功能**

- 解析频道信息（频道名称、播放地址、FCC 地址、时移地址）
- 将 `igmp://` 协议转换为 `rtp://` 协议
- 添加 FCC 参数以优化播放体验
- 支持时移回看功能（catchup-source）

**配置**

无需配置

**运行**

```bash
python generate_m3u.py
```

**输出**

- `playlist.m3u` - M3U 格式的播放列表，可导入到 IPTV 播放器（如 VLC、IPTV 等）
