# 三、文件上传绕过技术

> 来源：CkSKILLS v1 `file-handling` §三、文件上传绕过技术（迁移至 v2 知识块）

```
扩展名：.php5/.phtml/.phar/.htaccess/.user.ini
双扩展：shell.php.jpg / shell.jpg.php
%00截断：shell.php%00.jpg
内容：GIF89a头、图片马
```

进阶绕过思路：
- MIME 类型伪造（Content-Type 改为 image/png）
- 内容检测绕过：图片马 + 二次渲染差异注入
- 解析差异：nginx 解析漏洞、Apache 多后缀、IIS 分号截断
- 上传点复用：头像路径 → 包含执行 / 路径可控覆盖
- .user.ini / .htaccess 覆盖
