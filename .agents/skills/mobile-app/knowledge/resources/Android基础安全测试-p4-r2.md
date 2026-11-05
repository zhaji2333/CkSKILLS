# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 4 · part 2

> 分段 2/2。索引见 `Android基础安全测试-p4.md`。

应用程序通常实施安全控制，这使得对应用程序执行安全审查变得更加困难，例如Root检测和证书固定。理想情况下，您将获得启用这些控件的应用程序版本和禁用控件的应用程序版本。这允许您分析控件的正确实现，之后您可以继续使用安全性较低的版本进行进一步测试。

当然，这并不总是可行的，您可能需要对启用所有安全控制的应用程序执行黑盒评估。下面的部分向您展示了如何绕过不同应用程序的证书固定。

#### 无线网络中的客户端隔离[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#client-isolation-in-wireless-networks)

一旦设置了拦截代理并拥有 MITM 位置，您可能仍然看不到任何东西。这可能是由于应用程序中的限制（请参阅下一节），但也可能是由于您所连接的 Wi-Fi 中所谓的客户端隔离。

[无线客户端隔离](https://documentation.meraki.com/MR/Firewall_and_Traffic_Shaping/Wireless_Client_Isolation)是一种安全功能，可防止无线客户端相互通信。此功能对来宾和 BYOD SSID 很有用，可增加安全级别以限制连接到无线网络的设备之间的攻击和威胁。

如果我们需要测试的Wi-Fi有客户端隔离怎么办？

你可以在你的Android设备上配置代理指向127.0.0.1:8080，通过USB连接你的手机到你的主机并使用adb做一个反向端口转发：

```
adb reverse tcp:8080 tcp:8080
```

完成此操作后，Android 手机上的所有代理流量都将转到 127.0.0.1 上的 8080 端口，并将通过 adb 重定向到主机上的 127.0.0.1:8080，现在您将在 Burp 中看到流量。使用此技巧，您还可以在具有客户端隔离的 Wi-Fi 中测试和拦截流量。

#### 非代理感知应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#non-proxy-aware-apps)

一旦设置了拦截代理并拥有 MITM 位置，您可能仍然看不到任何东西。这主要是由于以下原因：

- 该应用程序使用像 Xamarin 这样的框架，它Root本不使用 Android 操作系统的代理设置或
- 您正在测试的应用程序正在验证是否设置了代理并且现在不允许任何通信。

在这两种情况下，您都需要额外的步骤才能最终看到流量。在下面的部分中，我们将描述两种不同的解决方案，bettercap 和 iptables。

您还可以使用受您控制的接入点来重定向流量，但这需要额外的硬件，我们现在专注于软件解决方案。

> 对于这两种解决方案，您需要在代理选项卡/选项/编辑界面中的 Burp 中激活“支持不可见代理”。

##### IPTABLES[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#iptables)

您可以在 Android 设备上使用 iptables 将所有流量重定向到您的拦截代理。以下命令会将端口 80 重定向到在端口 8080 上运行的代理

```
iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination <Your-Proxy-IP>:8080
```

验证 iptables 设置并检查 IP 和端口。

```
$ iptables -t nat -L
Chain PREROUTING (policy ACCEPT)
target     prot opt source               destination

Chain INPUT (policy ACCEPT)
target     prot opt source               destination

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination
DNAT       tcp  --  anywhere             anywhere             tcp dpt:5288 to:<Your-Proxy-IP>:8080

Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination

Chain natctrl_nat_POSTROUTING (0 references)
target     prot opt source               destination

Chain oem_nat_pre (0 references)
target     prot opt source               destination
```

如果你想重置 iptables 配置，你可以刷新规则：

```
iptables -t nat -F
```

##### 贝特帽[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bettercap)

[阅读“测试网络通信](https://mas.owasp.org/MASTG/General/0x04f-Testing-Network-Communication/)”一章和测试用例“[模拟中间人攻击](https://mas.owasp.org/MASTG/General/0x04f-Testing-Network-Communication/#simulating-a-man-in-the-middle-attack-with-bettercap)”以进一步准备和运行 bettercap 的说明。

运行代理的主机和 Android 设备必须连接到同一无线网络。使用以下命令启动 bettercap，将下面的 IP 地址 (XXXX) 替换为您的 Android 设备的 IP 地址。

```
$ sudo bettercap -eval "set arp.spoof.targets X.X.X.X; arp.spoof on; set arp.spoof.internal true; set arp.spoof.fullduplex true;"
bettercap v2.22 (built for darwin amd64 with go1.12.1) [type 'help' for a list of commands]

[19:21:39] [sys.log] [inf] arp.spoof enabling forwarding
[19:21:39] [sys.log] [inf] arp.spoof arp spoofer started, probing 1 targets.
```

#### 代理检测[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#proxy-detection)

一些移动应用程序正在尝试检测是否设置了代理。如果是这种情况，他们会认为这是恶意的并且无法正常工作。

为了绕过这种保护机制，您可以设置 bettercap 或配置不需要在您的 Android 手机上设置代理的 iptables。我们之前没有提到但适用于此场景的第三个选项是使用 Frida。[`ProxyInfo`](https://developer.android.com/reference/android/net/ProxyInfo)在 Android 上可以通过查询类并检查 getHost() 和 getPort() 方法来检测是否设置了系统代理。可能有多种其他方法可以实现相同的任务，您需要反编译 APK 才能识别实际的类和方法名称。

您可以在下面找到 Frida 脚本的样板源代码，该脚本将帮助您重载验证代理是否已设置并始终返回 false 的方法（在本例中称为 isProxySet）。即使现在配置了代理，应用程序现在也会认为没有设置任何代理，因为函数返回 false。

```
setTimeout(function(){
    Java.perform(function (){
        console.log("[*] Script loaded")

        var Proxy = Java.use("<package-name>.<class-name>")

        Proxy.isProxySet.overload().implementation = function() {
            console.log("[*] isProxySet function invoked")
            return false
        }
    });
});
```

### 绕过证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypassing-certificate-pinning)

一些应用程序将实施 SSL Pinning，这会阻止应用程序接受您的拦截证书作为有效证书。这意味着您将无法监控应用程序和服务器之间的流量。

对于大多数应用程序，可以在几秒钟内绕过证书固定，但前提是应用程序使用这些工具涵盖的 API 函数。如果应用程序使用自定义框架或库实施 SSL Pinning，则必须手动修补和停用 SSL Pinning，这可能很耗时。

本节介绍绕过 SSL Pinning 的各种方法，并提供有关在现有工具无济于事时应该采取的措施的指导。

#### 绕过方法[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypassing-methods)

有几种方法可以绕过黑盒测试的证书固定，具体取决于设备上可用的框架：

- Cydia Substrate：安装[Android-SSL-TrustKiller](https://github.com/iSECPartners/Android-SSL-TrustKiller)包。
- Frida：使用[frida-multiple-unpinning](https://codeshare.frida.re/@akabe1/frida-multiple-unpinning/)脚本。
- objection：使用`android sslpinning disable`命令。
- Xposed：安装[TrustMeAlready](https://github.com/ViRb3/TrustMeAlready)或[SSLUnpinning](https://github.com/ac-pm/SSLUnpinning_Xposed)模块。

如果你有安装了 frida-server 的 root 设备，你可以通过运行以下[Objection](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#objection)命令来绕过 SSL 固定（如果你使用的是非 root 设备，请[重新打包你的应用程序）：](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#repackaging-apps)

```
android sslpinning disable
```

下面是一个输出示例：

![反对 Android SSL Pinning 绕过](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/Images/Chapters/0x05b/android_ssl_pinning_bypass.png)

