---
name: mobile-app
description: Android/APK/小程序/移动端逆向与组件安全专项。当目标是 APK/预装应用/厂商应用/小程序，需要脱壳、逆向、组件漏洞、密钥追踪或未授权接口时调用。
---

# mobile-app — Android/APK/小程序/移动端逆向与组件安全专项

## 何时调用

- APK/Android/预装应用/系统应用
- 小程序/云开发/微信生态
- 脱壳/JADX/IDA/ASC
- 导出组件/Intent/WebView/Provider/Deep Link
- 硬编码密钥→未授权接口

## 30 秒分诊

1. 先判壳（unzip 看 so/manifest 入口类）；有壳转脱壳
2. 无壳：ASC 快筛（manifest/findrefs）→ JADX 精读
3. 优先找硬编码密钥/签名算法 → 打未授权接口
4. 组件面：导出组件/Intent/WebView 桥/Deep Link

## 首枪顺序

- ASC `getmanifest`/`findrefs`/`getclass` 快筛，再 JADX 全量
- 硬编码 appKey/appSecret/sign → 重算签名调接口
- 导出组件：adb 显式 Intent 拉起/传参
- WebView：JS 桥/addJavascriptInterface 注入
- Provider 未授权读写；PendingIntent 劫持
- 脱壳：Frida dump/apktool → 重新审计
- 小程序：反编译 wxapkg → 提 appid/secret → 云函数未授权
- so 层：JNI 攻击面/IDA 无头分析

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/android-security-audit-05-🔴-一、密钥追踪-→-未授权接口专项-最高优先级.md` | 密钥追踪→未授权接口 | 7.9KB |
| `knowledge/android-security-audit-06-二、静态分析.md` | 静态分析/组件面 | 0.3KB |
| `knowledge/android-security-audit-07-三、Native-内存安全深挖-IDA-9-5-无头-+-MCP.md` | Native 深挖 | 8.0KB |
| `knowledge/apk-reversing-01-标准产物-交付标准.md` | 脱壳与产物 | 0.9KB |
| `knowledge/miniprogram-security-01-快速开始-5-分钟出第一个接口-凭证.md` | 小程序快筛 | 0.5KB |

其余 40 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `binary-re` / `source-audit` / `web-auth-access`

