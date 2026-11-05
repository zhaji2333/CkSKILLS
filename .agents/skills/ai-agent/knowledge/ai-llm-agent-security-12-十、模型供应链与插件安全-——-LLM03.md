# 十、模型供应链与插件安全 —— LLM03

> 来源：CkSKILLS v1 `ai-llm-agent-security` §十、模型供应链与插件安全 —— LLM03（迁移至 v2 知识块）

| 攻击面 | 风险 | 测试要点 |
|---|---|---|
| 模型权重 | 后门/触发器 | 特定触发词产出异常输出 |
| HuggingFace 模型 | pickle 反序列化 RCE | `torch.load` 加载恶意权重 |
| 插件/扩展 | 工具描述注入、越权 | description 藏指令、插件权限过大 |
| 第三方模型 API | 中间人篡改响应 | 替换响应注入指令 |
| 依赖库 | 供应链 CVE | langchain/llama-index 已知漏洞 |
| Embedding 模型 | 投毒嵌入空间 | 操纵检索结果 |

```bash
python -c "import pickletools; pickletools.dis(open('model.pkl','rb'))"
```
