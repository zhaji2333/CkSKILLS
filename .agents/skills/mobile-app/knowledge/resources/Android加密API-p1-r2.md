# Android 加密 API[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#android-cryptographic-apis) · part 1 · part 2

> 分段 2/2。索引见 `Android加密API-p1.md`。

表示该`KeyGenParameterSpec`密钥可用于加密和解密，但不能用于其他目的，如签名或验证。它进一步指定块模式 (CBC)、填充 (PKCS #7)，并明确指定需要随机加密（这是默认设置）。`"AndroidKeyStore"`是本示例中使用的security providers的名称。这将自动确保密钥存储在`AndroidKeyStore`保护密钥的受益人中。

GCM 是另一种 AES 块模式，与其他较旧的模式相比，它提供了额外的安全优势。除了在密码学上更安全之外，它还提供身份验证。使用 CBC（和其他模式）时，需要使用 HMAC 单独执行身份验证（请参阅“ [Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章）。请注意，GCM 是唯一[不支持填充](https://developer.android.com/training/articles/keystore.html#SupportedCiphers)的 AES 模式。

尝试违反上述规范使用生成的密钥将导致安全异常。

下面是使用该密钥进行加密的示例：

```
String AES_MODE = KeyProperties.KEY_ALGORITHM_AES
        + "/" + KeyProperties.BLOCK_MODE_CBC
        + "/" + KeyProperties.ENCRYPTION_PADDING_PKCS7;
KeyStore AndroidKeyStore = AndroidKeyStore.getInstance("AndroidKeyStore");

// byte[] input
Key key = AndroidKeyStore.getKey(keyAlias, null);

Cipher cipher = Cipher.getInstance(AES_MODE);
cipher.init(Cipher.ENCRYPT_MODE, key);

byte[] encryptedBytes = cipher.doFinal(input);
byte[] iv = cipher.getIV();
// save both the IV and the encryptedBytes
```

IV（初始化向量）和加密后的字节都需要存储；否则无法解密。

下面是密文的解密方式。是加密的`input`字节数组，`iv`是加密步骤的初始化向量：

```
// byte[] input
// byte[] iv
Key key = AndroidKeyStore.getKey(AES_KEY_ALIAS, null);

Cipher cipher = Cipher.getInstance(AES_MODE);
IvParameterSpec params = new IvParameterSpec(iv);
cipher.init(Cipher.DECRYPT_MODE, key, params);

byte[] result = cipher.doFinal(input);
```

由于 IV 每次都是随机生成的，因此应将其与密文 ( `encryptedBytes`) 一起保存，以便稍后解密。

在 Android 6.0（API 级别 23）之前，不支持 AES 密钥生成。因此，许多实现选择使用 RSA 并生成用于非对称加密的公私密钥对，使用`KeyPairGeneratorSpec`或用于`SecureRandom`生成 AES 密钥。

这是用于创建 RSA 密钥对`KeyPairGenerator`的示例：`KeyPairGeneratorSpec`

```
Date startDate = Calendar.getInstance().getTime();
Calendar endCalendar = Calendar.getInstance();
endCalendar.add(Calendar.YEAR, 1);
Date endDate = endCalendar.getTime();
KeyPairGeneratorSpec keyPairGeneratorSpec = new KeyPairGeneratorSpec.Builder(context)
        .setAlias(RSA_KEY_ALIAS)
        .setKeySize(4096)
        .setSubject(new X500Principal("CN=" + RSA_KEY_ALIAS))
        .setSerialNumber(BigInteger.ONE)
        .setStartDate(startDate)
        .setEndDate(endDate)
        .build();

KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA",
        "AndroidKeyStore");
keyPairGenerator.initialize(keyPairGeneratorSpec);

KeyPair keyPair = keyPairGenerator.generateKeyPair();
```

此示例创建密钥大小为 4096 位（即模数大小）的 RSA 密钥对。也可以用类似的方式生成椭圆曲线 (EC) 密钥。但是，从 Android 11（API 级别 30）开始，[AndroidKeyStore 不支持使用 EC 密钥进行加密或解密](https://developer.android.com/guide/topics/security/cryptography#SupportedCipher)。它们只能用于签名。

可以使用基于密码的密钥派生函数版本 2 (PBKDF2) 从密码生成对称加密密钥。该加密协议旨在生成可用于加密目的的加密密钥。算法的输入参数根据[弱密钥生成函数](https://mas.owasp.org/MASTG/General/0x04g-Testing-Cryptography/#weak-key-generation-functions)部分进行调整。下面的代码清单说明了如何根据密码生成强加密密钥。

```
public static SecretKey generateStrongAESKey(char[] password, int keyLength)
{
    //Initialize objects and variables for later use
    int iterationCount = 10000;
    int saltLength     = keyLength / 8;
    SecureRandom random = new SecureRandom();
    //Generate the salt
    byte[] salt = new byte[saltLength];
    random.nextBytes(salt);
    KeySpec keySpec = new PBEKeySpec(password.toCharArray(), salt, iterationCount, keyLength);
    SecretKeyFactory keyFactory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
    byte[] keyBytes = keyFactory.generateSecret(keySpec).getEncoded();
    return new SecretKeySpec(keyBytes, "AES");
}
```

上述方法需要一个包含密码和所需密钥长度（以位为单位）的字符数组，例如 128 或 256 位 AES 密钥。我们定义了 PBKDF2 算法将使用的 10,000 轮迭代计数。增加迭代次数会显着增加对密码进行暴力攻击的工作量，但它会影响性能，因为密钥派生需要更多的计算能力。我们将 salt 大小定义为等于密钥长度，我们除以 8 以处理位到字节的转换。我们使用`SecureRandom`该类随机生成盐。显然，盐是您想要保持不变的东西，以确保为相同提供的密码一次又一次地生成相同的加密密钥。请注意，您可以将盐私下存储在`SharedPreferences`. 建议将 salt 从 Android 备份机制中排除，以防止在较高风险数据的情况下同步。

> 请注意，如果您将获得 root 权限的设备或打过补丁（例如重新打包）的应用程序视为对数据的威胁，最好使用放置在`AndroidKeystore`. 基于密码的加密 (PBE) 密钥是使用推荐的`PBKDF2WithHmacSHA1`算法生成的，直到 Android 8.0（API 级别 26）。对于更高的 API 级别，最好使用`PBKDF2withHmacSHA256`，这将以更长的哈希值结束。

