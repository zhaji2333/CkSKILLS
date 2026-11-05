# 七、权限提升专项

> 来源：CkSKILLS v1 `windows-reverse-engineering` §七、权限提升专项（迁移至 v2 知识块）

### 1. 服务类
```
Unquoted Service Path：
  路径含空格未加引号 → C:\Program Files\My Service\svc.exe
  放置 C:\Program.exe / C:\Program Files\My.exe 劫持
  前提：服务以 SYSTEM 启动，普通用户可写父目录
Weak Service Permissions：
  sc sdshow <svc> → 解析 ACL
  普通用户可修改 binPath → 替换为 payload
  AccessChk: accesschk.exe -uwcqv "Users" *
```

### 2. DLL 劫持
```
查找：Procmon 监控 Name not found 的 DLL 加载
可写目录：PATH 中的用户目录、应用目录
签名绕过：Side-Loading（代理 DLL 转发原函数）
工具：DLL Hijacking Auditor / SharpDLLHijack
```

### 3. UAC 绕过
```
自动提升的 COM 对象（ICMLuaUtil / IColorDataProxy）
 fodhelper.exe / computerdefaults.exe 注册表劫持
环境变量注入：windir / SystemRoot 劫持
Token Manipulation：
  impersonation token窃取（SeImpersonate）
  Potato 家族：RoguePotato / JuicyPotato / PrintSpicePotato
  SeImpersonate → SYSTEM（IIS/SQL Server 服务）
```

### 4. 内核提权
```
驱动 IOCTL：DeviceIoControl → 缓冲区解析漏洞
  IOCTL Heap Overflow / Arbitrary Write
Pool Overflow：非分页池溢出 → 占位token → SYSTEM
任意写：覆盖 HalDispatchTable / token 权限位
工具：HEVD（学习）、IOCTL Picker
```
