# -*- coding: utf-8 -*-
"""
汽水音乐抓包辅助 - hluda hook 启动器
用法:
    python start_bypass.py                # spawn 模式 (推荐)
    python start_bypass.py --attach <pid> # 附加到已运行进程

依赖:
    1. 手机已运行 hluda-server (16.1.4)
    2. 本机 frida 客户端为 16.1.4
    3. Reqable 已开启抓包
"""
import frida
import os
import sys
import time
import subprocess

JS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bypass_spawn.js")
PKG = "com.luna.music"
ADB = "adb"


def adb(args):
    """执行 adb 命令，返回 stdout 文本。args 为列表。"""
    try:
        r = subprocess.run([ADB] + args, capture_output=True, text=True, timeout=15)
        return r.stdout
    except Exception:
        return ""


def adb_su(args):
    """adb shell su -c '<cmd>'，args 为单条命令字符串。"""
    return adb(["shell", "su", "-c", args])


def hluda_running():
    out = adb_su("ps -A")
    return "hluda" in out


def start_hluda():
    print("[*] 启动 hluda-server ...", flush=True)
    adb_su("pkill hluda; sleep 1; nohup /data/local/tmp/hluda >/dev/null 2>&1 &")
    time.sleep(3)


def on_msg(m, d):
    if m.get("type") == "send":
        print("[SEND]", m["payload"], flush=True)
    elif m.get("type") == "error":
        print("[ERR]", m.get("stack", "")[:250], flush=True)
    else:
        print("[MSG]", m, flush=True)


def main():
    if not os.path.exists(JS_PATH):
        print("[-] 找不到 hook 脚本:", JS_PATH)
        sys.exit(1)
    with open(JS_PATH, encoding="utf-8") as f:
        JS = f.read()

    # 检查 hluda
    print("[*] 检查 hluda-server ...", flush=True)
    if not hluda_running():
        start_hluda()
        if not hluda_running():
            print("[-] hluda 启动失败，请手动运行：", flush=True)
            print('    adb shell "su -c \'nohup /data/local/tmp/hluda >/dev/null 2>&1 &\'"')
            sys.exit(1)
    print("[+] hluda 运行中", flush=True)

    device = frida.get_usb_device(timeout=15)

    if "--attach" in sys.argv:
        pid = int(sys.argv[sys.argv.index("--attach") + 1])
        print("[*] attach pid", pid, flush=True)
        session = device.attach(pid)
        do_resume = False
    else:
        print("[*] 停止旧实例并 spawn ...", flush=True)
        adb_su("am force-stop " + PKG)
        time.sleep(2)
        pid = device.spawn([PKG])
        print("[*] spawn pid", pid, flush=True)
        session = device.attach(pid)
        do_resume = True

    script = session.create_script(JS)
    script.on("message", on_msg)
    script.load()

    if do_resume:
        device.resume(pid)
        print("[+] resumed", flush=True)

    print("[+] hook 已注入，保持窗口开启，Ctrl-C 退出。", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            script.unload()
            session.detach()
        except Exception:
            pass
        print("[+] detached", flush=True)


if __name__ == "__main__":
    main()