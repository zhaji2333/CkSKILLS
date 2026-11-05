# 四、动态分析要点

> 来源：CkSKILLS v1 `windows-reverse-engineering` §四、动态分析要点（迁移至 v2 知识块）

### 1. 调试基础
```
x64dbg：
  断点：bp <addr> / 条件断点 / 内存断点 / 硬件断点
  追踪：TraceInto/TraceOver → 记录执行流
  内存：内存窗口、堆栈窗口、 watches
WinDbg：
  !analyze -v（崩溃分析）
  !exchain / !dh / !handle
  sxe ld:<module>（模块加载断点）
  ba <size> <addr>（硬件断点）
```

### 2. 输入点 Hook
```
Frida hook 危险函数：
  Interceptor.attach(Module.findExportByName(null, 'memcpy'), {
    onEnter: function(args) {
      console.log('memcpy dst=', args[0], 'src=', args[1], 'len=', args[2].toInt32());
    }
  });
API Monitor：批量监控文件/注册表/网络/进程 API
Procmon：文件+注册表活动追踪
```

### 3. 网络协议逆向
```
1. Wireshark 抓包 → 提取协议字段
2. boofuzz/自定义脚本变异输入
3. 在 recv/WSARecv 下断 → 反推解析逻辑
4. 定位长度字段/魔数/校验 → 构造合规包
5. 在协议解析函数中寻找溢出点
```
