# Appcall

Appcall是一种机制，用于在**调试程序**的上下文中调用调试器会话下的函数。

Appcall机制高度依赖于被调用函数的类型信息。因此，在执行Appcall之前，必须有一个正确的函数原型。

Appcall的工作原理：

1. 首先劫持当前线程的堆栈。
   1. 如果想在不同的上下文中进行Appcall，请显式切换线程。
2. 推送参数。
3. 暂时将指令指针调整到被调用函数的开头。
4. 函数返回（或发生异常）后，将恢复原始堆栈、指令指针和其他寄存器，并将结果返回给调用者。

## 基本使用

**使用 Appcall 时，IDA 处于调试状态。**

Appcall的使用有 IDC 和 Python 两种方式，这里讲解 Python 方式。

依赖：（两个都是默认导入的）

```python
import idc # idc.get_name_ea(0, funcName) 获取函数地址，也可以直接指定
from idaapi import Appcall
```

IDA 已经有定义的函数，可直接使用：

1. `Appcall.printf(...)`
2. `Appcall['printf'](...)`

没有定义或重新定义的函数需要 `proto`。

### Appcall属性

1. `Appcall.UTF16(s)`：将字符串转化为 UTF16 的字节流 (`bytes`)
2. `Appcall.array(type_name)`：创建数组类型。
   1. `type_name` 指定数组元素的类型。
   2. `array.pack(L)`：将列表或者元组打包到 `byref` 缓冲区中。
   3. `array.unpack(buf, as_list=True)`：将数组解包存入 `buf` 对象中。
      1. `as_list` 如果为 `False` 则将数组作为元组解包。
3. `Appcall.buffer(str=None, size=0, fill='\x00')`：创建可变字符串数组使用。
   1. 返回值： `byref` 对象。
   2. `byref.value` 获取缓冲区内的字符串内容。
4. `Appcall.byref(val)`：创建不可变对象的引用。
   1. `byref.value` 获取对象的内容。
5. `Appcall.int64(val)`：创建`int64` 对象。
6. `Appcall.obj(**kwds)`：创建一个对象。
7. `Appcall.proto(name_or_ea, proto_or_tinfo, flags=None)`：将所需要的原型实例化为 `appcall` (`callable` 对象)。
   - `name_or_ea`：函数名字符串或者函数地址。
   - `proto_or_tinfo`：函数原型字符串或者函数类型的 `tinfo_t` 对象。
     - 可以使用 `get_tinfo()` 函数获取。
8. `Appcall.typeobj(typedecl_or_tinfo, ea=None)`：获取一个类型的 Appcall 对象。
   1. 有对象 `tp = Appcall.typedobj("struct abc_t {int a, b;};")`
   2. 存：
      1. 存在地址上：`tp.store(ea)`。
   3. 取：
      1. 从地址中取：`tp.retrieve(ea)`。
      2. 从字节数据中取：`tp.retrieve(b"\x01\x00\x00\x00\x02\x00\x00\x00")`。
9. `Appcall.unicode(s)`：将字符串转化为 Unicode 的字节流 (`bytes`)。
10. `Appcall.valueof(name, default=0)`：返回给定名称字符串 `name` 的数值。
11. `Appcall.Consts`：实例变量，使用 `Appcall.Consts.CONST_NAME` 来访问常量，`CONST_NAME` 因程序的设定变化。

### 调用函数

```
Appcall.proto(name, prototype)
Appcall.proto(ea, prototype)
```

#### 无参数、无返回值 函数

目标：

```c
void tellme() {
    printf("You got it!\n");
}
```

脚本：

```python
ea = idc.get_name_ea(0, "tellme")
tellme_func = Appcall.proto(ea, "void tellme();")
result = tellme_func() # void 返回 0
```

#### 参数为int、有返回值 函数

目标：

```c
int myadd(int a, int b) {
    return a + b;
}
```

脚本：

`int` 类型可直接传参，但 `int64` 类型需传参 `Appcall.int64(x)`。

```python
ea = idc.get_name_ea(0, "myadd")
myadd_func = Appcall.proto(ea, "int myadd(int a, int b);")
result = myadd_func(1, 2)
print(result)
```

#### 参数为引用 函数

目标：

```c
int changeIntByRef(int *a) {
    *a = 10;
    return *a;
}
```

脚本：

