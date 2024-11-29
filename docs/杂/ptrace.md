## 函数定义

`long ptrace(enum __ptrace_request request, pid_t pid, void *addr, void *data);`

1. enum __ptrace_request request：指示了ptrace要执行的命令

   1. ```C
      enum __ptrace_request
      {
      	PTRACE_TRACEME = 0,		//被调试进程调用
      	PTRACE_PEEKDATA = 2,	//查看内存
        	PTRACE_PEEKUSER = 3,	//查看struct user 结构体的值
        	PTRACE_POKEDATA = 5,	//修改内存
        	PTRACE_POKEUSER = 6,	//修改struct user 结构体的值
        	PTRACE_CONT = 7,		//让被调试进程继续
        	PTRACE_SINGLESTEP = 9,	//让被调试进程执行一条汇编指令
        	PTRACE_GETREGS = 12,	//获取一组寄存器(struct user_regs_struct)
        	PTRACE_SETREGS = 13,	//修改一组寄存器(struct user_regs_struct)
        	PTRACE_ATTACH = 16,		//附加到一个进程
        	PTRACE_DETACH = 17,		//解除附加的进程
        	PTRACE_SYSCALL = 24,	//让被调试进程在系统调用前和系统调用后暂停
      };
      ```

2. pid_t pid: 指示ptrace要跟踪的进程

3. void *addr: 指示要监控的内存地址

4. void *data: 存放读取出的或者要写入的数据。

## reqeust

### PTRACE_SYSCALL

让被调试进程在系统**调用前**和系统**调用后**暂停。

因此，当产生系统调用时，会有两次暂停。

### PTRACE_GETREGS

获取trace进程的寄存器数据。

`ptrace(PTRACE_GETREGS, child_pid, 0, struct user_regs_struct regs)`

寄存器数据放在了`regs`中

```C
struct user_regs_struct
{
  __extension__ unsigned long long int r15;
  __extension__ unsigned long long int r14;
  __extension__ unsigned long long int r13;
  __extension__ unsigned long long int r12;
  __extension__ unsigned long long int rbp;
  __extension__ unsigned long long int rbx;
  __extension__ unsigned long long int r11;
  __extension__ unsigned long long int r10;
  __extension__ unsigned long long int r9;
  __extension__ unsigned long long int r8;
  __extension__ unsigned long long int rax;
  __extension__ unsigned long long int rcx;
  __extension__ unsigned long long int rdx;
  __extension__ unsigned long long int rsi;
  __extension__ unsigned long long int rdi;
  __extension__ unsigned long long int orig_rax;
  __extension__ unsigned long long int rip;
  __extension__ unsigned long long int cs;
  __extension__ unsigned long long int eflags;
  __extension__ unsigned long long int rsp;
  __extension__ unsigned long long int ss;
  __extension__ unsigned long long int fs_base;
  __extension__ unsigned long long int gs_base;
  __extension__ unsigned long long int ds;
  __extension__ unsigned long long int es;
  __extension__ unsigned long long int fs;
  __extension__ unsigned long long int gs;
};
```

### PTRACE_PEEKUSER

查看用户区域数据（寄存器数据）

`ptrace(PTRACE_PEEKUSER, child_pid, offset, 0)`

`offset`即为目标数据在`struct user_regs_struct`的偏移

例如：`rax`的偏移为`120`

### 用法

#### SINGLESETP、PEEKUSER、PEEKDATA判断进程将要执行的指令

```C
long rip = ptrace(PTRACE_PEEKUSER, child, 128LL, 0LL);
long instruction = ptrace(PTRACE_PEEKDATA, child, rip, 0LL);
// 判断是否执行到如下指令(**)
// .text:0000000000001292 89 C2             mov     edx, eax            ** 
// .text:0000000000001294 8B 45 A4          mov     eax, [rbp+var_5C]   ** 将index放入rax
if (
    (rip & 0xFFF) == 0x292 && 
    (instruction & 0xFFFFFFFFFFLL) == 0xA4458BC289LL
)
```

### SYSCALL、PEEKUSER判断执行的系统调用

```C
long int orig_rax = ptrace(PTRACE_PEEKUSER, child, 120, 0);  // orig_rax 保存了 系统调用号
// 还可以通过GETREGS获取寄存器数据，即可获得系统调用的参数以及返回值
```

