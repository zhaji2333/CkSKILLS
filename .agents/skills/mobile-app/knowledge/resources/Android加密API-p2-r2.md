# Android 加密 API[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#android-cryptographic-apis) · part 2 · part 2

> 分段 2/2。索引见 `Android加密API-p2.md`。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#static-analysis_3)

识别随机数生成器的所有实例并查找自定义或众所周知的不安全类。例如，`java.util.Random`为每个给定的种子值生成相同的数字序列；因此，数字的顺序是可以预测的。相反，应该选择一个经过严格审查的算法，该算法当前被该领域的专家认为是强大的，并且应该使用经过充分测试的具有足够长度种子的实现。

`SecureRandom`标识不是使用默认构造函数创建的所有实例。指定种子值可能会降低随机性。更喜欢它的[无参数构造函数，`SecureRandom`](https://www.securecoding.cert.org/confluence/display/java/MSC02-J.+Generate+strong+random+numbers)它使用系统指定的种子值来生成一个 128 字节长的随机数。

一般来说，如果 PRNG 没有被宣传为密码安全（例如`java.util.Random`），那么它可能是统计 PRNG，不应在安全敏感的上下文中使用。如果生成器已知并且可以猜到种子，伪随机数生成器[可以生成可预测的数字。](https://www.securecoding.cert.org/confluence/display/java/MSC63-J.+Ensure+that+SecureRandom+is+properly+seeded)128 位种子是生成“足够随机”数字的良好起点。

一旦攻击者知道使用哪种类型的弱伪随机数生成器 (PRNG)，编写概念验证以根据先前观察到的随机值生成下一个随机值就很容易了，就像[对 Java Random 所做的那样](https://franklinta.com/2014/08/31/predicting-the-next-math-random-in-java/). 在非常弱的自定义随机生成器的情况下，可以从统计上观察模式。尽管推荐的方法无论如何都是反编译 APK 并检查算法（请参阅静态分析）。

如果你想测试随机性，你可以尝试捕获大量数字并使用 Burp 的[排序器](https://portswigger.net/burp/documentation/desktop/tools/sequencer)检查随机性的质量有多好。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#dynamic-analysis_3)

您可以对上述类和方法使用[方法跟踪来确定正在使用的输入/输出值。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#method-tracing)

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#references)

- [#nelenkov] - N. Elenkov，Android Security Internals，No Starch Press，2014 年，第 5 章。

### 密码学参考[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#cryptography-references)

- Android 开发者博客：NDK 开发者的变化 - https://android-developers.googleblog.com/2016/06/android-changes-for-ndk-developers.html
- Android 开发者博客：不推荐使用加密提供程序 - https://android-developers.googleblog.com/2016/06/security-crypto-provider-deprecated-in.html
- Android 开发者博客：Android P 中的密码学变化 - https://android-developers.googleblog.com/2018/03/cryptography-changes-in-android-p.html
- Android 开发者博客：一些 SecureRandom 想法 - https://android-developers.googleblog.com/2013/08/some-securerandom-thoughts.html
- Android 开发者文档 - https://developer.android.com/guide
- BSI 建议 - https://www.keylength.com/en/8/
- Ida Pro - https://www.hex-rays.com/products/ida/
- 充气城堡军团 - https://www.bouncycastle.org/java.html
- NIST 密钥长度建议 - https://www.keylength.com/en/4/
- 安全提供商 - https://developer.android.com/reference/java/security/Provider.html
- 海绵城堡 - https://rtyley.github.io/spongycastle/

### 安全随机引用[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#securerandom-references)

- BurpProxy 定序器 - https://portswigger.net/burp/documentation/desktop/tools/sequencer
- SecureRandom 的正确播种 - https://www.securecoding.cert.org/confluence/display/java/MSC63-J.+Ensure+that+SecureRandom+is+properly+seeded

### 测试密钥管理参考[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#testing-key-management-references)

- Android 钥匙串 API - https://developer.android.com/reference/android/security/KeyChain
- Android 密钥库 API - https://developer.android.com/reference/java/security/KeyStore.html
- Android Keystore 系统 - https://developer.android.com/training/articles/keystore#java
- Android Pie 功能和 API - https://developer.android.com/about/versions/pie/android-9.0#secure-key-import
- KeyInfo 文档 - https://developer.android.com/reference/android/security/keystore/KeyInfo
- SharedPreferences - https://developer.android.com/reference/android/content/SharedPreferences.html

### 关键认证参考[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#key-attestation-references)

- Android 密钥证明 - https://developer.android.com/training/articles/security-key-attestation
- 证明和断言 - https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API/Attestation_and_Assertion
- FIDO 联盟技术说明 - https://fidoalliance.org/fido-technotes-the-truth-about-attestation/
- FIDO 联盟白皮书 - https://fidoalliance.org/wp-content/uploads/Hardware-backed_Keystore_White_Paper_June2018.pdf
- 谷歌示例代码 - https://github.com/googlesamples/android-key-attestation/tree/master/server
- 验证 Android 密钥证明 - https://medium.com/@herrjemand/webauthn-fido2-verifying-android-keystore-attestation-4a8835b33e9d
- W3C Android 密钥证明 - https://www.w3.org/TR/webauthn/#android-key-attestation

#### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#owasp-masvs)

- MSTG-STORAGE-1：“需要使用系统凭证存储设施来存储敏感数据，例如 PII、用户凭证或加密密钥。”
- MSTG-CRYPTO-1：“该应用程序不依赖使用硬编码密钥的对称加密作为唯一的加密方法。”
- MSTG-CRYPTO-2：“该应用程序使用经过验证的加密原语实现。”
- MSTG-CRYPTO-3：“该应用程序使用适合特定用例的加密原语，并配置了符合行业最佳实践的参数。”
- MSTG-CRYPTO-4：“该应用程序不使用出于安全目的而被广泛认为已弃用的加密协议或算法。”
- MSTG-CRYPTO-5：“该应用程序不会出于多种目的重复使用相同的加密密钥。”
- MSTG-CRYPTO-6：“所有随机值都是使用足够安全的随机数生成器生成的。”
