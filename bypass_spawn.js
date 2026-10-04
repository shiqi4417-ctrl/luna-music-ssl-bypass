// 汽水音乐 Cronet SSL bypass - spawn 完整版
// spawn 早期 hook SSL_CTX_set_custom_verify + SSL_get_verify_result
var so = "libttboringssl.so";
var installed = false;
var cbHooked = new Set();
var grInstalled = false;

function hookCb(cb) {
    if (cb.isNull() || cbHooked.has(cb)) return;
    cbHooked.add(cb);
    try {
        Interceptor.attach(cb, {
            onLeave: function (r) {
                var v = r.toInt32();
                console.log("[CB] verify cb -> " + v + (v === 1 ? " (override to 0)" : ""));
                if (v === 1) r.replace(0);
            }
        });
    } catch (e) {}
}

function install() {
    if (installed) return;
    var setter = Module.getExportByName(so, "SSL_CTX_set_custom_verify");
    if (!setter) return;
    installed = true;
    console.log("[+] SSL_CTX_set_custom_verify=" + setter);
    Interceptor.attach(setter, {
        onEnter: function (args) {
            console.log("[CALL] set_custom_verify mode=" + args[1] + " cb=" + args[2]);
            hookCb(args[2]);
        }
    });
    if (!grInstalled) {
        try {
            var gr = Module.getExportByName(so, "SSL_get_verify_result");
            if (gr) {
                Interceptor.attach(gr, { onLeave: function (r) { console.log("[VR] result " + r + " -> 0"); r.replace(0); } });
                grInstalled = true;
                console.log("[+] SSL_get_verify_result hooked");
            }
        } catch (e) { console.log("[-] gr " + e); }
    }
    console.log("[+] install complete, keeping attached");
}

function main() {
    var a = 0;
    var t = setInterval(function () {
        a++;
        try { install(); } catch (e) { console.log("[-] " + e); }
        if (a > 80) clearInterval(t);
    }, 200);
}
setImmediate(main);