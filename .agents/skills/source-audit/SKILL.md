---
name: source-audit
description: 白盒代码审计与反编译产物审计专项。当拿到源码/反编译产物/代码片段，需要从输入点追到危险函数、或做鉴权/逻辑审计时调用。
---

# source-audit — 白盒代码审计与反编译产物审计专项

## 何时调用

- 有源码/反编译产物/代码片段
- 代码审计/0day 白盒
- 危险函数排查
- 鉴权/授权设计审计

## 30 秒分诊

1. 先定输入点（HTTP 参数/文件/消息/环境）
2. 追传播链到 sink（SQL/命令/文件/反序列化/模板）
3. 查鉴权：每个敏感操作是否校验身份/权限/租户
4. 输出：可疑调用链 + 触发条件 + 验证请求

## 首枪顺序

- SAST：source → propagation → sink 三列清单
- 危险函数速查：PHP/Java/Python/Node/Go
- 鉴权审计：越权/未授权/租户隔离
- 反序列化/模板/命令/文件操作的 sink 定位
- 结合黑盒：用 SAST 线索定向验证

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/source-code-audit-01-一、静态审计方法-SAST.md` | SAST 方法 | 0.6KB |
| `knowledge/source-code-audit-02-二、危险函数速查-按语言.md` | 危险函数速查 | 0.8KB |
| `knowledge/source-code-audit-03-三、鉴权审计要点.md` | 鉴权审计 | 0.4KB |
| `knowledge/source-code-audit-04-四、结合其他技能.md` | 与其他技能联动 | 0.4KB |

## 相关

- `web-injection` / `web-deser-xxe` / `binary-re`

