# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 3 · part 2

> 分段 2/2。索引见 `Android基础安全测试-p3.md`。

要远程嗅探 Android 手机的网络流量，首先执行`tcpdump`并将其输出通过管道传输到`netcat`(nc)：

```
tcpdump -i wlan0 -s0 -w - | nc -l -p 11111
```

上面的 tcpdump 命令涉及

- 在 wlan0 接口上监听，
- 以字节为单位定义捕获的大小（快照长度）以获取所有内容（-s0），以及
- 写入文件 (-w)。我们传递的不是文件名，`-`这将使 tcpdump 写入标准输出。

通过使用管道 ( `|`)，我们将 tcpdump 的所有输出发送到 netcat，它在端口 11111 上打开一个侦听器。您通常需要监视 wlan0 接口。如果您需要另一个接口，请使用命令列出可用选项`$ ip addr`。

要访问端口 11111，您需要通过 adb 将端口转发到您的主机。

```
adb forward tcp:11111 tcp:11111
```

以下命令通过 netcat 和管道连接到转发端口到 Wireshark。

```
nc localhost 11111 | wireshark -k -S -i -
```

Wireshark 应立即启动 (-k)。它通过连接到转发端口的 netcat 从标准输入 (-i -) 获取所有数据。您应该从 wlan0 接口看到所有手机的流量。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/Android_Wireshark.png)

您可以使用 Wireshark 以人类可读的格式显示捕获的流量。弄清楚使用了哪些协议以及它们是否未加密。捕获所有流量（TCP 和 UDP）很重要，因此您应该执行被测应用程序的所有功能并对其进行分析。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/tcpdump_and_wireshard_on_android.png)

这个巧妙的小技巧现在可以让您识别使用了哪种协议以及应用程序正在与哪些端点通信。现在的问题是，如果 Burp 无法显示流量，我该如何测试端点？对此没有简单的答案，但一些 Burp 插件可以帮助您入门。

#### Firebase/谷歌云消息传递（FCM/GCM）[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#firebasegoogle-cloud-messaging-fcmgcm)

Firebase Cloud Messaging (FCM) 是 Google Cloud Messaging (GCM) 的继任者，是 Google 提供的一项免费服务，允许您在应用程序服务器和客户端应用程序之间发送消息。服务器和客户端应用程序通过 FCM/GCM 连接服务器进行通信，该服务器处理下游和上游消息。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/FCM-notifications-overview.png)

下游消息（推送通知）从应用服务器发送到客户端应用；上游消息从客户端应用程序发送到服务器。

FCM 适用于 Android、iOS 和 Chrome。FCM 目前提供两种连接服务器协议：HTTP 和 XMPP。如[官方文档](https://firebase.google.com/docs/cloud-messaging/server#choose)所述，这些协议的实现方式不同。以下示例演示了如何拦截这两种协议。

##### 测试设置的准备[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#preparation-of-test-setup)

您需要在手机上配置 iptables 或使用 bettercap 才能拦截流量。

FCM 可以使用 XMPP 或 HTTP 与 Google 后端通信。

##### HTTP[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#http)

FCM 使用端口 5228、5229 和 5230 进行 HTTP 通信。通常，仅使用端口 5228。

- 为 FCM 使用的端口配置本地端口转发。以下示例适用于 macOS：

```
$ echo "
rdr pass inet proto tcp from any to any port 5228-> 127.0.0.1 port 8080
rdr pass inet proto tcp from any to any port 5229 -> 127.0.0.1 port 8080
rdr pass inet proto tcp from any to any port 5230 -> 127.0.0.1 port 8080
" | sudo pfctl -ef -
```

- 拦截代理必须监听上面端口转发规则中指定的端口（端口8080）。

##### XMPP[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#xmpp)

对于 XMPP 通信，[FCM 使用端口](https://firebase.google.com/docs/cloud-messaging/xmpp-server-ref)5235（生产）和 5236（测试）。

- 为 FCM 使用的端口配置本地端口转发。以下示例适用于 macOS：

```
$ echo "
rdr pass inet proto tcp from any to any port 5235-> 127.0.0.1 port 8080
rdr pass inet proto tcp from any to any port 5236 -> 127.0.0.1 port 8080
" | sudo pfctl -ef -
```

##### 拦截请求[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#intercepting-the-requests)

拦截代理必须监听上面端口转发规则中指定的端口（端口8080）。

启动应用程序并触发使用 FCM 的函数。您应该在拦截代理中看到 HTTP 消息。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/FCM_Intercept.png)

##### 推送通知的端到端加密[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#end-to-end-encryption-for-push-notifications)

作为额外的安全层，可以使用[Capillary](https://github.com/google/capillary)对推送通知进行加密。Capillary 是一个库，用于简化从基于 Java 的应用程序服务器到 Android 客户端的端到端 (E2E) 加密推送消息的发送。

### 设置拦截代理[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#setting-up-an-interception-proxy)

一些工具支持对依赖 HTTP(S) 协议的应用程序进行网络分析。最重要的工具是所谓的拦截代理；[OWASP ZAP](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#owasp-zap)和[Burp Suite](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#burp-suite) Professional 是最著名的。拦截代理为测试人员提供了中间人的位置。这个位置对于读取和/或修改所有应用程序请求和端点响应很有用，这些请求和端点响应用于测试授权、会话、管理等。

#### 虚拟设备的拦截代理[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#interception-proxy-for-a-virtual-device)

##### 在 ANDROID 虚拟设备 (AVD) 上设置 WEB 代理[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#setting-up-a-web-proxy-on-an-android-virtual-device-avd)

以下过程适用于 Android Studio 3.x 附带的 Android 模拟器，用于在模拟器上设置 HTTP 代理：

1. 设置您的代理以侦听本地主机，例如端口 8080。
2. 在模拟器设置中配置 HTTP 代理：
   - 单击模拟器菜单栏中的三个点
   - 打开**设置**菜单
   - 单击**代理**选项卡
   - 选择**手动代理配置**
   - **在主机名字**段中输入“127.0.0.1”，在**端口号**字段中输入您的代理端口（例如，“8080”）
   - 点击**应用**

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/emulator-proxy.png)

HTTP 和 HTTPS 请求现在应该通过主机上的代理进行路由。如果没有，请尝试关闭和打开飞行模式。

还可以在启动 AVD 时使用[emulator 命令在命令行上配置 AVD 的代理。](https://developer.android.com/studio/run/emulator-commandline)以下示例启动 AVD Nexus_5X_API_23 并将代理设置为 127.0.0.1 和端口 8080。

```
emulator @Nexus_5X_API_23 -http-proxy 127.0.0.1:8080
```

