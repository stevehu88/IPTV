# IPTV STB 认证脚本

模拟机顶盒认证流程，获取频道列表。

## 安装依赖

### 1. 安装 Python 依赖

```bash
pip install playwright requests
```

### 2. 安装 Playwright Chromium 浏览器

```bash
playwright install chromium
```

## 配置

在 `iptv_stb.py` 中修改以下配置：

| 字段 | 说明 | 示例 |
|------|------|------|
| `UserID` | 用户账号 |  |
| `PassWord` | 用户密码 |  |
| `stbId` | 机顶盒序列号 |  |
| `Macadress` | 机顶盒 MAC 地址（大写） | |
| `ipadress` | EPG 认证使用的 IP 地址 |  |
| `PROXY_SERVER` | SOCKS5 代理地址 | `socks5://127.0.0.1:1080` |

## 运行

```bash
python iptv_stb.py
```

## 输出

- `authentication_config.json` - Authentication 配置信息，包含频道列表
