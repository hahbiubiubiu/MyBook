Learning from [angr - 0x401RevTrain-Tools](https://34r7hm4n.me/0x401RevTrain-Tools/angr)

# angr

## 基本用法

### 加载二进制文件

```python
proj = angr.Project(filename)
```

可通过 `proj` 查看文件的架构等信息。

### 符号执行状态——SimStae

```python
state = proj.factory.entry_state()
```

可通过 `state` 查看一些寄存器、内存等信息。

### 符号、具体值

在angr中，无论是具体值还是符号量都有相同的类型——`claripy.ast.bv.BV`。

```python
>>> claripy.BVV(666, 32)        # 创建一个32位的有具体值的BV
<BV32 0x29a>
>>> claripy.BVS('sym_var', 32)  # 创建一个32位的符号值BV
<BV32 sym_var_97_32>
```

### 符号执行引擎——Simulation Managers

```python
>>> simgr = proj.factory.simulation_manager(state)
<SimulationManager with 1 active>
```

`with 1 active` 表示当前有一条可以继续延伸的状态，也就是初始状态 `state`。

1. `simgr.step()` 往前执行一步。
2. `simgr.explore(find=addr)` 执行到目标地址。
3. `simgr.found` 保存了当前符号执行的所有状态。
   1. 可以通过 `simgr.found[0]` 获取当前的状态。
   2. `simgr.found[0].posix.dumps(0)`：
      1. `.posix`：提供对 POSIX 系统调用接口的模拟支持，允许你与文件描述符进行交互。
      2. `.dumps(0)`：方法用于获取与给定文件描述符关联的数据。
         1. 参数 `0` 对应标准输入。
         2. 该方法返回的是一个字符串，表示从标准输入读取的所有数据。

## 用法

### explore

#### explore：find（到达某地址）

让 angr 在 `strcmp` 返回时，添加约束 `eax == 0`，进行求解：

```python
proj = angr.Project('example-1')                
sym_flag = claripy.BVS('flag', 100 * 8)     # BV的大小得设大一点，不然跑不出来，原因未知
state = proj.factory.entry_state(stdin=sym_flag)
simgr = proj.factory.simgr(state)
# 0x40138D为call strcmp的下一条指令
simgr.explore(find=0x40138D)
solver = simgr.found[0].solver
solver.add(simgr.found[0].regs.eax == 0)
print(solver.eval(sym_flag, cast_to=bytes))
```

#### explore：avoid（避免某地址）

```python
proj = angr.Project('dist/01_angr_avoid')
state = proj.factory.entry_state()
simgr = proj.factory.simgr(state)
# 要到达0x80485E0，但是避免走过0x80485A8
simgr.explore(find=0x80485E0, avoid=0x80485A8)
print(simgr.found[0].posix.dumps(0))
```

#### explore：find和函数（利用函数的返回值作为条件）

```python
def is_successful(state):
    return b'Good Job.' in state.posix.dumps(1)

def should_avoid(state):
    return b'Try again.' in state.posix.dumps(1)

proj = angr.Project('dist/02_angr_find_condition')
state = proj.factory.entry_state()
simgr = proj.factory.simgr(state)
# 要标准输出中包含 Good Job
# 避免标准输出中包含 Try again
simgr.explore(find=is_successful, avoid=should_avoid)
print(simgr.found[0].posix.dumps(0))
```

### symbolic

#### 寄存器

```python
proj = angr.Project('../dist/03_angr_symbolic_registers')
state = proj.factory.blank_state(addr=0x8048980)
# 在0x8048980时，输入被放在了eax、ebx、edx中
password0 = claripy.BVS('password0', 32)
password1 = claripy.BVS('password1', 32)
password2 = claripy.BVS('password2', 32)
state.regs.eax = password0
state.regs.ebx = password1
state.regs.edx = password2
simgr = proj.factory.simgr(state)
simgr.explore(find=0x80489E6)
solver = simgr.found[0].solver
```

#### 栈空间（局部变量）

局部变量一般放在栈空间里。

根据栈的分布来设置 `esp`，然后在输入的变量的位置，push 符号化的变量。

```python
proj = angr.Project('../dist/04_angr_symbolic_stack')
state = proj.factory.blank_state(addr=0x8048694)
state.regs.ebp = state.regs.esp + 40
state.regs.esp = state.regs.ebp - 0xC + 4
password0 = claripy.BVS('password0', 32)
password1 = claripy.BVS('password1', 32)
state.stack_push(password0)
state.stack_push(password1)
state.regs.esp = state.regs.ebp - 40
simgr = proj.factory.simgr(state)
simgr.explore(find=0x80486E1)
solver = simgr.found[0].solver
```

#### 内存（全局变量）

在全局变量的地址进行符号化。

```python
proj = angr.Project('../dist/05_angr_symbolic_memory')
state = proj.factory.blank_state(addr=0x80485FE)
password0 = claripy.BVS('password0', 64)
password1 = claripy.BVS('password1', 64)
password2 = claripy.BVS('password2', 64)
password3 = claripy.BVS('password3', 64)
state.mem[0xA1BA1C0].uint64_t = password0
state.mem[0xA1BA1C0 + 8].uint64_t = password1
state.mem[0xA1BA1C0 + 16].uint64_t = password2
state.mem[0xA1BA1C0 + 24].uint64_t = password3
simgr = proj.factory.simgr(state)
simgr.explore(find=0x804866A)
solver = simgr.found[0].solver
```

#### 动态内存（malloc分配的内存）

由于地址不固定，可以在内存中选定一块区域作为输入的地址，作为 `malloc` 的返回值。

```python
proj = angr.Project('../dist/06_angr_symbolic_dynamic_memory')
state = proj.factory.blank_state(addr=0x8048696)
password0 = claripy.BVS('password0', 64)
password1 = claripy.BVS('password1', 64)
state.mem[0xABCC700].uint64_t = password0
state.mem[0xABCC700 + 8].uint64_t = password1
state.mem[0xABCC8A4].uint32_t = 0xABCC700
state.mem[0xABCC8AC].uint32_t = 0xABCC700 + 8
simgr = proj.factory.simgr(state)
simgr.explore(find=0x8048759)
solver = simgr.found[0].solver
```

#### 文件

对文件内容进行符号化。

```python
proj = angr.Project('../dist/07_angr_symbolic_file')
state = proj.factory.blank_state(addr=0x80488D3)
password0 = claripy.BVS('password0', 64)
# 模拟文件
sim_file = angr.SimFile(name='OJKSQYDP.txt', content=password0, size=0x40)
state.fs.insert('OJKSQYDP.txt', sim_file)
simgr = proj.factory.simgr(state)
simgr.explore(find=0x80489AD)
solver = simgr.found[0].solver
```

### constraints

对于会导致路径爆炸的指令，如果可以直接进行化简，则可以添加约束替代。

对于这样的检测，会导致 `2 ** len` 种状态：

```c
cnt = 0;
for (int i = 0; i < len; i++)
{
    if (input[i] == result[i])
        v3++;
}
return v3 == len;
```

可通过 `found.add_constraints(found.memory.load(buffer_addr, 16) == b'AUPDNNPROEZRJWKB')` 替代。

```python
proj = angr.Project('../dist/08_angr_constraints')
state = proj.factory.blank_state(addr=0x8048622)
password = claripy.BVS('password', 16 * 8)
buffer_addr = 0x804A050
state.memory.store(buffer_addr, password)
simgr = proj.factory.simgr(state)
simgr.explore(find=0x8048669)
found = simgr.found[0]
found.add_constraints(found.memory.load(buffer_addr, 16) == b'AUPDNNPROEZRJWKB')
```

### hook

#### hook 指令

替换 `check_equals` 函数：

```python
@proj.hook(addr=0x80486B3, length=5)  # call指令长度为5
def my_check_equals(state):
    buffer_addr = 0x804A054
    buffer = state.memory.load(buffer_addr, 16)
    state.regs.eax = claripy.If(buffer == b'XYMKBKUHNIQYNQXE', claripy.BVV(1, 32), claripy.BVV(0, 32))
```

以下写法等价：

```python
def my_check_equals(state):
    buffer_addr = 0x804A054
    buffer = state.memory.load(buffer_addr, 16)
    state.regs.eax = claripy.If(buffer == b'XYMKBKUHNIQYNQXE', claripy.BVV(1, 32), claripy.BVV(0, 32))

proj.hook(addr=0x80486B3, hook=my_check_equals, length=5)
```

#### SimProcedures

##### hook 函数

hook 之后 angr 在符号执行的过程中将不会调用原先的 `check_equals_ORSDDWXHZURJRBDH` 函数，而是 `MyCheckEquals.run`。

```python
class MyCheckEquals(angr.SimProcedure):
    def run(self, buffer_addr, length):
        buffer = self.state.memory.load(buffer_addr, length)
        return claripy.If(buffer == b'ORSDDWXHZURJRBDH', claripy.BVV(1, 32), claripy.BVV(0, 32))

proj = angr.Project('../dist/10_angr_simprocedures')
proj.hook_symbol(symbol_name='check_equals_ORSDDWXHZURJRBDH', simproc=MyCheckEquals())
```

##### 模拟系统函数的SimProcedures

angr 在 angr/procedures 中定义了很多模拟系统函数的 `SimProcedures`。

hook `scanf`：

```python
proj = angr.Project('../dist/11_angr_sim_scanf')
proj.hook_symbol("__isoc99_scanf", angr.SIM_PROCEDURES['libc']['scanf']())
```

### veritesting

> Enhancing Symbolic Execution with Veritesting
>
> - 结合动态与静态执行：Veritesting 从动态符号执行（DSE）开始，当遇到不包含系统调用、间接跳转或其他难以静态精确推理的语句时，切换到静态验证式方法（SSE）。这种切换能够在一定程度上缓解 DSE 中的路径爆炸问题和 SSE 中的求解器爆炸问题。
> - 处理复杂程序结构：对于包含循环和系统调用等复杂结构的程序，Veritesting 能够在动态执行过程中确定循环的具体迭代次数，将循环展开为有限的路径，然后使用 SSE 对这些路径进行总结和分析，最后再切换回 DSE 处理剩余难以静态分析的部分。

通过以下方式开启：

```python
simgr = proj.factory.simgr(state, veritesting=True)
```

Versitesting 通常与其他 exploration techniques 不兼容。

### library

对于动态库中的函数，可以通过 `call_state` 创建一个函数调用的初始状态。

```python
proj = angr.Project('../dist/lib14_angr_shared_library.so')
validate_addr = 0x4006D7
password = claripy.BVS('password', 8 * 8)
length = claripy.BVV(8, 32)
state = proj.factory.call_state(validate_addr, password, length)
simgr = proj.factory.simgr(state)
simgr.explore(find=0x400783)
found = simgr.found[0]
found.solver.add(found.regs.eax == 1)
print(found.solver.eval(password, cast_to=bytes))
```

### VEX IR

angr 的符号执行基于一种特定的中间代码——VEX。

大部分的VEX IR就是把一条汇编指令用多条VEX IR指令替代。

angr 符号执行中每次 step 的单位：

```python
import angr

proj = angr.Project('TestProgram')
state = proj.factory.entry_state()
simgr = proj.factory.simgr(state)
while len(simgr.active):
    print('--------------')
    for active in simgr.active:
        print(hex(active.addr))
        if b'Congratulations~' in active.posix.dumps(1):
            print(active.posix.dumps(0))
    simgr.step()
```

simgr的step函数是以一个irsb为单位进行符号执行的，也就是说每次step之后的状态，是在上一次state的基础上，符号执行一个irsb之后的结果。

当前要执行的 `irsb` 可以通过 `state.scratch.irsb` 获得。

### 获取CFG

方法一：获取函数的的CFG（以`jmp` 等指令和 `call` 指令分割）。

```python
proj = angr.Project(filename, load_options={'auto_load_libs': False})
cfg = proj.analyses.CFGFast()
func = cfg.kb.functions[start_addr]
basicblocks = list(func.blocks)
```

方法二：获取函数的的CFG（以`jmp` 等指令和 `call` 指令分割）。

```python
proj = angr.Project(filename, load_options={'auto_load_libs': False})
cfg = proj.analyses.CFGFast()
func = cfg.kb.functions[start_addr].transition_graph
basicblocks = list(func.nodes())
```

方法三：获取函数的的CFG（以`jmp` 等指令分割，并且会将 `jmp $+5` 与其下一个基本块视为一个基本块）。

```python
cfg = proj.analyses.CFGFast(
    normalize=True,
    force_complete_scan=False,
)
cfg = cfg.kb.functions[func_addr].transition_graph
cfg = to_supergraph(cfg)
```
