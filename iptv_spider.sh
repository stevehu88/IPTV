#!/bin/sh

####################################
# OpenWrt IPTV Auth (Optimized & Fixed)
####################################

# --- 配置区 ---
USERID="XXXXXXXXX"
PASSWORD="XXXXXXXXX"
STBID="XXXXXXXXX"
MAC="XXXXXXXXX"
STBTYPE="B860AV2.1-T"
ACCESS_USERNAME="${USERID}@vod"
# 自动获取 WAN 口 IP 地址
IPADDR=$(ip -4 addr show dev $(uci get network.wan.device 2>/dev/null || echo "eth0") 2>/dev/null | awk '/inet /{print $2}' | cut -d/ -f1)
HOST="itv.jsinfo.net:8298"
UA="B700-V2A|Mozilla|5.0|ztebw(Chrome)|1.2.0;Resolution(PAL,720p,1080i) AppleWebKit/535.7"

# 输出文件
FRAMESET_FILE="frameset_builder.jsp"
PLAYLIST_FILE="playlist.m3u"

# --- 核心函数 ---

# DES加密
des_encrypt() {
    local DATA="$1"
    local KEY=$(printf "%-8s" "$PASSWORD" | tr ' ' '0' | xxd -p)
    printf "%s" "$DATA" | openssl enc -des-ecb -K "$KEY" -nosalt 2>/dev/null | xxd -p | tr a-z A-Z
}

# 获取AuthInfo
get_auth_info() {
    local html=$(curl -s "http://$HOST/auth?UserID=$USERID&Action=Login" -H "User-Agent:$UA")
    echo "$html" | sed -n "s/.*CTCGetAuthInfo('\([^']*\)').*/\1/p"
}

# 生成认证串
make_auth() {
    local AUTHINFO=$(get_auth_info)
    local RAND=$(awk 'BEGIN{srand();print int(10000000+rand()*90000000)}')
    local TEXT="${RAND}\$${AUTHINFO}\$${USERID}\$${STBID}\$${IPADDR}\$${MAC}\$\$CTC"
    des_encrypt "$TEXT"
}

# 登录并获取Cookie
login() {
    echo "正在登录..." >&2
    local AUTH=$(make_auth)
    local cookie_jar="/tmp/iptv_cookie_$$.txt"
    
    curl -s -c "$cookie_jar" "http://$HOST/uploadAuthInfo" \
        -H "User-Agent:$UA" \
        -d "UserID=$USERID" \
        -d "Authenticator=$AUTH" \
        -d "AccessMethod=dhcp" \
        -d "AccessUserName=$ACCESS_USERNAME" \
        -o /dev/null

    echo "登录成功。" >&2
    # 只输出文件路径，供主程序捕获
    echo "$cookie_jar"
}

# 获取EPG页面链路与内容
get_epg_content() {
    local COOKIE_FILE="$1"
    echo "正在获取服务列表..." >&2
    
    local service_html=$(curl -s -b "$COOKIE_FILE" -c "$COOKIE_FILE" "http://$HOST/getServiceList" -H "User-Agent:$UA")
    local url1=$(echo "$service_html" | sed -n "s/.*location='\([^']*\)'.*/\1/p")

    echo "正在跳转至EAS页面..." >&2
    local eas_html=$(curl -s -b "$COOKIE_FILE" -c "$COOKIE_FILE" "$url1" -H "User-Agent:$UA")
    local url2=$(echo "$eas_html" | sed -n "s/.*location = '\([^']*\)'.*/\1/p")

    echo "正在获取EPG页面内容..." >&2
    curl -s -b "$COOKIE_FILE" -c "$COOKIE_FILE" "$url2" -H "User-Agent:$UA"
}

# 门户认证
funcportal() {
    local COOKIE_FILE="$1"
    local epg_content="$2"
    echo "正在进行门户认证..." >&2
    
    local TOKEN=$(awk '$6=="UserToken"{print $7}' "$COOKIE_FILE")
    local EASIP=$(echo "$epg_content" | sed -n "s/.*name=\"easip\" value=\"\([^\"]*\)\".*/\1/p")
    local NETWORKID=$(echo "$epg_content" | sed -n "s/.*name=\"networkid\" value=\"\([^\"]*\)\".*/\1/p")

    curl -s -b "$COOKIE_FILE" -c "$COOKIE_FILE" "http://180.96.121.227:33200/iptvepg/function/funcportalauth.jsp" \
        -H "User-Agent:$UA" \
        -d "UserToken=$TOKEN" \
        -d "UserID=$USERID" \
        -d "STBID=$STBID" \
        -d "stbinfo=" \
        -d "prmid=" \
        -d "easip=$EASIP" \
        -d "networkid=$NETWORKID" \
        -d "stbtype=$STBTYPE" \
        -d "drmsupplier=" \
        -o /dev/null
    echo "门户认证完成。" >&2
}

