# -*- coding:utf-8 -*-
import requests
import re
import json
import random
import binascii
import time
from urllib.parse import urlparse, parse_qs
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

# 日志设置
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# SOCKS5代理设置
SOCKS5_PROXY = "socks5://127.0.0.1:1080"
PROXIES = {
    'http': SOCKS5_PROXY,
    'https': SOCKS5_PROXY
}

UserID = "XXXXXXXXX"     # Device.ManagementServer.IPTVServiceUsername 用户账号
PassWord = "XXXXXXXXX"   # Device.ManagementServer.ADSLPassword 用户密码
AccessUserName = "XXXXXXXXX"  # Device.ManagementServer.ADSLUsername 认证用户账号
stbId = "XXXXXXXXX"      # Device.X_CTC_IPTV.STBID 机顶盒序列号
Macadress = "XXXXXXXXX"  # Device.LAN.MACAddress 机顶盒MAC（注意大写）
ipadress = "XXXXXXXXX"   # Device.LAN.IPAddress EPG认证使用的IP地址（根据路由表更新）
stbtype = "B860AV2.1-T-NW"    # 机顶盒型号
filepath = r"playlist.json"

# 自定义请求函数，添加日志
def logged_request(method, url, **kwargs):
    """带日志的请求函数"""
    start_time = time.time()
    logger.info(f"发送 {method.upper()} 请求: {url}")
    
    if 'headers' in kwargs:
        logger.debug(f"请求头: {kwargs['headers']}")
    if 'data' in kwargs:
        logger.debug(f"请求数据: {kwargs['data']}")
    if 'proxies' in kwargs and kwargs['proxies']:
        logger.debug(f"使用代理: {kwargs['proxies']}")
    
    try:
        response = requests.request(method, url, **kwargs)
        elapsed = time.time() - start_time
        logger.info(f"请求完成: {url} - 状态码: {response.status_code} - 耗时: {elapsed:.2f}s")
        logger.debug(f"响应头: {dict(response.headers)}")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"请求失败: {url} - 错误: {e} - 耗时: {elapsed:.2f}s")
        raise


