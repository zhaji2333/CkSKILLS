# 二、信息收集要"脏"（历史与周边）

> 来源：CkSKILLS v1 `recon-js-analysis` §二、信息收集要"脏"（历史与周边）（迁移至 v2 知识块）

必须尝试的信息源：
- **Wayback Machine**：翻旧版本页面/JS（可能有已删除的接口和功能）
- **GitHub/GitLab搜索**：目标域名、内部接口、泄露的密钥/配置
- **Google Dork**：site:target.com filetype:pdf/xls/doc/sql/log/bak
- **证书透明度日志**：发现隐藏的子域名
- **招聘JD**：推断技术栈（用了什么框架→对应什么已知漏洞）
- **JS中的注释/TODO**：开发者留下的线索
- **robots.txt / sitemap.xml**：暴露的隐藏路径
- **前端source map**：还原完整前端源码
- **APK/IPA反编译**：提取硬编码的接口和密钥
- **更新日志/Changelog**：新功能=新攻击面
