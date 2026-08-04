---
name: mobile-iot-device-security
description: 当目标为Android/iOS APP、微信/支付宝小程序、IoT设备/固件，或需要ADB调试、抓包突破、so层逆向、WebView/DeepLink/本地存储安全测试时调用。负责协议分析、导出组件、WebView漏洞、证书校验绕过、固件提取、硬编码凭证挖掘。
---

# mobile-iot-device-security — 移动端/IoT/固件专项深度挖掘

## 何时调用（触发条件）

- 拿到 APK/IPA/小程序包
- 需要抓包突破（证书绑定、双向认证）
- 需要逆向协议（protobuf/自定义加密）
- 发现 WebView、DeepLink、Intent、本地存储
- IoT 设备/固件分析

## 一、移动端专项挖掘（14.3）

### 抓包突破
- 证书绑定绕过：Frida + SSL Unpinning
- 双向认证：提取客户端证书
- 协议分析：protobuf/自定义协议解码

### 逆向分析
- jadx反编译 → 搜索API/密钥/加密逻辑
- so层分析 → IDA/Ghidra
- Hook关键函数 → Frida动态调试

### 常见问题
- 本地存储明文密码/token
- 日志泄露敏感信息
- WebView漏洞（JS接口暴露）
- DeepLink劫持
- Intent重定向

## 二、移动端/客户端类场景表（全景）

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| APP登录接口 | 协议分析/重放攻击 | 加密参数可逆、token无时效 |
| 本地存储 | 敏感信息泄露 | SharedPreferences/SQLite/Keychain明文存储 |
| WebView | JS接口暴露/XSS/中间人 | addJavascriptInterface、allowFileAccess |
| DeepLink/URL Scheme | 劫持/越权操作 | 未验证调用来源、参数注入 |
| 推送服务 | 消息伪造/信息泄露 | 推送ID可遍历、消息可伪造 |
| 剪贴板 | 敏感信息泄露 | 复制敏感数据到剪贴板 |
| 截图/录屏防护 | 绕过防护 | FLAG_SECURE绕过 |

## 三、Android 专项

- 导出组件（Activity/Service/ContentProvider/BroadcastReceiver）未授权调用
- WebView：addJavascriptInterface 暴露、allowFileAccess、file:// 域加载
- 明文存储：SharedPreferences/SQLite 中密码/token
- 证书校验：TrustManager 全信任、不校验主机名
- Intent 重定向：跨应用跳转携带敏感数据
- 可调试/备份标志：android:debuggable、allowBackup
- 签名校验绕过：重打包后签名校验缺失

## 四、iOS 专项

- Keychain 明文存储、iTunes 备份泄露
- URL Scheme 劫持（其他 App 可调用）
- 越狱检测绕过（影响分析时要区分）
- 证书固定绕过、ATS 配置宽松

## 五、小程序专项

- 反编译获取接口与密钥
- 鉴权不严、接口越权
- 本地存储敏感信息

## 六、IoT/固件专项（S类）

- 硬编码口令、调试接口（串口/UART、Telnet）
- 固件提取：解包分析（binwalk）、弱加密、未签名升级
- 云接口：设备与云端通信的鉴权缺陷
- Web 管理界面漏洞（弱口令、命令注入）
- 固件中的密钥/证书硬编码

## 七、ADB 与 Android 操作避坑（附录 A 要点）

```bash
# Git Bash 路径转换问题：禁用路径转换
MSYS_NO_PATHCONV=1 adb push file.txt /sdcard/

# adb shell 变量提前展开：转义$符号
adb shell "su -c 'cp \$CERT_DIR/* /tmp/'"
```

- Windows 打包 Magisk 模块用 7-Zip（避免 PowerShell `\` 路径分隔符）
- Android 10+ 系统证书注入用 bind mount + service.sh，不直接写 APEX
- 证书 hash：`openssl x509 -inform PEM -subject_hash_old -in cert.crt -noout`

## 八、验证要点

- 逆向产物优先提取：硬编码 API/密钥/加密算法/接口清单
- 抓包验证：加密参数是否可逆、token 是否可重放
- WebView：addJavascriptInterface 暴露面 → JS 调用原生方法
- 导出组件：无权限调用能否操作他人数据/敏感功能
- 固件：默认口令、调试接口、未签名升级链

## 九、修复建议

- 敏感数据用系统安全存储（Keychain/Keystore），禁止明文
- WebView 最小权限：关闭 file 访问、白名单 JS 接口、校验来源
- 导出组件声明权限，未导出组件禁止 exported
- 证书固定 + 主机名校验
- 固件：签名升级、去除调试接口、密钥安全存储

