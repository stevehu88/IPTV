from playwright.sync_api import sync_playwright
import json
from pathlib import Path


# ======================
# 用户配置
# ======================
USER_ID = "025208527583"
PASSWORD = "922145"
STB_ID = "ED100599007040700000C09296E79601"
MAC_ADDRESS = "C0:92:96:E7:96:01"
IP_ADDRESS = "10.250.206.219"

AUTH_URL = f"http://itv.jsinfo.net:8298/auth?UserID={USER_ID}&Action=Login"

# ======================
# 代理配置
# ======================
PROXY_SERVER = "socks5://127.0.0.1:1080"

# ======================
# 文件路径
# ======================
BASE_DIR = Path(__file__).parent
CRYPTO_JS_PATH = BASE_DIR / "crypto-js.min.js"
AUTH_JS_PATH = BASE_DIR / "authentication.js"
MEDIAPLAYER_JS_PATH = BASE_DIR / "mediaplayer.js"
OUTPUT_PATH = BASE_DIR / "authentication_config.json"


def load_scripts():
    """加载并生成注入脚本"""
    cryptojs = CRYPTO_JS_PATH.read_text(encoding="utf-8")
    auth_template = AUTH_JS_PATH.read_text(encoding="utf-8")

    authjs = (
        auth_template
        .replace("__AccessMethod__", "dhcp")
        .replace("__AccessUserName__", f"{USER_ID}@vod")
        .replace("__UserID__", USER_ID)
        .replace("__stbId__", STB_ID)
        .replace("__ipadress__", IP_ADDRESS)
        .replace("__Macadress__", MAC_ADDRESS)
        .replace("__PassWord__", PASSWORD)
    )

    mediaplayerjs = MEDIAPLAYER_JS_PATH.read_text(encoding="utf-8")

    return cryptojs, authjs, mediaplayerjs


def run():
    cryptojs, authjs, mediaplayerjs = load_scripts()

    with sync_playwright() as p:
        print("🚀 启动 Chromium...", flush=True)

        browser = p.chromium.launch(
            headless=False,
            proxy={"server": PROXY_SERVER}
        )

        context = browser.new_context(
            user_agent=(
                "B700-V2A|Mozilla|5.0|ztebw(Chrome)|1.2.0;"
                "Resolution(PAL,720p,1080i) AppleWebKit/535.7 "
                "(KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7"
            )
        )

        # 注入 JS（建议在 new_page 前做）
        context.add_init_script(cryptojs)
        context.add_init_script(authjs)
        context.add_init_script(mediaplayerjs)

        page = context.new_page()

        print(f"🌐 打开认证页面: {AUTH_URL}", flush=True)

        page.goto(AUTH_URL, wait_until="domcontentloaded")

        
        # first_channel_play 
        # 可选：更优等待方式（比 sleep 更稳）
        page.wait_for_function(
            "() => window.Authentication && window.Authentication.CTCGetConfig('ShowPic') == 2",
        )

        config = page.evaluate("() => window.Authentication.config")

        OUTPUT_PATH.write_text(
            json.dumps(config, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"💾 已保存: {OUTPUT_PATH}", flush=True)

        browser.close()


if __name__ == "__main__":
    run()