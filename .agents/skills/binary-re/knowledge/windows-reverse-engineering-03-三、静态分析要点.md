# 三、静态分析要点

> 来源：CkSKILLS v1 `windows-reverse-engineering` §三、静态分析要点（迁移至 v2 知识块）

### 1. 信息收集先行
```
文件类型：DIE / TrID 识别编译器/语言/壳
PE结构：  检查 ASLR/DEP/CFG/SafeSEH/SEHOP 保护标志
导入表：  关注危险 API（见下表）
字符串：  提取 URL/IP/路径/密钥/SQL/错误信息
资源段：  嵌入配置/证书/PE/脚本
```

### 2. 危险 API 速查表

| 类别 | 危险 API | 风险 |
|---|---|---|
| 字符串 | strcpy/strcat/sprintf/vsprintf/gets | 栈溢出 |
| 宽字符 | wcscpy/wcscat/swprintf | 栈溢出 |
| 内存 | memcpy/RtlCopyMemory/memmove | 长度可控溢出 |
| 格式化 | printf/sprintf/fprintf/wsprintf | 格式化字符串 |
| 命令 | system/CreateProcess/ShellExecute/WinExec | 命令注入 |
| 文件 | fopen/CreateFile/WriteFile | 路径穿越/任意写 |
| 网络 | recv/WSARecv/ReadFile(pipe) | 网络输入面 |
| 注册表 | RegSetValue/RegCreateKey | 持久化/配置篡改 |
| 加载 | LoadLibrary/GetProcAddress | DLL劫持/注入 |
| 内存 | VirtualAlloc/WriteProcessMemory | 注入面 |

### 3. 控制流与数据流追踪
```
入口点 → WinMain / DllMain / ServiceMain / HandlerRoutine
输入源：命令行 / 配置文件 / 网络 socket / 命名管道 / RPC / COM
关键路径：recv → memcpy / GetCommandLine → sprintf / ReadFile → strcpy
危险Sink：函数指针调用、虚表调用、jmp/call [reg]
```

### 4. .NET 程序专项
```
dnSpy 反编译 → 搜索 Process.Start/SecurityElement/XmlDocument
关注：XmlDocument.Load（XXE）、Process.Start（命令注入）、
     BinaryFormatter/XmlSerializer（反序列化）、
     RegEx（ReDoS）、路径拼接（穿越）
混淆：de4dot 去混淆 → 重新反编译
强命名：检查强名称，评估重打包/篡改可行性
```
