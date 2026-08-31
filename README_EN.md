# CK-Skills

> An SRC-oriented vulnerability-hunting skill pack for Claude Code / Codex — researcher methodology turned into dispatchable, reusable Agent skills.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-20-green.svg)](.agents/skills)

**Languages:** [中文](README.md) · **English**

## Overview

CK-Skills is an **Agent prompt-engineering and skill knowledge system** for SRC (bug bounty / vulnerability reward) hunting. It runs on general Agent frameworks such as Claude Code and Codex. Together, the system prompt (`AGENTS.md`) and **20 specialist skills** raise a general-purpose Agent to expert-level performance in offensive security.

It targets three failure modes of generic Agents in this domain:

- Methodology is scattered and coverage is incomplete
- Work stops at a shallow pass instead of following an expert workflow
- Experience-heavy bugs (business logic, access control, WAF bypass) are hard to automate

## Architecture

Five layers, each with a single job:

```
┌──────────────────────────────────────────────┐
│  Agent runtime (Claude Code / Codex)         │  Reasoning and tool use
├──────────────────────────────────────────────┤
│  System prompt AGENTS.md                     │  Identity / constraints / discipline / routing
├──────────────────────────────────────────────┤
│  20 specialist Skills (knowledge layer)      │  Methodology / scenario tables / steps
├──────────────────────────────────────────────┤
│  Trigger routing (scene → skill / vuln type) │  Expert knowledge loaded on demand
├──────────────────────────────────────────────┤
│  hunts/<target>/CLUEBOARD.md                 │  Shared blackboard (cross-session memory)
└──────────────────────────────────────────────┘
```

- **AGENTS.md**: six-part charter (identity, constraints, discipline, routing, assessment, output). Defines Agent persona, extended reasoning, ten testing rules, and structured output.
- **Skill**: Markdown DSL with frontmatter (trigger semantics) plus six elements (when to call, methodology, scenario tables, hunt steps, verification, remediation).
- **Routing tables**: scene → skill, vulnerability type → skill, priority, and combo scenarios. Mixture-of-experts style: load only the specialist you need.
- **Clue board**: one Markdown ledger per target. Specialist skills read and write the same file. A lightweight blackboard: skills are knowledge sources, the board is the blackboard, `AGENTS.md` routing is control — not a multi-agent scramble.

> Note: skill bodies and `AGENTS.md` are written in Chinese because the primary report targets (Chinese SRCs, CNVD/CNNVD, EDUSRC) require Chinese deliverables. The methodology itself is language-agnostic. Use this README and the skill `description` frontmatter to know **when** to load each skill; the Agent still follows the Chinese playbooks for execution and report wording.

## Skills

| Skill | Scope |
|---|---|
| `recon-js-analysis` | Asset mapping, webpack / source-map recovery, API and secret extraction, URL/IP/domain expansion, appid/appkey follow-up |
| `unauth-path-key-hunt` | Zero-identity public-surface recovery of paths and keys: response fingerprinting, crypto-is-not-auth (RSA/JSEncrypt), domain-migration / sibling-host retest |
| `hunt-clueboard` | Per-target Markdown clue board (cross-session working memory: read → hunt → write back). Does not replace hunting skills |
| `auth-access-control` | Auth bypass, frontend route-guard bypass, captcha, IDOR, multi-tenant isolation, password reset, JWT |
| `injection-vulns` | SQL / NoSQL / command / SSTI / expression injection |
| `business-logic-race` | Payment logic, state-machine modeling, amount tampering, race conditions |
| `file-handling` | Upload getshell, path traversal, Zip Slip, CSV injection |
| `ssrf-internal-network` | SSRF, cloud metadata, internal recon, DNS rebinding |
| `deserialization-xxe` | Deserialization RCE, XXE, prototype pollution, gadget chains |
| `xss-frontend-security` | XSS (including redirect / open-redirect variants), CSRF, CORS, clickjacking |
| `api-protocol-security` | BOLA, GraphQL, WebSocket, HTTP request smuggling |
| `miniprogram-security` | WeChat / Alipay / Douyin mini programs, package decompile, API and secret extraction, login / payment / IDOR / rendering / cloud functions |
| `cloud-infra-supply-chain` | Cloud misconfig, K8s, CI/CD, SBOM, supply chain |
| `source-code-audit` | Source → propagation → sink static audit |
| `waf-bypass-techniques` | Level 1–7 escalation framework |
| `ai-llm-agent-security` | Prompt injection, jailbreaks, system-prompt leak, RAG/memory poisoning, agent-tool RCE/SSRF, sandbox escape, model supply chain |
| `windows-reverse-engineering` | Windows PE reversing, .NET/kernel, memory corruption, protocol reversing, anti-debug, exploit-chain and PoC work |
| `android-security-audit` | Android APK component audit, Intent / WebView / Provider / Binder / Deep Link, no-Frida / no-Root verification, HyperOS-style intake reports |
| `apk-reversing` | Packer ID, unpacking, JADX/apktool full decompile, so/H5/assets extract — input for `android-security-audit` |
| `report` | Submission close-out: verification gates, DOCX report (template + step-style PoC + real screenshots), semantic filenames |

