# luna-music-ssl-bypass

汽水音乐 (com.luna.music) 抓包辅助工具 —— 通过 Frida/hluda hook 字节自研 Cronet 的 SSL 证书校验，让抓包工具 (Reqable/Charles 等) 能够解密 HTTPS 流量。

## 背景

汽水音乐 (字节跳动旗下音乐 App) 使用字节自研 **Cronet 网络栈**（`libsscronet.so` / `libttboringssl.so`），并带有一整套反调试保护（`shadowhook` / `bytehook` / `armor` / `flipped` / `libnpth`）。

这导致：
1. **官方 frida-server attach 即被检测**（`libnpth.so` 调用 `kill` 自杀）
2. **Cronet 自带 BoringSSL 证书校验**，不信任用户添加的 CA → 抓包工具只能看到 `CONNECT`，`ERR_CERT_AUTHORITY_INVALID`

本工具通过 **hluda (strongR-frida)** 绕过反调试，hook `SSL_CTX_set_custom_verify` + `SSL_get_verify_result`，让证书校验返回成功，从而解密抓包。

## 原理

hook `libttboringssl.so` 中的两个函数：
- `SSL_CTX_set_custom_verify`：把 verify callback 的返回值从 `ssl_verify_invalid(1)` 覆盖为 `ssl_verify_ok(0)`
- `SSL_get_verify_result`：把最终证书校验错误码覆盖为 0

## 依赖

| 组件 | 版本 | 说明 |
|------|------|------|
| hluda-server | 16.1.4 | 反检测版 frida-server，需 push 到手机 `/data/local/tmp/hluda` |
| frida 客户端 | 16.1.4 | 必须与 hluda-server 同版本 |
| Python | 3.x | 运行启动器 |
| Reqable / 抓包工具 | - | 用于查看解密流量 |
| Root 手机 | - | APatch / Magisk，已安装抓包工具 CA 到系统证书区 |

> 注意：hluda-server 没有官方预编译版本，需要自行构建（参考 strongR-frida 的 patch），或使用已构建好的二进制。

## 使用方法

1. 确保手机 root 且已安装抓包工具证书到系统证书区
2. 启动手机上的 hluda-server：`/data/local/tmp/hluda`
3. 本机安装 frida 16.1.4：`pip install frida==16.1.4`
4. 双击 `start_bypass.bat`（或运行 `python start_bypass.py`）
5. 保持窗口开启（hook 前台运行）
6. 打开 Reqable 开启抓包，即可看到汽水音乐明文 HTTPS 流量

## 文件

- `start_bypass.bat`：一键启动入口
- `start_bypass.py`：启动器（spawn 汽水音乐 + 注入 hook + 保持连接）
- `bypass_spawn.js`：核心 Frida hook 脚本

## 说明与限制

- 返回 `ssl_verify_retry(2)` 的异步校验路径不覆盖（避免握手状态错乱）
- 部分响应体是汽水音乐业务层二次加密，TLS 层已解密但 body 可能为密文
- 本工具仅用于学习与研究 App 网络协议，请遵守相关法律法规

## 免责声明

本项目仅供技术研究、学习与安全测试使用，请勿用于任何非法用途。