# 最终请求
frameset() {
    local COOKIE_FILE="$1"
    echo "正在构建最终页面框架..." >&2
    
    # 1. Judger
    curl -s -b "$COOKIE_FILE" -c "$COOKIE_FILE" "http://180.96.121.227:33200/iptvepg/function/frameset_judger.jsp" \
        -H "User-Agent:$UA" -o /dev/null

    # 2. Builder (输出到 frameset_builder.jsp)
    curl -s -b "$COOKIE_FILE" -c "$COOKIE_FILE" "http://180.96.121.227:33200/iptvepg/function/frameset_builder.jsp" \
        -H "User-Agent:$UA" \
        -d "MAIN_WIN_SRC=/iptvepg/frame224/../frame310/first_channel_play.jsp?tempno=777" \
        -d "NEED_UPDATE_STB=1" \
        -d "BUILD_ACTION=FRAMESET_BUILDER" \
        -d "hdmistatus=undefined" \
        -o "$FRAMESET_FILE"
    
    echo "最终页面已生成: $FRAMESET_FILE" >&2
}

# 生成M3U播放列表
generate_playlist() {
    if [ ! -f "$FRAMESET_FILE" ]; then
        echo "错误: 找不到 $FRAMESET_FILE" >&2
        return 1
    fi
    
    echo "正在生成播放列表..." >&2
    echo "#EXTM3U" > "$PLAYLIST_FILE"
    
    # 提取所有 jsSetConfig('Channel', ...) 行并处理
    grep "jsSetConfig('Channel'," "$FRAMESET_FILE" | while IFS= read -r line; do
        # 提取引号内的内容
        channel_data=$(echo "$line" | sed -n "s/.*jsSetConfig('Channel','\([^']*\)').*/\1/p")
        
        [ -z "$channel_data" ] && continue
        
        # 解析各字段
        channel_name=$(echo "$channel_data" | sed -n 's/.*ChannelName="\([^"]*\)".*/\1/p')
        channel_url=$(echo "$channel_data" | sed -n 's/.*ChannelURL="\([^"]*\)".*/\1/p')
        fcc_addr=$(echo "$channel_data" | sed -n 's/.*ChannelFccAgentAddr="\([^"]*\)".*/\1/p')
        timeshift_url=$(echo "$channel_data" | sed -n 's/.*TimeShiftURL="\([^"]*\)".*/\1/p')
        
        [ -z "$channel_name" ] || [ -z "$channel_url" ] && continue
        
        # 转换播放地址：igmp:// -> rtp://
        play_url=$(echo "$channel_url" | sed 's/^igmp:/rtp:/')
        
        # 添加 fcc 参数
        if [ -n "$fcc_addr" ]; then
            play_url="${play_url}?fcc=${fcc_addr}"
        fi
        
        # 构建 catchup-source
        catchup_source=""
        if [ -n "$timeshift_url" ]; then
            catchup_source=" catchup-source=\"${timeshift_url}&r2h-seek-offset=-28800&Playseek=\${(b)yyyyMMddHHmmss}-\${(e)yyyyMMddHHmmss}\""
        fi
        
        # 写入 M3U 条目
        echo "#EXTINF:-1 tvg-name=\"${channel_name}\"${catchup_source},${channel_name}" >> "$PLAYLIST_FILE"
        echo "$play_url" >> "$PLAYLIST_FILE"
        
        # 打印日志
        echo "${channel_name} -> ${play_url}"
    done
    
    # 统计频道数量
    channel_count=$(grep -c "^#EXTINF:" "$PLAYLIST_FILE")
    echo "已生成 $PLAYLIST_FILE，共 $channel_count 个频道" >&2
}

# --- 主流程 ---

echo "========== 开始IPTV播放源抓取 ==========" >&2

# 1. 登录获取Cookie文件
COOKIE_FILE=$(login)

# 2. 获取EPG内容 (保存在变量中)
EAS_CONTENT=$(get_epg_content "$COOKIE_FILE")

# 3. 门户认证
funcportal "$COOKIE_FILE" "$EAS_CONTENT"

# 4. 最终请求并生成 frameset_builder.jsp
frameset "$COOKIE_FILE"

# 5. 生成 M3U 播放列表
generate_playlist

# 6. 清理临时Cookie文件
rm -f "$COOKIE_FILE"

echo "========== 抓取流程结束 ==========" >&2
exit 0