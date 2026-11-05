# 五、验证要点

> 来源：CkSKILLS v1 `deserialization-xxe` §五、验证要点（迁移至 v2 知识块）

- 反序列化：先确认可控输入点与编码方式，再选 gadget 链验证 RCE
- XXE：先测回显（文件读取），无回显用 OOB DNSLog 验证
- 原型污染：控制台/接口验证 `Object.prototype` 被污染
- 每个 payload 按适用维度过一遍（编码/变形/协议…）；下"无漏洞"结论前写明否定证据，不凑层数
