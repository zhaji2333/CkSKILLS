# 十二、模糊测试

> 来源：CkSKILLS v1 `windows-reverse-engineering` §十二、模糊测试（迁移至 v2 知识块）

```
选择：
  文件型：AFL++ + WinAFL（持久化模式）
  协议型：boofuzz（结构化）/ 自定义变异
  内核型：kAFL / IOCTL fuzzer
目标函数：解析复杂结构、处理外部输入的函数
种子：合法样本库（覆盖各分支）
监控：崩溃捕获（WinDbg/gflags）+ 崩溃分类
去重：栈哈希 → 同类合并
```
