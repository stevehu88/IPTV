# OpenWrt 上运行的 IPTV 抓取程序

## 概述

本目录包含在 OpenWrt 路由器上直接运行的 IPTV 播放列表抓取脚本。

## 前置条件

- 已按照 [openwrt_setup](../openwrt_setup/README.md) 完成路由器配置
- WAN 口已获取 IPTV 专网 IP 地址
- OpenWrt 已安装 `curl`、`openssl-util`、`xxd` 工具

## 脚本说明

### iptv_spider.sh

在 OpenWrt 上模拟机顶盒认证流程，获取频道列表并生成 M3U 播放列表。

**主要功能**：
- DES 加密认证
- 自动获取 WAN 口 IP 地址
- 登录 IPTV 平台获取频道数据
- 生成 M3U 格式播放列表

**配置**：

编辑脚本中的配置区：

```bash
USERID="XXXXXXXXX"      # IPTV 用户账号
PASSWORD="XXXXXXXXX"    # 用户密码
STBID="XXXXXXXXX"       # 机顶盒序列号
MAC="XXXXXXXXX"         # 机顶盒 MAC 地址（大写）
STBTYPE="B860AV2.1-T"   # 机顶盒型号
```

**运行**：

```bash
chmod +x iptv_spider.sh
./iptv_spider.sh
```

**输出**：

- `playlist.m3u` - M3U 格式播放列表

**输出示例**：

```
========== 开始IPTV播放源抓取 ==========
正在登录...
登录成功。
正在获取服务列表...
正在跳转至EAS页面...
正在获取EPG页面内容...
正在进行门户认证...
门户认证完成。
正在构建最终页面框架...
最终页面已生成: frameset_builder.jsp
正在生成播放列表...
已生成 playlist.m3u，共 XXX 个频道
========== 抓取流程结束 ==========
```

## 安装依赖

如果脚本无法运行，请安装所需工具：

```bash
opkg update
opkg install curl openssl-util xxd
```

## 注意事项

- 确保路由器已加入 IPTV 专网后再运行脚本
- 脚本会自动清理临时 Cookie 文件
- 生成的播放列表可直接导入 IPTV 播放器使用
