# 一、文件操作类场景表（全景）

> 来源：CkSKILLS v1 `file-handling` §一、文件操作类场景表（全景）（迁移至 v2 知识块）

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| 文件上传（头像/附件/证件） | 任意文件上传→getshell | 后缀绕过、MIME绕过、内容检测绕过、二次渲染绕过 |
| 文件下载/导出 | 任意文件读取/路径穿越 | ../遍历、绝对路径、编码绕过、符号链接 |
| 文件预览（PDF/Office） | SSRF/XXE/RCE | 远程URL加载、OLE对象、宏执行 |
| 文件导入（Excel/CSV/XML） | XXE/CSV注入/公式注入/反序列化 | =cmd、外部实体、恶意序列化数据 |
| 图片处理（裁剪/缩放/水印） | ImageMagick RCE/SSRF | MVG/SVG payload、url:协议 |
| 视频/音频处理 | FFmpeg SSRF/文件读取 | concat协议、file://、HLS playlist |
| 压缩包处理（解压/打包） | 路径穿越/Zip Slip/符号链接 | ../覆盖关键文件、软链接读取 |
| 日志下载/审计导出 | 敏感信息泄露/路径穿越 | 日志中含token/密码、文件名可控 |
