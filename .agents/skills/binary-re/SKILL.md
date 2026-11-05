---
name: binary-re
description: 二进制/固件/ELF/PE/内存破坏逆向专项。当目标是 PE/ELF/SO/固件可执行文件、Windows 服务、TCP 二进制服务、需要逆向协议或挖内存破坏漏洞时调用。
---

# binary-re — 二进制/固件/ELF/PE/内存破坏逆向专项

## 何时调用

- PE/.NET/ELF/SO/固件二进制
- TCP 行协议/自定义协议服务
- 内存破坏（溢出/UAF/格式化字符串/越界）
- 逆向算法/授权/加密/口令
- 驱动/内核组件

## 30 秒分诊

1. 先 `file`/`checksec`/`strings`/`readelf` 摸清形态
2. 服务型：nc 看 banner/HELP 摸命令集
3. 下载型：拿二进制本地静态逆向；再找隐藏路由/表单
4. 固件型：找口令常量/XOR 表/状态机/加密数据

## 首枪顺序

- 未初始化内存：BUILD/DUMP/EXPORT 直接 dump 结构体
- 越界读：声明长度 > 载荷（heartbeat）；固定偏移常见凭据/敏感数据
- LRU/历史：PUT 满容量触发淘汰，HIST 读被淘汰项
- 负偏移/超长写：覆写 guard/secret → REVEAL
- 栈溢出：无 canary/NX off → ret2shellcode/ROP
- 固件：rodata XOR 表、口令常量、状态转移表、TEA/RC4/PJW/FNV
- Go stripped：pclntab 恢复符号；VM/decoy 识别
- 真实环境：校验通过后读取本地授权文件/输出设备凭证；未公开表单/命令从二进制字符串抄

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/二进制与固件逆向实战.md` | v2 实战：服务型/泄露/破坏/固件 | 4.0KB |
| `knowledge/windows-reverse-engineering-05-五、缓冲区溢出专项挖掘.md` | 缓冲区溢出 | 1.3KB |
| `knowledge/windows-reverse-engineering-11-十一、漏洞利用构造.md` | 漏洞利用构造 | 0.9KB |
| `knowledge/windows-reverse-engineering-03-三、静态分析要点.md` | 静态分析要点 | 1.8KB |
| `knowledge/windows-reverse-engineering-04-四、动态分析要点.md` | 动态分析 | 1.1KB |
| `knowledge/windows-reverse-engineering-10-十、反调试-反虚拟机对抗.md` | 反调试对抗 | 1.0KB |

其余 8 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `source-audit` / `mobile-app`

