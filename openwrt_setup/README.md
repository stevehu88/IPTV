# OpenWrt 路由器 IPTV 专网配置

## 概述

本目录用于配置 OpenWrt 路由器，模拟机顶盒的 DHCP 认证过程，使 WAN 口获取 IPTV 专网 IP 地址，从而访问 IPTV 专网资源。

## 前置条件

- OpenWrt 路由器
- 机顶盒信息：
  - hostname（机顶盒主机名）
  - IPTV 密码（6 位数字）
  - IPTV 账号

## 工具说明

### option60_toolkit.py

DHCP Option 60 生成工具，基于中国电信 IPTV 技术规范实现。

**功能**：
- 生成 Option 60 加密字段
- 解密 Option 60 字段
- 验证密码是否正确

**依赖**：

```bash
pip install pycryptodome
```

**使用方法**：

1. 修改脚本中的配置：
   ```python
   userid = "XXXXXXXXXXXX@vod"  # IPTV 账号
   password = "XXXXXX"          # IPTV 密码（6 位数字）
   ```

2. 运行脚本生成 Option 60 字段：
   ```bash
   python option60_toolkit.py
   ```

3. 输出示例：
   ```
   Option60: 00001F3901XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

## 配置步骤

### 1. 生成 Option 60 字段

使用 `option60_toolkit.py` 生成加密的 Option 60 十六进制数据。

### 2. 配置 OpenWrt

SSH 登录 OpenWrt 后台，执行以下命令：

```bash
# 设置 hostname（机顶盒主机名）
uci set network.wan.hostname='机顶盒的hostname'

# 设置 Option 60 字段
uci set network.wan.sendopts='0x3c:生成的Option60十六进制数据'

# 保存配置
uci commit network

# 重启 WAN 接口
ifdown wan
ifup wan
```

### 3. 验证配置

```bash
ifconfig
```

确认 WAN 口已获取 IPTV 专网 IP 地址（通常为 `10.x.x.x` 或 `100.x.x.x` 网段）。

## 注意事项

- Option 60 字段包含加密的用户信息，请妥善保管
- 如果无法获取 IP，请检查密码和账号是否正确
- 部分地区可能需要额外的认证参数
