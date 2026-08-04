---
name: file-handling
description: 当目标存在文件上传（头像/附件/证件）、下载/导出、导入（Excel/CSV/XML）、预览（PDF/Office）、图片/音视频处理、压缩包解压打包、在线编辑器/终端等功能时调用。负责任意文件上传getshell、路径穿越、任意文件读取/删除、LFI/RFI、Zip Slip、CSV注入/公式注入、ImageMagick/FFmpeg攻击深度挖掘。
---

# file-handling — 文件与路径安全专项深度挖掘

## 何时调用（触发条件）

- 文件上传：头像/附件/证件/导入文件
- 文件下载/导出：报表、日志、备份
- 文件预览/处理：PDF/Office、图片裁剪缩放、音视频处理
- 压缩包处理：在线解压/打包
- 文件路径参数可控：filename、path、file、template
- 在线编辑器/IDE、终端/Shell 模拟、数据库查询工具

## 一、文件操作类场景表（全景）

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

## 二、漏洞类型全景

| 类型 | 场景 | 挖掘要点 |
|---|---|---|
| F1. 任意文件上传 | 头像、附件、导入 | 类型/扩展名/内容校验 |
| F2. 路径穿越 | 下载接口、模板加载 | `../`规范化检查 |
| F3. 任意文件读取/删除 | 导出报表、缓存处理 | 路径白名单 |
| F4. 文件包含（LFI/RFI） | 动态include | php://filter等协议 |

## 三、文件上传绕过技术

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

## 四、路径穿越与任意文件读写

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

## 五、文件处理引擎攻击

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

## 六、特殊功能类扩展

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| 在线解压/打包 | 路径穿越/DoS | Zip炸弹、符号链接攻击 |
| 在线编辑器/IDE | 任意文件读写/RCE | 文件路径可控、代码执行 |
| 终端/Shell模拟 | 命令注入/逃逸 | 命令过滤绕过、沙箱逃逸 |
| 数据库查询工具 | SQL注入/越权 | 查询语句可控、连接信息泄露 |

## 七、验证要点

- 上传：先验证文件落盘与访问路径，再测执行（解析到 Web 目录才可 getshell）
- 下载/导出：filename 参数可控性 → 穿越读取 → 影响面（配置文件/源码）
- 预览/处理：远程 URL 加载 → SSRF/XXE 链
- 解压：Zip Slip 覆盖文件（.htaccess/.user.ini/配置）
- 修复优先级：上传 getshell / 任意文件读取为 P0-P1

## 八、修复建议

- 上传：扩展名+内容白名单、存储与执行目录隔离、随机文件名
- 下载/读取：路径白名单+规范化校验（realpath 比对）
- 解压：拒绝 ../ 与符号链接、限制解压大小与文件数
- 处理引擎：升级补丁、禁用危险协议（url:/concat）
- 导入：禁止公式执行、禁用外部实体

