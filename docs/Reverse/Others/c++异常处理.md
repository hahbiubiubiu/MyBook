## 概述

异常是程序在执行期间产生的问题。C++ 异常是指在程序运行时发生的特殊情况。

触发异常后，如果有对应的异常处理就会跳到异常处理去执行。

如果没有异常处理或者异常处理程序未成功处理异常，程序就会退出。

## 相关数据结构

### EXCEPTION_POINTERS

包含异常记录，其中包含与计算机无关的异常说明，以及异常时具有与计算机相关的处理器上下文说明的上下文记录。

```C++
typedef struct _EXCEPTION_POINTERS {
    PEXCEPTION_RECORD ExceptionRecord;
    PCONTEXT          ContextRecord;
} EXCEPTION_POINTERS, *PEXCEPTION_POINTERS;
```

* `EXCEPTION_RECORD`：指向`EXCEPTION_RECORD`结构的指针，该结构包含与计算机无关的异常说明。
* `CONTEXT`：指向`CONTEXT`结构的指针，该结构包含异常时处理器状态的特定于处理器的说明。

### EXCEPTION_RECORD

描述异常。

```C++
typedef struct _EXCEPTION_RECORD {
    DWORD                    ExceptionCode;
    DWORD                    ExceptionFlags;
    struct _EXCEPTION_RECORD *ExceptionRecord;
    PVOID                    ExceptionAddress;
    DWORD                    NumberParameters;
    ULONG_PTR                ExceptionInformation[EXCEPTION_MAXIMUM_PARAMETERS];
} EXCEPTION_RECORD;
```

* `ExceptionCode`：发生异常的原因。

  * | 值                                 | 含义                                                         |
    | :--------------------------------- | ------------------------------------------------------------ |
    | EXCEPTION_ACCESS_VIOLATION         | 线程尝试从虚拟地址读取或写入其没有相应访问权限的虚拟地址。   |
    | EXCEPTION_ARRAY_BOUNDS_EXCEEDED    | 线程尝试访问超出边界且基础硬件支持边界检查的数组元素。       |
    | EXCEPTION_BREAKPOINT               | 遇到断点。                                                   |
    | EXCEPTION_DATATYPE_MISALIGNMENT    | 线程尝试读取或写入在不提供对齐的硬件上未对齐的数据。 <br />例如，16 位值必须在 2 字节边界上对齐；4 字节边界上的 32 位值等。 |
    | EXCEPTION_FLT_DENORMAL_OPERAND     | 浮点运算中的一个操作数是反常运算。 非规范值太小，无法表示为标准浮点值。 |
    | EXCEPTION_FLT_DIVIDE_BY_ZERO       | 线程尝试将浮点值除以 0 的浮点除数。                          |
    | EXCEPTION_FLT_INEXACT_RESULT       | 浮点运算的结果不能完全表示为小数点。                         |
    | EXCEPTION_FLT_INVALID_OPERATION    | 此异常表示此列表中未包含的任何浮点异常。                     |
    | EXCEPTION_FLT_OVERFLOW             | 浮点运算的指数大于相应类型允许的量级。                       |
    | EXCEPTION_FLT_STACK_CHECK          | 堆栈因浮点运算而溢出或下溢。                                 |
    | EXCEPTION_FLT_UNDERFLOW            | 浮点运算的指数小于相应类型允许的量级。                       |
    | EXCEPTION_ILLEGAL_INSTRUCTION      | 线程尝试执行无效指令。                                       |
    | EXCEPTION_IN_PAGE_ERROR            | 线程尝试访问不存在的页面，但系统无法加载该页。<br /> 例如，如果在通过网络运行程序时网络连接断开，则可能会发生此异常。 |
    | EXCEPTION_INT_DIVIDE_BY_ZERO       | 线程尝试将整数值除以零的整数除数。                           |
    | EXCEPTION_INT_OVERFLOW             | 整数运算的结果导致执行结果中最重要的位。                     |
    | EXCEPTION_INVALID_DISPOSITION      | 异常处理程序向异常调度程序返回了无效处置。 <br />使用高级语言（如 C）的程序员不应遇到此异常。 |
    | EXCEPTION_NONCONTINUABLE_EXCEPTION | 线程尝试在发生不可连续的异常后继续执行。                     |
    | EXCEPTION_PRIV_INSTRUCTION         | 线程尝试执行在当前计算机模式下不允许其操作的指令。           |
    | EXCEPTION_SINGLE_STEP              | 跟踪陷阱或其他单指令机制指示已执行一个指令。                 |
    | EXCEPTION_STACK_OVERFLOW           | 线程占用了其堆栈。                                           |

