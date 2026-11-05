# 七、验证要点

> 来源：CkSKILLS v1 `file-handling` §七、验证要点（迁移至 v2 知识块）

- 上传：先验证文件落盘与访问路径，再测执行（解析到 Web 目录才可 getshell）
- 下载/导出：filename 参数可控性 → 穿越读取 → 影响面（配置文件/源码）
- 预览/处理：远程 URL 加载 → SSRF/XXE 链
- 解压：Zip Slip 覆盖文件（.htaccess/.user.ini/配置）
- 修复优先级：上传 getshell / 任意文件读取为 P0-P1