```python
ea = idc.get_name_ea(0, "changeIntByRef")
changeintbyref_func = Appcall.proto(ea, "int changeIntByRef(int *a);")
a = Appcall.byref(5)
r = changeintbyref_func(a)
print(a.value)
```

#### 参数为结构体 函数

目标：

```c
struct Student
{
    char name[20];
    int age;
    float score;
};

void modifyStudent(struct Student *stu)
{
    printf("Student: %s, %d, %f\n", stu->name, stu->age, stu->score);
    strcpy(stu->name, "Alice");
}
```

IDA 需要创建结构体：

```c
struct Student
{
    char name[20];
    int age;
    float score;
};
```

脚本：

```python
ea = idc.get_name_ea(0, "modifyStudent")
modifyStudent_func = Appcall.proto(ea, "void modifyStudent(struct Student *stu);")
# 方法1：
arg = {"name": "test", "age": 20, "score": 100.0}
# 方法2：感觉这个好一些🤔
arg = Appcall.obj(name="test", age=20, score=100.0)
modifyStudent_func(arg)
print(arg)
```

+ IDA会自动创建缺少的对象字段，并填充为零。
+ 对象始终通过引用传递（不需要使用&）。

##### idapython创建结构体脚本

> add_struc_member(sid, name, offset, flag, typeid, nbytes, target=-1, tdelta=0, reftype=2)
>     Add structure member
>
>     @param sid: structure type ID
>     @param name: name of the new member
>     @param offset: offset of the new member
>                    -1 means to add at the end of the structure
>     @param flag: type of the new member. Should be one of
>                  FF_BYTE..FF_PACKREAL (see above) combined with FF_DATA
>     @param typeid: if is_struct(flag) then typeid specifies the structure id for the member
>                    if is_off0(flag) then typeid specifies the offset base.
>                    if is_strlit(flag) then typeid specifies the string type (STRTYPE_...).
>                    if is_stroff(flag) then typeid specifies the structure id
>                    if is_enum(flag) then typeid specifies the enum id
>                    if is_custom(flags) then typeid specifies the dtid and fid: dtid|(fid<<16)
>                    Otherwise typeid should be -1.
>     @param nbytes: number of bytes in the new member
>     
>     @param target: target address of the offset expr. You may specify it as
>                    -1, ida will calculate it itself
>     @param tdelta: offset target delta. usually 0
>     @param reftype: see REF_... definitions
>     
>     @note: The remaining arguments are allowed only if is_off0(flag) and you want
>            to specify a complex offset expression
>     
>     @return: 0 - ok, otherwise error code (one of typeinf.TERR_*)

```python
sid = idc.add_struc(-1, "biu", 0)
# 创建 char arr[256];
idc.add_struc_member(sid, "arr1", -1, idc.FF_BYTE|idc.FF_DATA, None, 256)
# 创建 unsigned int brr[256];
idc.add_struc_member(sid, "arr2", -1, idc.FF_DWORD|idc.FF_DATA, -1, 256)
```

#### 参数寄存器 非标准函数

目标：

```c
// rax = rsi - rdi
int asm1(void)
{
    int result;
    __asm__ volatile (
        "movl %%esi, %%eax\n\t"
        "subl %%edi, %%eax"
        : "=a" (result)  // 输出操作数
        :                 // 输入操作数
        : "cc"            // 破坏的标志（条件码）
    );
    return result;
}
```

脚本：

```python
ea = idc.get_name_ea(0, "asm1")
asm1_func = Appcall.proto(ea, "int __usercall asm1@<rax>(int a@<rsi>, int b@<rdi>);")
r = asm1_func(4, 2)
print(r)
```

#### 参数为不透明类型 函数

不透明类型，如 `FILE、HWND、HANDLE、HINSTANCE、HKEY` 等，本身并不打算用作结构，而是像指针一样，可以使用 `__at__` 来检索给定IDC对象的C指针。

```python
fp = Appcall.fopen("./biu.txt", "w")
Appcall.fwrite("Hello, World!\n", 1, 13, fp.__at__)
Appcall.fclose(fp.__at__)
```



#### 参数为数组 函数

目标：

```c
int arraysum(int *arr, int len) {
    printf("Executing arraysum((%d, %d, ...), %d)\n", arr[0], arr[1], len);
    int sum = 0;
    for (int i = 0; i < len; i++) {
        sum += arr[i];
    }
    return sum;
}
int chararraysum(char *arr, int len) {
    printf("Executing chararraysum((%c, %c, ...), %d)\n", arr[0], arr[1], len);
    int sum = 0;
    for (int i = 0; i < len; i++) {
        sum += arr[i];
    }
    return sum;
}
```

