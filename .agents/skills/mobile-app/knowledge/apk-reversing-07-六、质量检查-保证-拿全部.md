# 六、质量检查（保证"拿全部"）

> 来源：CkSKILLS v1 `apk-reversing` §六、质量检查（保证"拿全部"）（迁移至 v2 知识块）

- [ ] **入口类真实**：JADX 打开 Application/入口 Activity 是业务代码，非 stub
- [ ] **特征串可命中**：`grep -rniE "appKey|secret|sign|接口域名" jadx_out/sources/` 有结果
- [ ] **so 完整**：`lib/arm64-v8a/` 下 so 齐全，IDA 9.5 无头模式可打开、JNI 导出表可枚举
- [ ] **H5 完整**：assets/www 或远程加载地址已记录
- [ ] **dex 合并**：多分片 dex 已合并，无遗漏
- [ ] **report.md 已写**：壳类型、脱壳方式、产物清单、未还原项（如实记录，不编造）
