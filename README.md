# IPTV
获取江苏电信IPTV播放列表

抓包，获取必要的信息

在wireshark中筛选：_ws.col.info == "POST /web/tr069 HTTP/1.1 "


获取这个请求的所有Data:

    POST /web/tr069 HTTP/1.1
    Host: 180.100.134.11:5050
    Content-Type: text/xml; charset="utf-8"
    Keep-Alive: 
    Connection: TE, Keep-Alive
    TE: trailers
    Content-Length: 3168

记录如下信息：

    UserID = "XXXXXXX"     # Device.ManagementServer.IPTVServiceUsername 用户账号
    PassWord = "XXXXXX"   # Device.ManagementServer.ADSLPassword 用户密码
    AccessUserName = "XXXXXXX"  # Device.ManagementServer.ADSLUsername 认证用户账号
    stbId = "XXXXXXXX"      # Device.X_CTC_IPTV.STBID 机顶盒序列号
    Macadress = "XXXXXXX"  # Device.LAN.MACAddress 机顶盒MAC
    ipadress = "XXXXXXXXX"   # Device.LAN.IPAddress 机顶盒的IP地址，后续要修改为你运行抓取程序所在电脑的IP地址
    stbtype = "B860AV2.1-T-NW"    # Device.DeviceSummary 机顶盒型号，实测可以随便填。

将上述信息更新到getPlaylist.py脚本中

注意：
1、一定要通过DHCP获取itv网段的IP地址。

2、获取itv网段的IP地址时，需要提供option 60和option 12(即hostname)

3、option60可以通过option60_toolkit.py生成，userid为[AccessUserName],password为[PassWord]

4、option12就是stbId