脚本：

```python
# int数组
ea = idc.get_name_ea(0, "arraysum")
arraysum_func = Appcall.proto(ea, "int arraysum(int *arr, int arrlen);")
arr = Appcall.array("int").pack([1, 2, 3, 4, 5])
result = arraysum_func(arr, 5)
print(result)
# char数组
ea = idc.get_name_ea(0, "chararraysum")
chararraysum_func = Appcall.proto(ea, "int chararraysum(char *arr, int arrlen);")
arr = Appcall.array("char").pack([ord(i) for i in "abcde"])
result = chararraysum_func(arr, 5)
print(result)
```

#### 修改char数组 函数（其他数组同理）

目标：

```c
void stringcpy(char *s1, char *s2) {   
    printf("Executing stringcpy(%s, %s)\n", s1, s2);
    strcpy(s1, s2);
}

void operatechararray(char *arr, int len) {
    printf("Executing operatechararray((%c, %c, ...), %d)\n", arr[0], arr[1], len);
    for (int i = 0; i < len; i++) {
        arr[i] = arr[i] + 1;
    }
    printf("End of operatechararray -> arr: (%c, %c, ...)\n", arr[0], arr[1]);
}
```

脚本：

+ `Appcall.buffer`
+ `Appcall.array(type).pack([...])`

```python
ea = idc.get_name_ea(0, "stringcpy")
stringcpy_func = Appcall.proto(ea, "void stringcpy(char *dst, char *src);")
dst = Appcall.buffer("", 256)
src = Appcall.array("char").pack([ord(i) for i in "hello"])
stringcpy_func(dst, src)
print(dst.value)

ea = idc.get_name_ea(0, "operatechararray")
operatechararray_func = Appcall.proto(ea, "void operatechararray(char *arr, int arrlen);")
arr = Appcall.array("char").pack([ord(i) for i in "abcde"])
operatechararray_func(arr, 5)
print(arr.value)
```

**注意**：如果给 `char` 数组元素赋值超过 `127`，则使用 `arr.value` 获取改变的值时会报错：

```
AttributeError: 'PyIdc_cvt_refclass__' object has no attribute '__idc_cvt_value__'
```

正常赋值时，`PyIdc_cvt_refclass__`具有属性`__idc_cvt_value__`。

##### 解决思路——无奈之举😭

以下为解决不了上述报错的无奈之举😭

###### 使用IDC

无法解决数组为 `int` 类型的情况。

```c
static main() {
    msg("Start\n");
    auto s = strfill('\x00', 256);
    auto l = 256;
    initIntArray(&s, l);
    auto i;
    for (i = 0; i < l; i++) {
        msg("%d, ", c);
    }
    msg("\nEnd\n");
}
```

###### 使用已知地址

`int` 数组同理。

以上问题可通过给出一个可写空间的地址作为数组地址，函数执行后，读取该地址的数据。

```python
addr = 0x...
ea = idc.get_name_ea(0, "operatechararray")
operatechararray_func = Appcall.proto(ea, "void operatechararray(char *arr, int arrlen);")
l = len(...)
operatechararray_func(addr, l)
content = [idc.get_bytes(addr+i) for i in range(l)]
```

###### 传入结构（感觉我是~~天才~~，哈哈 😀😀）

把 `void initIntArray(int *arr, int len);` 视为：

```python
# ida创建结构体
struct biu
{
  int arr[256];
};
void initIntArray(struct biu *arr, int len);
```

脚本：

```python
ea = idc.get_name_ea(0, "initIntArray")
initchararray_func = Appcall.proto(ea, "void initIntArray(struct biu *arr, int len);")
length = 256
# 用另一种结构体创建方法 好像有时会崩溃
arg = Appcall.obj(arr=([0] * length))
initchararray_func(arg, length)
# 结果地址为 arg["__at__"]
content = [
    int.from_bytes(
        idaapi.get_bytes(arg["__at__"] + 4 * i, 4), 
        byteorder="little"
    ) for i in range(length)
]
print(content)
```

### 调试指定函数

`Manual Appcall` 机制可用于保存当前执行上下文，在另一个上下文中执行另一个函数，然后弹出上一个上下文并从该点继续调试。

