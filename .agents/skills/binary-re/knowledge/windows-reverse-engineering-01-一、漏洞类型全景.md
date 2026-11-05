# 一、漏洞类型全景

> 来源：CkSKILLS v1 `windows-reverse-engineering` §一、漏洞类型全景（迁移至 v2 知识块）

| 类型 | 危险函数/场景 | 挖掘要点 |
|---|---|---|
| 缓冲区溢出 | strcpy/strcat/sprintf/gets/memcpy/wcscpy | 栈溢出、堆溢出、off-by-one、整型溢出 |
| 远程命令执行 | system/CreateProcess/ShellExecute/WinExec | 命令拼接、UNC路径、COM接口滥用 |
| 权限提升 | 服务路径未引用/UAC绕过/令牌滥用/弱权限 | Unquoted Service Path、DLL劫持、令牌窃取 |
| 信息泄露 | 硬编码凭证/调试输出/内存残留/配置文件 | 字符串扫描、资源段、内存dump |
| 拒绝服务 | 未校验长度/空指针/除零/死循环/资源耗尽 | 输入长度异常、空对象解引用 |
