> 来源：实战知识库（真实 SRC 战法沉淀，已并入 CkSKILLS_v2）。
> 与 `rules/` 冲突时以 rules 为准；CORS 按 `../../../../rules/20-min-harm.md` 与团队取舍不主动挖。

# Groovy 公式沙箱打到命令执行

> 战法索引指针。认的是「数据模型/公式把用户脚本当 Groovy 跑，SM 只拦了 Runtime.exec」。  
> **不是** Jenkins `/script`，也不是对话口工具执行（见 `../../ai-agent/knowledge/agent-tool-exec-test.md`）。  
> 写不写只认 `../../../../rules/40-evidence-report.md`。命令只做 `id`。

## 认什么

像下面同时出现：

1. 数据模型 / 公式 / 响应转换脚本字段（`responseExtractScript` 一类，名字不封闭）
2. 跑的是 Groovy（`Eval.me` / `GroovyShell` 能算 `3*9`）
3. `'id'.execute()` / `Runtime.exec` / `ProcessBuilder` 回 `SecurityException` 或「Executing shell commands is not allowed」
4. 明文 `execute` / `File.write` / `file://` / `Class.forName` 被 WAF 拦（360xx），字符码拼回去又能跑

`File.write` 拦了别停：`FileOutputStream` / nio `Files.write` / `PrintWriter` 常常还在。

## 打哪（不登录）

免授权调用口打脚本（创建模型若要应用令牌，触发仍走免授权 GET）。

1. 脚本不要明文写 `execute`/`File`：`return Eval.me([字节码].collect{(char)it}.join())`
2. `sun.misc.Unsafe.theUnsafe` → `allocateInstance(UNIXProcess)`（没有就试 `ProcessImpl`）
3. 跳过构造，调 `toCString` + `forkAndExec(mode=1, helper='', prog=/bin/sh, argBlock=-c + 命令, argc=2, fds=[-1,-1,-1])`
4. 把 `id` 写到 `/tmp` 再 `File.getText` 读回（构造函数里的 checkExec 走不到）

`setSecurityManager(null)` 被拒不是假点。Nashorn/`'id'.execute()` 被 SM 拦也不是停。

## 出什么算成

回包是本机 `uid=`（真实系统用户），不是沙箱提示里的假 uid。

## 假点

- SM / 沙箱 hook 了 native `forkAndExec`
- 没有 `UNIXProcess` / `ProcessImpl`
- `Eval.me` 禁了，字符码解码后 WAF 仍拦
- 只算出 `3*9`、只读到文件、命令没跑起来

## 停

没 Groovy 公式口 → 本枪 N/A。  
SM 拦 exec 就停、不再打 Unsafe/forkAndExec = 漏测。  
认到只打**当前站**；禁止为此 FOFA 全网同皮。

