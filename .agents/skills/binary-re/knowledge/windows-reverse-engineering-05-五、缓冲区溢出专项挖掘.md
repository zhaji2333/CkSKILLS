# 五、缓冲区溢出专项挖掘

> 来源：CkSKILLS v1 `windows-reverse-engineering` §五、缓冲区溢出专项挖掘（迁移至 v2 知识块）

### 1. 栈溢出
```
特征：strcpy/gets/sprintf 无边界检查
验证：
  1. 定位输入到栈缓冲区的拷贝
  2. pattern_create 创建唯一模式
  3. 覆盖 EBP/RET，pattern_offset 计算偏移
  4. 检查可跳转模块（jmp esp / pop reg; ret）
  5. 构造 ROP 绕 DEP（mona rop / ROPgadget）
保护：检查 /GS（cookie）、SafeSEH、CFG
```

### 2. 堆溢出
```
特征：memcpy/HeapAlloc 后越界写
利用：
  Windows XP/2003：UFH/Block List 腐蚀
  Win7+：堆块元数据（_HEAP_ENTRY）腐蚀
  Win10+：Segment Heap，关注 _HEAP_ENTRY_CONTEXT
UAF：释放后引用 → 占位控制 → 虚表劫持
  1. 定位 free → use 的间隔
  2. 在间隔内分配等大内存占位
  3. 覆盖虚表指针 → 跳转可控地址
```

### 3. 整型溢出
```
符号扩展：int → size_t 转换
算术溢出：(a+b) < len 时 a+b 回绕
乘法溢出：a*b 截断
验证：在 memcpy 前断点，观察长度参数
```

### 4. off-by-one
```
循环条件：<= 误写为 < / 循环变量多增 1
wcsncpy 末尾不补 \0 → 后续 strcpy 越界
验证：精确控制输入长度，对比堆栈/堆布局差异
```
