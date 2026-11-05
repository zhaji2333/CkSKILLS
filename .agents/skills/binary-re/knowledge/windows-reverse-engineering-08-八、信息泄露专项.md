# 八、信息泄露专项

> 来源：CkSKILLS v1 `windows-reverse-engineering` §八、信息泄露专项（迁移至 v2 知识块）

### 1. 静态泄露
```
硬编码：字符串扫描 Password=/key=/AKID/secret
PDB 路径：泄露开发目录结构/用户名
资源段：嵌入证书/配置/SQL/接口
版本信息：Company/InternalName 暴露厂商
```

### 2. 动态泄露
```
内存残留：进程内存 dump → 搜索 token/密码
调试输出：OutputDebugString / 日志文件
注册表：HKLM\Software\<App> 明文配置
错误信息：崩溃 dump / 异常栈
```

### 3. 协议泄露
```
明文传输：未加密 socket / Telnet / HTTP
调试接口：留有调试命令/隐藏命令字
越权读取：协议字段未校验 → 读取他人数据
```