def extract_all_channels(js_text):
    """
    从 JavaScript 代码中提取频道信息（完整字段）
    参数:
        js_text: 包含频道数据的 JavaScript 代码文本
    返回:
        频道列表，包含所有字段的完整频道信息
    """
    try:
        logger.info("开始解析频道数据（完整字段）")
        channel_pattern = r"jsSetConfig\('Channel','(.*?)'\)"
        channel_matches = re.findall(channel_pattern, js_text, re.DOTALL)
        logger.info(f"找到 {len(channel_matches)} 个频道匹配项")
        
        result = []
        for match in channel_matches:
            # 提取所有字段
            channel_id_match = re.search(r'ChannelID="([^"]*)"', match)
            channel_name_match = re.search(r'ChannelName="([^"]*)"', match)
            user_channel_id_match = re.search(r'UserChannelID="([^"]*)"', match)
            channel_url_match = re.search(r'ChannelURL="([^"]*)"', match)
            time_shift_match = re.search(r'TimeShift="([^"]*)"', match)
            channel_sdp_match = re.search(r'ChannelSDP="([^"]*)"', match)
            time_shift_url_match = re.search(r'TimeShiftURL="([^"]*)"', match)
            channel_log_url_match = re.search(r'ChannelLogURL="([^"]*)"', match)
            channel_logo_url_match = re.search(r'ChannelLogoURL="([^"]*)"', match)
            position_x_match = re.search(r'PositionX="([^"]*)"', match)
            position_y_match = re.search(r'PositionY="([^"]*)"', match)
            begin_time_match = re.search(r'BeginTime="([^"]*)"', match)
            interval_match = re.search(r'Interval="([^"]*)"', match)
            lasting_match = re.search(r'Lasting="([^"]*)"', match)
            channel_type_match = re.search(r'ChannelType="([^"]*)"', match)
            channel_purchased_match = re.search(r'ChannelPurchased="([^"]*)"', match)
            time_shift_length_match = re.search(r'TimeShiftLength="([^"]*)"', match)
            telecomcode_match = re.search(r'telecomcode="([^"]*)"', match)
            channel_fcc_server_addr_match = re.search(r'ChannelFCCServerAddr="([^"]*)"', match)
            channel_fcc_agent_addr_match = re.search(r'ChannelFccAgentAddr="([^"]*)"', match)
            
            # 构建完整的频道信息字典
            channel_info = {}
            
            # 添加所有找到的字段
            if channel_id_match:
                channel_info['ChannelID'] = channel_id_match.group(1)
            if channel_name_match:
                channel_info['ChannelName'] = channel_name_match.group(1)
            if user_channel_id_match:
                channel_info['UserChannelID'] = user_channel_id_match.group(1)
            if channel_url_match:
                channel_info['ChannelURL'] = channel_url_match.group(1)
            if time_shift_match:
                channel_info['TimeShift'] = time_shift_match.group(1)
            if channel_sdp_match:
                channel_info['ChannelSDP'] = channel_sdp_match.group(1)
            if time_shift_url_match:
                channel_info['TimeShiftURL'] = time_shift_url_match.group(1)
            if channel_log_url_match:
                channel_info['ChannelLogURL'] = channel_log_url_match.group(1)
            if channel_logo_url_match:
                channel_info['ChannelLogoURL'] = channel_logo_url_match.group(1)
            if position_x_match:
                channel_info['PositionX'] = position_x_match.group(1)
            if position_y_match:
                channel_info['PositionY'] = position_y_match.group(1)
            if begin_time_match:
                channel_info['BeginTime'] = begin_time_match.group(1)
            if interval_match:
                channel_info['Interval'] = interval_match.group(1)
            if lasting_match:
                channel_info['Lasting'] = lasting_match.group(1)
            if channel_type_match:
                channel_info['ChannelType'] = channel_type_match.group(1)
            if channel_purchased_match:
                channel_info['ChannelPurchased'] = channel_purchased_match.group(1)
            if time_shift_length_match:
                channel_info['TimeShiftLength'] = time_shift_length_match.group(1)
            if telecomcode_match:
                channel_info['telecomcode'] = telecomcode_match.group(1)
            if channel_fcc_server_addr_match:
                channel_info['ChannelFCCServerAddr'] = channel_fcc_server_addr_match.group(1)
            if channel_fcc_agent_addr_match:
                channel_info['ChannelFccAgentAddr'] = channel_fcc_agent_addr_match.group(1)
            
            # 只有在有基本频道信息时才添加到结果中
            if channel_info and 'ChannelName' in channel_info:
                result.append(channel_info)
                logger.debug(f"解析到频道: {channel_info.get('ChannelName', '未知')} - ID: {channel_info.get('ChannelID', '未知')}")
            else:
                logger.warning(f"跳过无效的频道数据: {match[:100]}...")
        
        logger.info(f"成功解析 {len(result)} 个频道（完整字段）")
        return result
    except Exception as e:
        logger.error(f"extract_all_channels失败: {e}")
        return None


def DesEncrypt(strMsg, strKey):
    try:
        logger.debug(f"DES加密 - 明文: {strMsg}, 密钥: {strKey}")
        keyappend = 8 - len(strKey)
        if keyappend > 0:
            strKey = strKey + "0" * keyappend
        key_bytes = strKey.encode("utf-8")
        msg_bytes = strMsg.encode("utf-8")
        padded_msg = pad(msg_bytes, DES.block_size)
        cipher = DES.new(key_bytes, DES.MODE_ECB)
        encrypted = cipher.encrypt(padded_msg)
        result = binascii.hexlify(encrypted).decode("utf-8").upper()
        logger.debug(f"DES加密结果: {result}")
        return result
    except Exception as e:
        logger.error(f"DesEncrypt失败: {e}")
        return None


def DesDecrypt(encrypted_msg, strKey):
    try:
        logger.debug(f"DES解密 - 密文: {encrypted_msg}, 密钥: {strKey}")
        keyappend = 8 - len(strKey)
        if keyappend > 0:
            strKey = strKey + "0" * keyappend
        key_bytes = strKey.encode("utf-8")
        encrypted_bytes = binascii.unhexlify(encrypted_msg.lower())
        cipher = DES.new(key_bytes, DES.MODE_ECB)
        decrypted = unpad(cipher.decrypt(encrypted_bytes), DES.block_size)
        result = decrypted.decode("utf-8")
        logger.debug(f"DES解密结果: {result}")
        return result
    except Exception as e:
        logger.error(f"DesDecrypt失败: {e}")
        return None


