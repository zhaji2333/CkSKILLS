---
name: cloud-infra-supply-chain
description: 当目标涉及云资产（对象存储/云元数据/Serverless）、容器/K8s、运维面板（宝塔/Grafana/Zabbix/Jenkins/GitLab/Nacos等）、消息队列/缓存中间件、CI/CD流水线、第三方回调集成、依赖组件CVE、信息泄露配置时调用。负责未授权访问、弱口令、云配置错误、供应链漏洞与敏感信息挖掘。
---

# cloud-infra-supply-chain — 云/基础设施/供应链专项深度挖掘

## 何时调用（触发条件）

- 云资产：对象存储、云主机、Serverless、云元数据
- 容器/K8s：Docker API、K8s Dashboard、ServiceAccount
- 运维面板/中间件：宝塔、Grafana、Zabbix、ELK、Jenkins、GitLab、Nacos、Redis、Kafka
- CI/CD 流水线、依赖组件清单（SBOM）
- 第三方集成：支付回调、短信、邮件、CDN、地图 API
- 信息泄露：错误栈、调试接口、备份文件、.map、日志

## 一、运维/管理类场景表（全景）

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

## 二、第三方集成类场景表（全景）

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| 支付回调(支付宝/微信) | 签名绕过/参数篡改 | 签名校验缺失、notify_url可控 |
| 短信网关 | 短信轰炸/内容可控 | 无频率限制、短信模板可控 |
| 邮件服务 | 邮件头注入/钓鱼 | 收件人可控、内容可控 |
| CDN/OSS | 配置错误/越权访问 | Bucket公开、签名URL泄露 |
| 地图/定位API | 信息泄露/Key泄露 | 泄露内部地址、API密钥硬编码 |
| 消息队列(Kafka/RabbitMQ) | 未授权访问/消息伪造 | 管理接口暴露、消息可注入 |
| 缓存服务(Redis/Memcached) | 未授权访问/数据泄露 | 默认端口无密码 |
| 微服务网关 | 路由绕过/鉴权绕过 | 路径标准化差异、Header注入 |

## 三、云环境专项（14.4）

```
云元数据：
  - AWS: http://169.254.169.254/latest/meta-data/
  - 阿里云: http://100.100.100.200/latest/meta-data/
  - 腾讯云: http://metadata.tencentyun.com/latest/meta-data/

Kubernetes:
  - ServiceAccount Token泄露
  - etcd未授权访问
  - Dashboard弱口令

Serverless:
  - 函数环境变量泄露
  - 临时凭证获取
  - 事件注入

对象存储:
  - Bucket公开可读/写
  - 预签名URL泄露
  - ACL配置错误
```

> SSRF 打云元数据的完整手法见 `ssrf-internal-network` 技能。

## 四、信息泄露专项（K类）

- 错误栈、调试接口、版本信息
- 源码泄漏、`.map` 文件、配置文件
- 日志泄露、备份文件（.bak/.sql/.zip）
- 对象存储权限（公开桶、预签名 URL）
- Git 历史泄露（.git/目录、commit 中的密钥）

## 五、供应链安全（L类）

| 类型 | 场景 |
|---|---|
| L1. 组件CVE | SBOM/依赖清单、版本比对 |
| L2. 云/容器错误配置 | 公开存储桶、弱IAM、裸奔Dashboard |
| L3. CI/CD密钥泄露 | 流水线日志、环境变量、仓库历史 |

### 挖掘方法
- 指纹识别 → 版本比对 → 查 CVE（nuclei 模板、公开漏洞库）
- 组件清单：package.json、requirements.txt、pom.xml、composer.lock
- CI/CD：Jenkins 匿名构建、GitLab 公开仓库、流水线日志中的凭证

## 六、新兴技术类（延伸）

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| AI/大模型接口 | Prompt注入/敏感信息 | 提示词泄露、越权调用、输出敏感数据 |
| 区块链/Web3 | 智能合约漏洞/私钥泄露 | 重入攻击、权限控制、密钥硬编码 |
| Serverless函数 | 注入/环境变量泄露 | 事件注入、临时凭证获取 |
| 低代码平台 | 表达式注入/越权 | 公式执行、流程绕过 |

## 七、验证要点

- 未授权访问：默认路径/默认端口直接访问是否 200
- 弱口令：先试默认凭证（admin:admin、root:root）
- 云配置：公开桶可读/写、预签名 URL 可遍历
- 信息泄露：泄露的数据能否用于下一步（密码、AK/SK、内部域名）
- 供应链：版本 → CVE 匹配 → 可利用性验证

## 八、修复建议

- 管理面收敛：仅内网/白名单访问，禁用默认凭证
- 中间件：鉴权 + 最小暴露端口 + 定期更新
- 云：对象存储私有 + 最小 IAM 权限 + IMDSv2
- 日志/备份脱敏，禁止公网访问
- 依赖：SBOM 管理 + 漏洞扫描 + 升级策略

