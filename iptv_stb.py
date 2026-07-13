from playwright.sync_api import sync_playwright

import requests

UserID = "025开头的12位号码"
PassWord = "六位iptv密码"
stbId = "XXXXXXXXXXXXXXXXXX"
Macadress = "机顶盒MAC地址"
ipadress = "获取的iptv专网的IP地址"


# 从 CDN 获取 crypto-js
cryptojs = requests.get(
    "https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"
).text


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        # proxy={
        #     "server": "socks5://127.0.0.1:1080"
        # }
    )

    context = browser.new_context(
        user_agent="B700-V2A|Mozilla|5.0|ztebw(Chrome)|1.2.0;Resolution(PAL,720p,1080i) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7"
    )

    page = context.new_page()

    # 响应监听 - 检测 frameset_builder.jsp 响应
    state = {"done": False}

    def on_response(response):
        if "frameset_builder.jsp" in response.url:
            print("[frameset_builder.jsp] 响应已收到", flush=True)
            state["done"] = True

    page.on("response", on_response)

    # ✅ 1. 注入 CryptoJS
    page.add_init_script(cryptojs)

    # ✅ 2. 注入 Authentication（同步实现）
    page.add_init_script(f"""
    (function() {{

        function DES_Encrypt(strMsg, strKey)
        {{
            while (strKey.length < 8)
            {{
                strKey += "0";
            }}

            var keyHex = CryptoJS.enc.Utf8.parse(strKey);
            var msgHex = CryptoJS.enc.Utf8.parse(strMsg);

            var encrypted = CryptoJS.DES.encrypt(
                msgHex,
                keyHex,
                {{
                    mode: CryptoJS.mode.ECB,
                    padding: CryptoJS.pad.Pkcs7
                }}
            );

            return encrypted.ciphertext.toString().toUpperCase();
        }}

        window.Authentication = {{

            config: {{
                "AccessMethod": "dhcp",
                "AccessUserName": "{UserID}@vod"
            }},

            CTCGetAuthInfo: function(AuthInfo)
            {{
                console.log("CTCGetAuthInfo:", AuthInfo);

                var randomum = Math.floor(
                    Math.random() * 90000000 + 10000000
                ).toString();

                var strEncry =
                    randomum + "$" +
                    AuthInfo + "$" +
                    "{UserID}" + "$" +
                    "{stbId}" + "$" +
                    "{ipadress}" + "$" +
                    "{Macadress}" +
                    "$$CTC";

                var Authenticator = DES_Encrypt(
                    strEncry,
                    "{PassWord}"
                );

                console.log("Authenticator:", Authenticator);

                return Authenticator;
            }},

            CTCGetConfig: function(key)
            {{
                console.log("CTCGetConfig:", key);
                return this.config[key] || "";
            }},

            CTCSetConfig: function(key, value)
            {{
                console.log("CTCSetConfig:", key, value);
                if (key === "Channel") {{
                    if (!this.config["Channel"]) {{
                        this.config["Channel"] = [];
                    }}
                    this.config["Channel"].push(value);
                }} else {{
                    this.config[key] = value;
                }}
            }},

            CTCStartUpdate: function()
            {{
                console.log("CTCStartUpdate");
            }}

        }};

    }})();
    """)

    # ✅ 3. 打开认证页面
    page.goto(
        f"http://itv.jsinfo.net:8298/auth?UserID={UserID}&Action=Login",
        wait_until="domcontentloaded"
    )

    # 等待 frameset_builder.jsp 响应
    while not state["done"]:
        page.wait_for_timeout(100)

    page.wait_for_timeout(3000)

    # 输出 Authentication.config 到文件
    config = page.evaluate("() => window.Authentication.config")
    with open("authentication_config.json", "w", encoding="utf-8") as f:
        import json
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("[config] 已保存到 authentication_config.json", flush=True)

    browser.close()