* `ExceptionFlags`：此成员包含零个或多个异常标志。

  * | 异常标志                     | 含义                                                         |
    | :--------------------------- | :----------------------------------------------------------- |
    | EXCEPTION_NONCONTINUABLE     | 存在此标志表示异常是不可持续的异常，而缺少此标志则表示该异常是一个连续的异常。 在不可持续异常后继续执行的任何尝试都会导致 EXCEPTION_NONCONTINUABLE_EXCEPTION 异常。 |
    | EXCEPTION_SOFTWARE_ORIGINATE | 此标志保留供系统使用。                                       |

* `ExceptionRecord`：指向关联的`EXCEPTION_RECORD`结构的指针。

* `ExceptionAddress`：发生异常的地址。

* `NumberParameters`：与异常关联的参数数。

* `ExceptionInformation[EXCEPTION_MAXIMUM_PARAMETERS]`：描述异常的其他参数的数组。

  * `RaiseException`函数可以指定此参数数组。

  * | 异常代码                   | 含义                                                         |
    | :------------------------- | :----------------------------------------------------------- |
    | EXCEPTION_ACCESS_VIOLATION | 数组的第一个元素包含一个读写标志，该标志指示导致访问冲突的操作类型。 如果此值为零，则线程尝试读取不可访问的数据。 如果此值为 1，则线程尝试写入不可访问的地址。如果此值为 8，则线程导致用户模式数据执行防护 (DEP) 冲突。第二个数组元素指定不可访问数据的虚拟地址。 |
    | EXCEPTION_IN_PAGE_ERROR    | 数组的第一个元素包含一个读写标志，该标志指示导致访问冲突的操作类型。 如果此值为零，则线程尝试读取不可访问的数据。 如果此值为 1，则线程尝试写入不可访问的地址。如果此值为 8，则线程导致用户模式数据执行防护 (DEP) 冲突。第二个数组元素指定不可访问数据的虚拟地址。第三个数组元素指定导致异常的基础 NTSTATUS 代码。 |

### CONTEXT

包含特定于处理器的寄存器数据。 

```c++
typedef struct _CONTEXT {
    DWORD64 P1Home;
    DWORD64 P2Home;
    DWORD64 P3Home;
    DWORD64 P4Home;
    DWORD64 P5Home;
    DWORD64 P6Home;
    DWORD   ContextFlags;
    DWORD   MxCsr;
    WORD    SegCs;
    WORD    SegDs;
    WORD    SegEs;
    WORD    SegFs;
    WORD    SegGs;
    WORD    SegSs;
    DWORD   EFlags;
    DWORD64 Dr0;
    DWORD64 Dr1;
    DWORD64 Dr2;
    DWORD64 Dr3;
    DWORD64 Dr6;
    DWORD64 Dr7;
    DWORD64 Rax;
    DWORD64 Rcx;
    DWORD64 Rdx;
    DWORD64 Rbx;
    DWORD64 Rsp;
    DWORD64 Rbp;
    DWORD64 Rsi;
    DWORD64 Rdi;
    DWORD64 R8;
    DWORD64 R9;
    DWORD64 R10;
    DWORD64 R11;
    DWORD64 R12;
    DWORD64 R13;
    DWORD64 R14;
    DWORD64 R15;
    DWORD64 Rip;
    union {
        XMM_SAVE_AREA32 FltSave;
        NEON128         Q[16];
        ULONGLONG       D[32];
        struct {
            M128A Header[2];
            M128A Legacy[8];
            M128A Xmm0;
            M128A Xmm1;
            M128A Xmm2;
            M128A Xmm3;
            M128A Xmm4;
            M128A Xmm5;
            M128A Xmm6;
            M128A Xmm7;
            M128A Xmm8;
            M128A Xmm9;
            M128A Xmm10;
            M128A Xmm11;
            M128A Xmm12;
            M128A Xmm13;
            M128A Xmm14;
            M128A Xmm15;
        } DUMMYSTRUCTNAME;
        DWORD           S[32];
    } DUMMYUNIONNAME;
    M128A   VectorRegister[26];
    DWORD64 VectorControl;
    DWORD64 DebugControl;
    DWORD64 LastBranchToRip;
    DWORD64 LastBranchFromRip;
    DWORD64 LastExceptionToRip;
    DWORD64 LastExceptionFromRip;
} CONTEXT, *PCONTEXT;
```



## SEH异常处理

当运行发生异常，程序就会去`fs:[0]`里找到TEB（x64平台上是`gs:[0]`指向TEB），然后在TEB的偏移量为0的地方找到SEH的链表头，然后一个个遍历，直到找到对应的异常处理函数。