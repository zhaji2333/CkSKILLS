# 四、路径穿越与任意文件读写

> 来源：CkSKILLS v1 `file-handling` §四、路径穿越与任意文件读写（迁移至 v2 知识块）

测试向量：
```
../ 、 ..%2f 、 %252e%252e%252f 、 ..%c0%af
绝对路径：/etc/passwd、C:\Windows\win.ini
编码：Unicode（\u002e\u002e/）、十六进制、双重编码
符号链接：上传软链接指向敏感文件
```

验证目标：
- /etc/passwd、/etc/shadow（读权限）
- 应用配置文件（数据库密码、AK/SK）
- 源码文件（.py/.java/.php/.jar）
- 删除接口：任意文件删除 → 配合 getshell/持久化
