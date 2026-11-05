# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 5 · part 2

> 分段 2/2。索引见 `Android篡改和逆向工程-p5.md`。

│      ╎│   0x000017a8      sub r0, fp, 0xc
│      ╎│   0x000017ac      add r1, r0, r1
│      ╎│   0x000017b0      add r3, r1, r3
│      ╎│   0x000017b4      strb r2, [r3]
│      ╎│   0x000017b8      ldr r3, [var_10h]                          ; str.
│      ╎│                                                              ; 0x10 ; entry.preinit0
│      ╎│   0x000017bc      add r3, r3, 2                              ; "ELF\x01\x01\x01" ; aav.0x00000001
│      ╎│   0x000017c0      str r3, [var_10h]                          ; str.
│      ╎│                                                              ; 0x10
│      ╎│   0x000017c4      ldr r3, [var_14h]                          ; 0x14 ; entry.preinit0
│      ╎│   0x000017c8      add r3, r3, 1
│      ╎│   0x000017cc      str r3, [var_14h]                          ; 0x14
│      ╎│   ; CODE XREF from fcn.00001760 (0x1780)
│      ╎╰─> 0x000017d0      ldr r3, [var_14h]                          ; 0x14 ; entry.preinit0
│      ╎    0x000017d4      cmp r3, 4                                  ; aav.0x00000004 ; aav.0x00000001 ; aav.0x00000001
│      ╰──< 0x000017d8      ble 0x1784                                 ; likely
│           0x000017dc      ldrb r4, [fp, -0x1c]                       ; "4"
│           0x000017e0      bl fcn.000016f0
│           0x000017e4      mov r3, r0
│           0x000017e8      cmp r4, r3
│       ╭─< 0x000017ec      bne 0x1854                                 ; likely
│       │   0x000017f0      ldrb r4, [fp, -0x1b]
│       │   0x000017f4      bl fcn.0000170c
│       │   0x000017f8      mov r3, r0
│       │   0x000017fc      cmp r4, r3
│      ╭──< 0x00001800      bne 0x1854                                 ; likely
│      ││   0x00001804      ldrb r4, [fp, -0x1a]
│      ││   0x00001808      bl fcn.000016f0
│      ││   0x0000180c      mov r3, r0
│      ││   0x00001810      cmp r4, r3
│     ╭───< 0x00001814      bne 0x1854                                 ; likely
│     │││   0x00001818      ldrb r4, [fp, -0x19]
│     │││   0x0000181c      bl fcn.00001728
│     │││   0x00001820      mov r3, r0
│     │││   0x00001824      cmp r4, r3
│    ╭────< 0x00001828      bne 0x1854                                 ; likely
│    ││││   0x0000182c      ldrb r4, [fp, -0x18]
│    ││││   0x00001830      bl fcn.00001744
│    ││││   0x00001834      mov r3, r0
│    ││││   0x00001838      cmp r4, r3
│   ╭─────< 0x0000183c      bne 0x1854                                 ; likely
│   │││││   0x00001840      ldr r3, [0x0000186c]                       ; [0x186c:4]=0x270 section..hash ; section..hash
│   │││││   0x00001844      add r3, pc, r3                             ; 0x1abc ; "Product activation passed. Congratulations!"
│   │││││   0x00001848      mov r0, r3                                 ; 0x1abc ; "Product activation passed. Congratulations!" ;
│   │││││   0x0000184c      bl sym.imp.puts                            ; int puts(const char *s)
│   │││││                                                              ; int puts("Product activation passed. Congratulations!")
│  ╭──────< 0x00001850      b 0x1864
│  ││││││   ; CODE XREFS from fcn.00001760 (0x17ec, 0x1800, 0x1814, 0x1828, 0x183c)
│  │╰╰╰╰╰─> 0x00001854      ldr r3, aav.0x00000288                     ; [0x1870:4]=0x288 aav.0x00000288
│  │        0x00001858      add r3, pc, r3                             ; 0x1ae8 ; "Incorrect serial." ;
│  │        0x0000185c      mov r0, r3                                 ; 0x1ae8 ; "Incorrect serial." ;
│  │        0x00001860      bl sym.imp.puts                            ; int puts(const char *s)
│  │                                                                   ; int puts("Incorrect serial.")
│  │        ; CODE XREF from fcn.00001760 (0x1850)
│  ╰──────> 0x00001864      sub sp, fp, 8
╰           0x00001868      pop {r4, fp, pc}                           ; entry.preinit0 ; entry.preinit0 ;
```

讨论函数中的所有指令超出了本章的范围，我们将只讨论分析所需的重点。在验证函数中，存在一个循环，该循环`0x00001784`在 offset 处执行 XOR 运算`0x00001798`。循环在下面的图形视图中更清晰可见。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/loop_1784.png)

XOR 是一种非常常用的*加密*信息的技术，其中混淆是目标而不是安全性。**XOR 不应该用于任何严格的加密**，因为它可以使用频率分析来破解。因此，仅在此类验证逻辑中存在 XOR 加密总是需要特别注意和分析。

向前移动，在偏移处`0x000017dc`，将从上面获得的 XOR 解码值与子函数调用的返回值进行比较`0x000017e8`。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/values_compare_17dc.png)

显然这个功能并不复杂，可以手动分析，但仍然是一项繁琐的工作。尤其是在大型代码库上工作时，时间可能是一个主要限制因素，因此希望能够自动执行此类分析。动态符号执行正是在这些情况下很有帮助。在上面的 crackme 中，符号执行引擎可以通过映射Licenses（许可证）检查的第一条指令 (at `0x00001760`) 和打印“产品激活通过”消息的代码(at `0x00001840`)之间的路径来确定输入字符串的每个字节的约束条件.

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/graph_ifelse_1760.png)

从上述步骤获得的约束被传递给求解器引擎，该引擎找到满足它们的输入 - 有效的Licenses（许可证）密钥。

您需要执行几个步骤来初始化 Angr 的符号执行引擎：

- 将二进制文件加载到 a`Project`中，这是 Angr 中任何类型分析的起点。
- 传递分析应从其开始的地址。在这种情况下，我们将使用串行验证函数的第一条指令初始化状态。这使得问题更容易解决，因为您避免了以符号方式执行 Base32 实现。
- 传递分析应该到达的代码块的地址。在这种情况下，这是 offset `0x00001840`，负责打印“产品激活已通过”消息的代码所在的位置。
- 此外，指定分析不应到达的地址。在这种情况下，打印“Incorrect serial”消息的代码块`0x00001854`并不有趣。

> 请注意，Angr 加载器将加载基地址为 的 PIE 可执行文件，`0x400000`在将其传递给 Angr 之前，需要将其添加到 Cutter 的偏移量中。

最终的解决方案脚本如下所示：

```
import angr # Version: 9.2.2
import base64

load_options = {}

b = angr.Project("./validate", load_options = load_options)
# The key validation function starts at 0x401760, so that's where we create the initial state.
# This speeds things up a lot because we're bypassing the Base32-encoder.

options = {
    angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
    angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
}

state = b.factory.blank_state(addr=0x401760, add_options=options)

simgr = b.factory.simulation_manager(state)
simgr.explore(find=0x401840, avoid=0x401854)

# 0x401840 = Product activation passed
