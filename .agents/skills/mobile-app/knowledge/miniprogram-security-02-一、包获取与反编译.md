# 一、包获取与反编译

> 来源：CkSKILLS v1 `miniprogram-security` §一、包获取与反编译（迁移至 v2 知识块）

**获取途径**
- **PC 微信**：`WeChat Files/Applet/<appid>/` 下 `.wxapkg` 缓存（主包+分包），需先在小程序里打开过
- **微信开发者工具**：导入源码调试（拿到项目源码的场景）
- **手机抓包**：HTTP(S) 代理 + 小程序包下载接口（配合证书安装）
- **第三方平台**：小程序包下载站、GitHub 泄露、历史版本
- **其他平台**：支付宝（.axml）、抖音、百度（.swan）结构类似，解包工具对应适配

**反编译工具**
```
wxappUnpacker        # 经典解包，还原 app.js/pages 结构
unveilr              # 较新，支持分包/新版格式
CrackMinApp          # 微信小程序一键解包
```
- 解包产物结构：`app.js`（全局逻辑）、`app.json`（页面/权限配置）、`pages/*`（页面）、`utils/*`、`project.config.json`、`cloudfunctions/`（云函数目录）
- 新版分包需先解主包再按 `app.json` 的 `subpackages` 配置逐分包解
- 压缩混淆的 JS：先用 js-beautify/反混淆还原，再搜索关键字

**还原度确认**：解包后核对 `app.json` 页面数与线上功能是否对应，确认还原完整再开始审计。

---