## Quick start (30 seconds)

### Option 1: one-shot install (recommended)

Paste the block below into your Agent (Claude Code, Codex, and similar). The Agent should **download → install → load → self-check**:

```
I will use you for authorized SRC / bug-bounty vulnerability hunting. Do the following now:

1. Download and install this skill pack: https://github.com/zhaji2333/CkSKILLS.git
2. Load: confirm AGENTS.md is active as the system prompt and the skill routing table is available
3. Self-check: list every installed specialist skill and confirm each trigger description is recognized
4. Report: output "skill pack installed and loaded" plus the skill list, then wait for my target

After that I will give a domain / APK / source tree. Follow the AGENTS.md routing table and invoke the matching skills for a deep hunt.
```

### Option 2: manual install

```bash
git clone https://github.com/zhaji2333/CkSKILLS.git
# Copy AGENTS.md and the .agents/ directory into your working tree, then restart the Agent
```

### After install

```
Target: https://example.com, logged in as a normal user, test access control
→ loads auth-access-control and runs the three authorization questions
```

### Uninstall

Delete `AGENTS.md` and `.agents/` from the working tree (or follow your Agent framework’s removal rules).

> Use only on systems you are authorized to test. Read the disclaimer at the end of this file.

## Recent updates

- **Added `unauth-path-key-hunt`**: zero-identity recovery of hidden API paths and keys (fingerprints, crypto-as-transport, migration retest)
- **Added `hunt-clueboard`**: per-target Markdown clue board so recon survives session compaction
- **Added `windows-reverse-engineering`**: Windows PE reversing and binary vulnerability hunting
- **Added `android-security-audit`**: APK component audit with JADX + ADB, no Frida / no Root, HyperOS-style intake
- **Added `report`**: report close-out skill — gates, DOCX for SRC/0day platforms (step-style PoC + real screenshots)
- **Refactored `miniprogram-security`**: split from the old mobile/IoT skill so Android content is not duplicated with `android-security-audit`
- **Added `apk-reversing`**: unpack and full decompile pipeline as input to `android-security-audit`
- **Expanded recon skills**:
  - `recon-js-analysis` now treats every URL/IP/domain from webpack/app.js/traffic as an expandable asset, and requires appid/appkey follow-up
  - `android-security-audit` extracts backend hosts and app credentials from decompiled APKs

## Design principles

- **Do not send packets until the JS is understood**: recon first, then requests
- **Clue board as blackboard**: persist hypotheses, hosts, paths, keys, and negative evidence. Read first, write back in the same turn. After compaction or a new session, trust the board — do not restart from the homepage JS (`hunt-clueboard`)
- **Coverage self-check**: done / not done / variants / related surfaces
- **Failure escalation**: levels 1–7; do not conclude “no bug” before level 4
- **Business modeling**: state machine + role matrix + illegal paths + consistency checks + concurrency
- **Cross-API questions**: data flow / credentials / state / permission / timing

## Contributing

Issues and PRs that add skills or tighten methodology are welcome. A new skill is a `SKILL.md` in the existing DSL, registered in the `AGENTS.md` routing tables.

## Disclaimer

This project is for **authorized security testing, research, and teaching only**. You must follow the laws of your jurisdiction and have **explicit written authorization** from the asset owner. Unlawful use is prohibited. You are solely responsible for any misuse.

## License

[MIT](LICENSE)
