# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 2 · part 1

> 分段 1/2。索引见 `Android数据存储-p2.md`。

# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 2

> 分段 2/6。索引见 `Android数据存储.md`。

## 承接

虽然密钥证明过程可以直接在应用程序中实现，但出于安全原因，建议在服务器端实现。以下是安全实施密钥证明的高级指南：

- 服务器应通过使用 CSPRNG（加密安全随机数生成器）安全地创建随机数来启动密钥证明过程，并将该随机数作为质询发送给用户。

- 客户端应`setAttestationChallenge`使用从服务器收到的质询调用 API，然后应使用该`KeyStore.getCertificateChain`方法检索证明证书链。

- 应将证明响应发送到服务器进行验证，并应执行以下检查以验证密钥证明响应：

- 验证证书链，直到根并执行证书健全性检查，例如有效性、完整性和可信度。如果链中的证书都没有被撤销，请检查由 Google 维护的[证书撤销状态列表。](https://developer.android.com/training/articles/security-key-attestation#root_certificat)

- 检查根证书是否使用谷歌证明根密钥签名，这使得证明过程值得信赖。

- 提取证明

  证书扩展数据

  ，它出现在证书链的第一个元素中，并执行以下检查：

  - 验证证明质询是否具有与启动证明过程时在服务器上生成的相同的值。
  - 验证密钥证明响应中的签名。
  - 验证 Keymaster 的安全级别以确定设备是否具有安全密钥存储机制。Keymaster 是一款在安全上下文中运行并提供所有安全密钥库操作的软件。安全级别将是`Software`或`TrustedEnvironment`之一`StrongBox`。`TrustedEnvironment`如果安全级别为或`StrongBox`且证明证书链包含使用 Google 证明根密钥签名的根证书，则客户端支持硬件级密钥证明。
  - 验证客户端的状态以确保完整的信任链 - 验证启动密钥、锁定引导加载程序和验证启动状态。
  - 此外，您还可以验证密钥对的属性，例如用途、访问时间、身份验证要求等。

> 请注意，如果由于任何原因该过程失败，则意味着密钥不在安全硬件中。这并不意味着密钥已泄露。

Android Keystore 认证响应的典型示例如下所示：

```
{
    "fmt": "android-key",
    "authData": "9569088f1ecee3232954035dbd10d7cae391305a2751b559bb8fd7cbb229bd...",
    "attStmt": {
        "alg": -7,
        "sig": "304402202ca7a8cfb6299c4a073e7e022c57082a46c657e9e53...",
        "x5c": [
            "308202ca30820270a003020102020101300a06082a8648ce3d040302308188310b30090603550406130...",
            "308202783082021ea00302010202021001300a06082a8648ce3d040302308198310b300906035504061...",
            "3082028b30820232a003020102020900a2059ed10e435b57300a06082a8648ce3d040302308198310b3..."
        ]
    }
}
```

在上面的 JSON 片段中，密钥具有以下含义： `fmt`：证明语句格式标识符 `authData`：它表示证明的身份验证器数据 `alg`：用于签名的算法 `sig`：签名 `x5c`：证明证书链

注意：`sig`是通过连接`authData`和`clientDataHash`（服务器发送的质询）生成的，并使用签名算法通过凭据私钥进行`alg`签名，并在服务器端使用第一个证书中的公钥对其进行验证。

如需更多了解实施指南，可参考[Google Sample Code 。](https://github.com/googlesamples/android-key-attestation/blob/master/server/src/main/java/com/android/example/KeyAttestationExample.java)

从安全分析的角度来看，分析师可以对密钥证明的安全实施执行以下检查：

- 检查密钥证明是否完全在客户端实现。在这种情况下，可以通过篡改应用程序、方法Hook等方式轻松绕过。
- 检查服务器在启动密钥证明时是否使用随机质询。因为不这样做会导致不安全的实施，从而使其容易受到重放攻击。此外，应执行与挑战的随机性有关的检查。
- 检查服务器是否验证密钥证明响应的完整性。
- 检查服务器是否对链上证书进行完整性验证、信任验证、有效性等基本检查。

#### 安全密钥导入到密钥库[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#secure-key-import-into-keystore)

Android 9（API 级别 28）添加了将密钥安全导入到`AndroidKeystore`. 首先`AndroidKeystore`生成一个密钥对，使用`PURPOSE_WRAP_KEY`它也应该用证明证书保护，这对旨在保护导入到的密钥`AndroidKeystore`。加密密钥生成为 ASN.1 编码消息，其`SecureKeyWrapper`格式还包含对允许使用导入密钥的方式的描述。然后，密钥在`AndroidKeystore`属于生成包装密钥的特定设备的硬件内部被解密，因此它们永远不会以明文形式出现在设备的主机内存中。

![将密钥安全导入 Keystore](https://mas.owasp.org/assets/Images/Chapters/0x05d/Android9_secure_key_import_to_keystore.jpg)

Java 中的示例：

```
KeyDescription ::= SEQUENCE {
    keyFormat INTEGER,
    authorizationList AuthorizationList
}

SecureKeyWrapper ::= SEQUENCE {
    wrapperFormatVersion INTEGER,
    encryptedTransportKey OCTET_STRING,
    initializationVector OCTET_STRING,
    keyDescription KeyDescription,
    secureKey OCTET_STRING,
    tag OCTET_STRING
}
```

上面的代码显示了在生成 SecureKeyWrapper 格式的加密密钥时要设置的不同参数。查看 Android 文档以[`WrappedKeyEntry`](https://developer.android.com/reference/android/security/keystore/WrappedKeyEntry)获取更多详细信息。

在定义 KeyDescription AuthorizationList 时，以下参数将影响加密密钥的安全性：

- 参数指定使用密钥的`algorithm`加密算法
- 参数指定密钥的`keySize`大小（以位为单位），以密钥算法的正常方式测量
- 该`digest`参数指定可与密钥一起使用以执行签名和验证操作的摘要算法

#### 较旧的 KeyStore 实现[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#older-keystore-implementations)

较旧的 Android 版本不包含 KeyStore，但它们*确实*包含来自 JCA（Java 加密体系结构）的 KeyStore 接口。您可以使用实现此接口的 KeyStore 来确保使用 KeyStore 存储的密钥的保密性和完整性；建议使用 BouncyCastle KeyStore (BKS)。所有实现都基于文件存储在文件系统上这一事实；所有文件均受密码保护。要创建一个，您可以使用`KeyStore.getInstance("BKS", "BC") method`，其中“BKS”是 KeyStore 名称 (BouncyCastle Keystore)，“BC”是提供者 (BouncyCastle)。您还可以使用 SpongyCastle 作为包装器并按如下方式初始化 KeyStore `KeyStore.getInstance("BKS", "SC")`：

请注意，并非所有 KeyStore 都能正确保护存储在 KeyStore 文件中的密钥。

#### 钥匙链[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#keychain)

[KeyChain 类](https://developer.android.com/reference/android/security/KeyChain.html)用于存储和检索*系统范围内的*私钥及其相应的证书（链）。如果首次将某些内容导入 KeyChain，系统将提示用户设置锁屏 PIN 码或密码以保护凭据存储。请注意，KeyChain 是系统范围的，每个应用程序都可以访问存储在 KeyChain 中的资料。

检查源代码以确定原生 Android 机制是否识别敏感信息。敏感信息应该加密，而不是以明文形式存储。对于必须存储在设备上的敏感信息，可以使用多个 API 调用来通过`KeyChain`类保护数据。完成以下步骤：

- 确保该应用使用 Android KeyStore 和 Cipher 机制在设备上安全地存储加密信息。寻找模式`AndroidKeystore`, `import java.security.KeyStore`, `import javax.crypto.Cipher`, `import java.security.SecureRandom`, 和相应的用法。
- 使用该`store(OutputStream stream, char[] password)`函数将 KeyStore 存储到带有密码的磁盘。确保密码由用户提供，而不是硬编码。

#### 存储加密密钥：技术[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-a-cryptographic-key-techniques)

为了减少在 Android 设备上未经授权使用密钥的情况，Android KeyStore 允许应用程序在生成或导入密钥时指定对其密钥的授权使用。授权一旦做出，便无法更改。

存储密钥——从最安全到最不安全：

- 密钥存储在硬件支持的 Android KeyStore 中
- 所有密钥都存储在服务器上，经过强认证后可用
- 主密钥存储在服务器上，用于加密存储在 Android SharedPreferences 中的其他密钥
- 密钥每次都来自强大的用户提供的具有足够长度和盐的密码
- 密钥存储在 Android KeyStore 的软件实现中
- master key 存储在 Android Keystore 的软件实现中，用于加密存储在 SharedPreferences 中的其他密钥
- 【不推荐】所有key都存储在SharedPreferences中
- [不推荐] 在源代码中硬编码加密密钥
- 【不推荐】基于稳定属性的可预测混淆函数或密钥推导函数
- [不推荐] 将生成的密钥存储在公共场所（如`/sdcard/`）

##### 使用硬件支持的 ANDROID KEYSTORE 存储密钥[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-keys-using-hardware-backed-android-keystore)

如果设备运行的是 Android 7.0（API 级别 24）及更高版本且具有可用的硬件组件（可信执行环境 (TEE) 或安全元件 (SE)），您可以使用[硬件支持的 Android KeyStore 。](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#hardware-backed-android-keystore)[您甚至可以使用为密钥证明的安全实施](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#key-attestation)提供的指南来验证密钥是否由硬件支持。如果硬件组件不可用和/或需要支持 Android 6.0（API 级别 23）及以下版本，那么您可能希望将密钥存储在远程服务器上并在身份验证后使其可用。

##### 在服务器上存储密钥[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-keys-on-the-server)

可以将密钥安全地存储在密钥管理服务器上，但是应用程序需要在线才能解密数据。这可能是某些移动应用程序用例的限制，应该仔细考虑，因为这会成为应用程序架构的一部分，并且可能会严重影响可用性。

##### 从用户输入派生密钥[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#deriving-keys-from-user-input)

从用户提供的密码派生密钥是一种常见的解决方案（取决于您使用的 Android API 级别），但它也会影响可用性，可能会影响攻击面并可能引入其他弱点。

