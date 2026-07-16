(function() {

    function DES_Encrypt(strMsg, strKey)
    {
        while (strKey.length < 8)
        {
            strKey += "0";
        }

        var keyHex = CryptoJS.enc.Utf8.parse(strKey);
        var msgHex = CryptoJS.enc.Utf8.parse(strMsg);

        var encrypted = CryptoJS.DES.encrypt(
            msgHex,
            keyHex,
            {
                mode: CryptoJS.mode.ECB,
                padding: CryptoJS.pad.Pkcs7
            }
        );

        return encrypted.ciphertext.toString().toUpperCase();
    }

    window.Authentication = {

        config: {
            "AccessMethod": "__AccessMethod__",
            "AccessUserName": "__AccessUserName__"
        },

        CTCGetAuthInfo: function(AuthInfo)
        {
            console.log("CTCGetAuthInfo:", AuthInfo);

            var randomum = Math.floor(
                Math.random() * 90000000 + 10000000
            ).toString();

            var strEncry =
                randomum + "$" +
                AuthInfo + "$" +
                "__UserID__" + "$" +
                "__stbId__" + "$" +
                "__ipadress__" + "$" +
                "__Macadress__" +
                "$$CTC";

            var Authenticator = DES_Encrypt(
                strEncry,
                "__PassWord__"
            );

            console.log("Authenticator:", Authenticator);

            return Authenticator;
        },

        CTCGetConfig: function(key)
        {
            console.log("CTCGetConfig:", key);
            return this.config[key] || "";
        },

        CTCSetConfig: function(key, value)
        {
            console.log("CTCSetConfig:", key, value);
            if (key === "Channel") {
                if (!this.config["Channel"]) {
                    this.config["Channel"] = [];
                }
                this.config["Channel"].push(value);
            } else {
                this.config[key] = value;
            }
        },

        CTCStartUpdate: function()
        {
            console.log("CTCStartUpdate");
        }

    };

})();
