---
name: web-file-path
description: 文件上传/下载/导入导出/预览/路径穿越/任意读写/处理引擎专项。当出现头像附件上传、报表导出、文档导入、PDF/Office/图片预览、压缩包、在线解压时调用。
---

# web-file-path — 文件上传/下载/导入导出/预览/路径穿越/任意读写/处理引擎专项

## 何时调用

- 上传（头像/附件/证件）
- 下载/导出/预览
- 导入（Excel/CSV/XML）
- 压缩包/在线解压
- 图片/音视频处理

## 30 秒分诊

1. 先试无鉴权上传/下载：能不能传、传到哪、文件名是否可控
2. 上传：看扩展名/内容/MIME 校验层，先绕扩展名再绕内容
3. 下载/预览：`file=`/`path=` 直拼则打绝对路径与编码穿越
4. 解析类（Office/图片/压缩包）→ 处理引擎攻击

## 首枪顺序

- 只拦 .php → 传 `.htaccess` AddType + `.jpg` 马；或 `<?` 短标签+动态函数
- 上传目录可执行 + 二次渲染 → 图片马/PDF+PHP polyglot
- 预览/下载接口吃 file=/path= → `/etc/passwd`、配置/密钥文件绝对路径
- 路径穿越被拦 → URL 编码/双写/绝对路径/二次解码
- XML 导入 → XXE（UTF-16/BOM 绕 WAF）
- CSV 导出 → 公式注入（如平台收录）
- 压缩包 → Zip Slip 写 web 目录
- 备份/日志/SQLite 在 web 目录 → /backup/、/db/*.db、*.bak
- LFI + 日志包含（UA 投毒）→ RCE

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/file-handling-03-三、文件上传绕过技术.md` | 上传绕过技术 | 0.6KB |
| `knowledge/file-handling-04-四、路径穿越与任意文件读写.md` | 穿越与任意读写 | 0.6KB |
| `knowledge/file-handling-05-五、文件处理引擎攻击.md` | ImageMagick/FFmpeg/Office/压缩包 | 0.6KB |
| `knowledge/path-traversal-lfi-test.md` | LFI/穿越实战大全 | 0.5KB |
| `knowledge/file-upload-test.md` | 真实 SRC 上传/分享/下载战术 | 13.3KB |

其余 8 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-injection` / `web-ssrf-render` / `cloud-infra`

