# 六、远程命令执行专项

> 来源：CkSKILLS v1 `windows-reverse-engineering` §六、远程命令执行专项（迁移至 v2 知识块）

### 1. 命令注入
```
拼接点：system(cmd.c_str()) / CreateProcess(NULL, cmd, ...)
特殊字符：& | ; %PATH% $(cmd) `cmd`
UNC 路径：\\attacker\share 触发 NTLM / SMB
案例：PrintSpooler、后台脚本调用、备份工具
验证：构造命令分隔符 payload → 回连 DNSLog/nc
```

### 2. 反序列化漏洞
```
.NET：
  BinaryFormatter / LosFormatter / ObjectStateFormatter
  JavaScriptSerializer / XmlSerializer（gadget 链）
  工具：ysoserial.net
Java（JVM on Windows）：
  ObjectInputStream + CC链 / JDK7u21
工具：ysoserial
验证：弹 calc.exe / 写文件 / 回连
```

### 3. COM 接口滥用
```
查找：OleView / 注册表 InprocServer32
关注：暴露 IShellDispatch / IWshShell 的对象
  Shell.Application → ShellExecute
验证：脚本调用 ShellExecute 执行任意命令
```