def save_response_for_debug(response_text, filename="debug_response.txt"):
    """保存响应内容以便调试"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response_text)
        logger.info(f"已将响应内容保存到 {filename} 文件，大小: {len(response_text)} 字符")
        return filename
    except Exception as e:
        logger.error(f"保存响应内容失败: {e}")
        return None


def CTCGetAuthInfo():
    try:
        header = {
            "Host": "itv.jsinfo.net:8298",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "B700-V2A|Mozilla|5.0|ztebw(Chrome)|1.2.0;Resolution(PAL,720p,1080i) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "X-Requested-With": "com.itv.android.iptv"
        }
        url = f"http://itv.jsinfo.net:8298/auth?UserID={UserID}&Action=Login"
        r = logged_request('GET', url, headers=header, proxies=PROXIES)
        AuthInfo = re.search(r"CTCGetAuthInfo\('(.*?)'\);", r.text).group(1)
        logger.info(f"获取到AuthInfo: {AuthInfo}")
        return AuthInfo
    except Exception as e:
        logger.error(f"CTCGetAuthInfo失败: {e}")
        return None


def getAuthenticator():
    try:
        randomum = str(random.randint(10000000, 99999999))
        logger.debug(f"生成随机数: {randomum}")
        AuthInfo = CTCGetAuthInfo()
        if not AuthInfo:
            logger.error("无法获取AuthInfo")
            return None
            
        strEncry = f"{randomum}${AuthInfo}${UserID}${stbId}${ipadress}${Macadress}$$CTC"
        logger.debug(f"待加密字符串: {strEncry}")
        strKey = PassWord
        Authenticator = DesEncrypt(strEncry, strKey)
        if Authenticator:
            logger.info(f"生成Authenticator: {Authenticator}")
        else:
            logger.error("DES加密失败")
        return Authenticator
    except Exception as e:
        logger.error(f"getAuthenticator失败: {e}")
        return None


def getUserToken():
    try:
        Authenticator = getAuthenticator()
        header = {
            "Host": "itv.jsinfo.net:8298",
            "Connection": "keep-alive",
            "Pragma": "no-cache",            "Cache-Control": "no-cache",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Origin": "http://itv.jsinfo.net:8298",
            "User-Agent": "B700-V2A|Mozilla|5.0|ztebw(Chrome)|1.2.0;Resolution(PAL,720p,1080i) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": f"http://itv.jsinfo.net:8298/auth?UserID={UserID}&Action=Login",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "X-Requested-With": "com.itv.android.iptv"
        }
        data = {
            "UserID": UserID,
            "Authenticator": Authenticator,
            "AccessMethod": "dhcp",
            "AccessUserName": AccessUserName
        }
        url = f"http://itv.jsinfo.net:8298/uploadAuthInfo"
        r = logged_request('POST', url, headers=header, data=data, proxies=PROXIES)
        cookies = r.cookies
        UserToken = cookies.get("UserToken")
        logger.info(f"获取到UserToken: {UserToken}")
        return UserToken
    except Exception as e:
        logger.error(f"getUserToken失败: {e}")
        return None


def getJSESSIONID():
    try:
        UserToken = getUserToken()
        header = {
            "Host": "itv.jsinfo.net:8298",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "B700-V2A|Mozilla|5.0|ztebw(Chrome)|1.2.0;Resolution(PAL,720p,1080i) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
            "Cookie": f"UserToken={UserToken}",
            "Referer": "http://itv.jsinfo.net:8298/getServiceList",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "X-Requested-With": "com.itv.android.iptv"
        }
        url = f"http://itv.jsinfo.net:8298/getServiceList"
        r = logged_request('GET', url, headers=header, proxies=PROXIES)
        url = re.search(r"location='(.*?)';", r.text).group(1)
        logger.info(f"重定向URL1: {url}")
        
        header.update({"Host": "eas.itv.jsinfo.net:33200"})
        header.pop("Cookie")
        r = logged_request('GET', url, headers=header, proxies=PROXIES)
        url = re.search(r"location = '(.*?)';", r.text).group(1)
        logger.info(f"重定向URL2: {url}")
        
        parsed_url = urlparse(url)
        epgurl = parsed_url.netloc
        header.update({"Host": f"{epgurl}"})
        r = logged_request('GET', url, headers=header, proxies=PROXIES)
        cookies = r.cookies
        JSESSIONID = cookies.get("JSESSIONID")
        logger.info(f"获取到JSESSIONID: {JSESSIONID}")
        return UserToken, JSESSIONID, url
    except Exception as e:
        logger.error(f"getJSESSIONID失败: {e}")
        return "", "", ""


def main():
    try:
        UserToken, JSESSIONID, Refererurl = getJSESSIONID()
        if not UserToken or not JSESSIONID:
            logger.error("获取UserToken或JSESSIONID失败")
            return None
            
        parsed_url = urlparse(Refererurl)
        query_params = parse_qs(parsed_url.query)
        easip = query_params.get('easip', [None])[0]
        netloc = parsed_url.netloc
        logger.info(f"解析到netloc: {netloc}, easip: {easip}")
        
        session = requests.session()
        session.proxies = PROXIES  # 设置session的代理
        
        # 自定义session的请求方法以添加日志
        original_request = session.request
        def logged_session_request(method, url, **kwargs):
            start_time = time.time()
            logger.info(f"Session发送 {method.upper()} 请求: {url}")
            response = original_request(method, url, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"Session请求完成: {url} - 状态码: {response.status_code} - 耗时: {elapsed:.2f}s")
            return response
        
        session.request = logged_session_request
        
        header = {
            "Host": netloc,
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Origin": f"http://{netloc}",
            "User-Agent": "B700-V2A|Mozilla|5.0|ztebw(Chrome)|1.2.0;Resolution(PAL,720p,1080i) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": Refererurl,
            "Cookie": f"JSESSIONID={JSESSIONID}",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "X-Requested-With": "com.itv.android.iptv"
        }
        
        # 第一步: funcportalauth.jsp
        url1 = f"http://{netloc}/iptvepg/function/funcportalauth.jsp"
        data1 = {
            "UserToken": UserToken,
            "UserID": UserID,
            "STBID": stbId,
            "stbinfo": "",
            "prmid": "",
            "easip": easip,
            "networkid": "1",
            "stbtype": stbtype,
            "drmsupplier": ""
        }
        r1 = session.post(url1, headers=header, data=data1)
        
        # 第二步: frameset_judger.jsp
        url2 = f"http://{netloc}/iptvepg/function/frameset_judger.jsp"
        header.update({"Referer": f"http://{netloc}/iptvepg/function/frame.jsp"})
        data2 = {
            "picturetype": "1,3,5"  # 根据抓包修正: 原为1,2,3,4,5，实际应为1,3,5
        }
        r2 = session.post(url2, headers=header, data=data2)
        
        # 第三步: frameset_builder.jsp
        url3 = f"http://{netloc}/iptvepg/function/frameset_builder.jsp"
        header.update({"Referer": f"http://{netloc}/iptvepg/function/frameset_judger.jsp"})
        data3 = {
            "MAIN_WIN_SRC": "/iptvepg/frame224/../frame310/first_channel_play.jsp?tempno=777",
            "NEED_UPDATE_STB": "1",
            "BUILD_ACTION": "FRAMESET_BUILDER",
            "hdmistatus": "undefined"
        }
        r3 = logged_request('POST', url3, headers=header, data=data3, proxies=PROXIES)
        
        # 存储r3.text以便调试
        if r3.text:
            debug_file = save_response_for_debug(r3.text, "r3_debug.txt")
        
        if r3.text and 'CCTV16' in r3.text:
            logger.info("成功获取频道数据，开始解析")
            playlist = extract_all_channels(r3.text)
            channel_count = len(playlist) if playlist else 0
            logger.info(f"解析到 {channel_count} 个频道")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(playlist, f, ensure_ascii=False, indent=2)
            logger.info(f"成功保存到 {filepath}")
            return playlist
        else:
            logger.warning("响应为空或未找到CCTV16频道")
            if r3.text:
                logger.debug(f"响应内容前200字符: {r3.text[:200]}")
            return None
    except Exception as e:
        logger.error(f"main函数执行失败: {e}", exc_info=True)
        return None


if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("开始执行IPTV播放列表获取脚本")
    logger.info(f"用户ID: {UserID}, 机顶盒ID: {stbId}")
    logger.info(f"使用代理: {SOCKS5_PROXY}")
    logger.info("=" * 50)
    
    start_time = time.time()
    res = main()
    elapsed = time.time() - start_time
    
    logger.info("=" * 50)
    if res:
        logger.info(f"脚本执行成功! 耗时: {elapsed:.2f}秒")
    else:
        logger.error(f"脚本执行失败! 耗时: {elapsed:.2f}秒")
    logger.info("=" * 50)
