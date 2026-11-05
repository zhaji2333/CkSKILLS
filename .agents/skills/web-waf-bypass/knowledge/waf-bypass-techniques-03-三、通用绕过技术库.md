# 三、通用绕过技术库

> 来源：CkSKILLS v1 `waf-bypass-techniques` §三、通用绕过技术库（迁移至 v2 知识块）

### 编码类
- URL 编码 / 双重编码（%252e）
- Unicode（\u002e、全角字符）
- 十六进制 / 八进制 / 十进制 IP
- HTML 实体 / Base64 / 分块编码

### 变形类
- 大小写混合（SeLeCt）
- 双写（selselectect）
- 注释插入（/**/、/*!*/）
- 空白符替换（%09、%0a、${IFS}）
- 等价函数/等价标签

### 逻辑类
- 换 HTTP 方法（POST↔GET、PUT、PATCH）
- 换 Content-Type（JSON↔form↔multipart）
- 参数位置迁移（参数名→参数值→Header→Cookie→Path）
- 参数污染（重复参数、数组化）

### 协议类
- HTTP 走私（CL/TE 差异）
- 分块传输（Transfer-Encoding: chunked）
- 管道化、WebSocket 升级
- 路径标准化差异（//、/./、/../、%2e）
