# 五、文件处理引擎攻击

> 来源：CkSKILLS v1 `file-handling` §五、文件处理引擎攻击（迁移至 v2 知识块）

### ImageMagick
- MVG/SVG payload、`url:` 协议（SSRF）
- 已知 CVE：ImageTragick 系列

### FFmpeg
- `concat` 协议、`file://` 读取
- HLS playlist 注入

### Office/PDF 预览
- 宏执行、OLE 对象（RCE）
- 外部实体（XXE）

### 压缩包
- Zip Slip：解压路径穿越覆盖关键文件
- 符号链接：解压软链接读取任意文件
- Zip 炸弹：DoS

### 导入文件
- CSV 公式注入：`=cmd`、`+HYPERLINK`
- XML/Office：XXE
- 反序列化对象（.ser/.bin）
