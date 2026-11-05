# 五、供应链安全（L类）

> 来源：CkSKILLS v1 `cloud-infra-supply-chain` §五、供应链安全（L类）（迁移至 v2 知识块）

| 类型 | 场景 |
|---|---|
| L1. 组件CVE | SBOM/依赖清单、版本比对 |
| L2. 云/容器错误配置 | 公开存储桶、弱IAM、裸奔Dashboard |
| L3. CI/CD密钥泄露 | 流水线日志、环境变量、仓库历史 |

### 挖掘方法
- 指纹识别 → 版本比对 → 查 CVE（nuclei 模板、公开漏洞库）
- 无头浏览器内核同样算组件：Chromium/WebKit/Playwright/Puppeteer/wkhtmltopdf 版本 → CVE 匹配（入口发现与指纹见 `ssrf-internal-network` 三）
- 组件清单：package.json、requirements.txt、pom.xml、composer.lock
- CI/CD：Jenkins 匿名构建、GitLab 公开仓库、流水线日志中的凭证
