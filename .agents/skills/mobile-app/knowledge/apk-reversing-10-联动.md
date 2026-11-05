# 联动

> 来源：CkSKILLS v1 `apk-reversing` §联动（迁移至 v2 知识块）

- 下游挖洞：产物直接交给 `android-security-audit`（密钥追踪→未授权接口 / 组件安全）
- 快筛前置：`asc-fast-hunt`（大包秒级定位密钥/签名/接口，决定是否值得全量还原；脱壳后的 dex 打包成 zip 也能回它检索：`cd <dex目录> && zip -q dumped.zip classes*.dex && $ASC/asc findrefs dumped.zip.apk string appkey`；`$ASC` 见该技能环境安装）
- H5 内嵌小程序：`miniprogram-security`
- 提取的密钥/域名上报深挖：`recon-js-analysis`
- 正式报告：按 `../../../../rules/40-evidence-report.md`输出
