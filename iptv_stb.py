from playwright.sync_api import sync_playwright
import json
import requests

# 用户配置
UserID = "025开头的12位号码"
PassWord = "六位iptv密码"
stbId = "XXXXXXXXXXXXXXXXXX"
Macadress = "机顶盒MAC地址"
ipadress = "获取的iptv专网的IP地址"

# 代理配置
PROXY_SERVER = "socks5://127.0.0.1:1080"

# 从 CDN 获取 crypto-js（不走代理）
cryptojs = requests.get(
    "https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js",
    timeout=10
).text


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        proxy={
            "server": PROXY_SERVER
        }
    )

    context = browser.new_context(
        user_agent="B700-V2A|Mozilla|5.0|ztebw(Chrome)|1.2.0;Resolution(PAL,720p,1080i) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7"
    )

    page = context.new_page()

    # 响应监听 - 检测 frameset_builder.jsp 响应
    state = {"done": False}

    def on_response(response):
        print(f"响应已收到: {response.status}, {response.url}", flush=True)
        if "frameset_builder.jsp" in response.url:
            state["done"] = True

    page.on("response", on_response)

    # ✅ 1. 注入 CryptoJS
    page.add_init_script(cryptojs)

    # ✅ 2. 注入 Authentication（从外部 JS 文件加载）
    with open("authentication.js", "r", encoding="utf-8") as f:
        auth_script = f.read()

    # 替换占位符
    auth_script = auth_script.replace("__AccessMethod__", "dhcp")
    auth_script = auth_script.replace("__AccessUserName__", f"{UserID}@vod")
    auth_script = auth_script.replace("__UserID__", UserID)
    auth_script = auth_script.replace("__stbId__", stbId)
    auth_script = auth_script.replace("__ipadress__", ipadress)
    auth_script = auth_script.replace("__Macadress__", Macadress)
    auth_script = auth_script.replace("__PassWord__", PassWord)

    page.add_init_script(auth_script)

    print("打开认证页面", flush=True)
    # ✅ 3. 打开认证页面
    page.goto(
        f"http://itv.jsinfo.net:8298/auth?UserID={UserID}&Action=Login",
        wait_until="domcontentloaded"
    )

    # 等待 frameset_builder.jsp 响应
    while not state["done"]:
        page.wait_for_timeout(100)

    # 等待 JS 执行完成
    page.wait_for_timeout(3000)

    # 输出 Authentication.config 到文件
    config = page.evaluate("() => window.Authentication.config")
    with open("authentication_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("Authentication已保存到 authentication_config.json", flush=True)

    browser.close()
