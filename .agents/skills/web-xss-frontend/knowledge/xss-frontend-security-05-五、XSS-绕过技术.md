# 五、XSS 绕过技术

> 来源：CkSKILLS v1 `xss-frontend-security` §五、XSS 绕过技术（迁移至 v2 知识块）

```
HTML实体：&#60;script&#62;
事件：onerror/onload/onfocus/onmouseover
标签：<svg>、<img>、<iframe>、<math>
伪协议：javascript:、data:
```

进阶思路：
- 过滤绕过：大小写、双写、编码嵌套、空白符/换行注入
- 富文本过滤逃逸：事件属性、svg/math 命名空间、style 表达式
- 服务端 vs 客户端过滤差异
- 存储点污染 → 多个触发点（后台/导出/邮件）
- 伪协议过滤绕过：`javascript://` 注释形态、U+2028/U+2029 行分隔符、实体编码、Tab 干扰（详见 3.3 变种库）
