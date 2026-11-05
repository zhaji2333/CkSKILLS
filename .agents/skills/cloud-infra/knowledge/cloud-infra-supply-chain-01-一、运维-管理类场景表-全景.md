# 一、运维/管理类场景表（全景）

> 来源：CkSKILLS v1 `cloud-infra-supply-chain` §一、运维/管理类场景表（全景）（迁移至 v2 知识块）

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| 后台登录 | 弱口令/默认口令/爆破 | admin:admin、无验证码、无锁定 |
| 数据库管理(phpMyAdmin等) | 未授权/弱口令/SQL执行 | 默认路径、弱密码 |
| 服务器面板(宝塔/cPanel) | 未授权/RCE | 默认端口、已知CVE |
| 监控系统(Zabbix/Grafana) | 未授权/SSRF/SQL注入 | 默认凭证、API未鉴权 |
| 日志系统(ELK/Splunk) | 未授权/敏感信息 | Kibana未鉴权、日志含密码 |
| CI/CD(Jenkins/GitLab) | 未授权/RCE/凭证泄露 | 匿名构建、密钥泄露、命令执行 |
| 容器管理(Docker/K8s) | 未授权/逃逸/提权 | Docker API暴露、Dashboard弱口令 |
| 配置中心(Nacos/Apollo) | 未授权/配置泄露 | 默认账号、API未鉴权 |