`Manual Appcall` 机制适用于在跟踪一个函数时，想调试另一个函数并从原来的位置恢复。

方法：

```python
biu = Appcall.biu # 想要调试的函数
# 设置模式为 APPCALL_MANUAL
# 1、设置全局模式
Appcall.set_appcall_options(Appcall.APPCALL_MANUAL)
# 2、单独设置模式
biu.options = Appcall.APPCALL_MANUAL
biu() # 调用
# 执行完后IDA会跳到biu函数，开始调试
# 调试完后，返回原来的上下文
Appcall.cleanup_appcall()
```

### Appcall相关函数

1. `get_tinfo(ea)`：检索与给定地址关联的类型信息字符串。
2. `parse_decl(string)`：从类型字符串构造类型信息字符串。
   1. `parse_decl("struct abc_t { int a, b;};", 0)`

# 实践

## 调用RC4解密

目标：

```c
#include <stdio.h>

void rc4_init(unsigned char *s, unsigned char *key, int keylen)
{
    int i, j = 0, k;
    unsigned char temp;
    for (i = 0; i < 256; i++)
    {
        s[i] = i;
    }
    for (i = 0; i < 256; i++)
    {
        j = (j + s[i] + key[i % keylen]) % 256;
        temp = s[i];
        s[i] = s[j];
        s[j] = temp;
    }
}

void rc4_crypt(unsigned char *s, unsigned char *data, int datalen)
{
    int i = 0, j = 0, k, t;
    unsigned char temp;
    for (k = 0; k < datalen; k++)
    {
        i = (i + 1) % 256;
        j = (j + s[i]) % 256;
        temp = s[i];
        s[i] = s[j];
        s[j] = temp;
        t = (s[i] + s[j]) % 256;
        data[k] ^= s[t];
    }
}

int main()
{
    unsigned char key[] = "mysecretkey";
    unsigned char encrypted_flag[11] = {0x8c, 0xbf, 0x19, 0xdf, 0xbb, 0x3d, 0x5b, 0xe3, 0xb4, 0x70};
    unsigned char s[256];
    rc4_init(s, key, strlen((char *)key));
    rc4_crypt(s, encrypted_flag, 10);
    printf("secret: %s\n", encrypted_flag);
    return 0;
}
```

Python 方法：

```python
c = [0x8c, 0xbf, 0x19, 0xdf, 0xbb, 0x3d, 0x5b, 0xe3, 0xb4, 0x70]
ea = idc.get_name_ea(0, "rc4_init")
rc4_init_func = Appcall.proto(
    ea, 
    "void rc4_init(struct biu *arr, unsigned char *key, int len);"
)
length = 256
key = "mysecretkey"
# arg1 创建方法1
arg1 = Appcall.obj(arr=b"\x00" * length)
# arg1 创建方法2
arg1 = Appcall.obj(arr=[0] * length)

arg2 = Appcall.buffer(key, len(key));
arg3 = len(key)
rc4_init_func(arg1, arg2, arg3)
s = [int.from_bytes(
    idaapi.get_bytes(arg1["__at__"] + i, 1), byteorder="little"
) for i in range(length)]
ea = idc.get_name_ea(0, "rc4_crypt")
rc4_crypt_func = Appcall.proto(
    ea, 
    "void rc4_crypt(unsigned char *s, unsigned char *data, int len);"
)
arg1 = Appcall.array("unsigned char").pack(s)
arg2 = Appcall.array("unsigned char").pack(c)
arg3 = len(c)
rc4_crypt_func(arg1, arg2, arg3)
# 解密后字符都在128以内，可以直接获取
print(arg2.value)
```

IDC 方法：

```c
static main() {
    msg("Start\n");
    auto s = strfill('\x31', 256);
    auto k = "mysecretkey";
    auto l = 11;
    dbg_appcall(
        LocByName("rc4_init"),
        "void rc4_init(unsigned char *s, unsigned char *key, int len);",
        &s, &k, l
    );
    
    auto i;
    # for (i = 0; i < 256; i++) {
    #     Message("%d, ", ord(s[i]) & 0xff);
    # }
    auto c = "\x8c\xbf\x19\xdf\xbb\x3d\x5b\xe3\xb4\x70\x00";
    dbg_appcall(
        LocByName("rc4_crypt"),
        "void rc4_init(unsigned char *s, unsigned char *c, int len);",
        &s, &c, 10
    );
    msg(c);
    msg("\nEnd\n");
}
```

