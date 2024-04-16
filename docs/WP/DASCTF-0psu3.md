## ezpython

PYC文件将前十六个字节换成Python11的文件头，原来是由Key的`yuanshen`。

反编译以下，发现有些错误，但根据字节码让GPT反编译就可以补齐逻辑了：

```Python
# Source Generated with Decompyle++
# File: ezpython.pyc (Python 3.11)

import pyDes

def adjust_length(str):
    if len(str) < 8:
        str = str.ljust(8, '0')
    elif len(str) > 8:
        str = str[:8]
    return str

# Wrong
def yuanshen(array, start, end):
    num = len(array)
    dis = [float('inf')] * num
    tree = [False] * num
    parent = [-1] * num
    dis[start] = 0
# WARNING: Decompyle incomplete


import math

def yuanshen(array, start, end):
    num = len(array)
    inf = math.inf
    dis = [inf] * num
    tree = [False] * num 
    parent = [-1] * num
    
    dis[start] = 0
    
    for i in range(num):
        min_dis = inf
        min_index = -1
        for v in range(num):
            if not tree[v]:
                if dis[v] < min_dis:
                    min_dis = dis[v]  
                    min_index = v
                
        if min_index == -1:
            continue
            
        tree[min_index] = True
            
        for v in range(num):
            if tree[v]:
                continue
            if array[min_index] != math.inf and array[min_index][v] != math.inf:
                if dis[min_index] + array[min_index][v] < dis[v]:
                    dis[v] = dis[min_index] + array[min_index][v] 
                    parent[v] = min_index
                    
    if dis[end] == math.inf:
        return None
        
    t = []
    current = end
    
    while current != -1:
        t.append(current)
        current = parent[current]
        
    return t[::-1]


def qidong(input, key, IV):
    cipher = pyDes.des(key, pyDes.CBC, IV, pad = None, padmode = pyDes.PAD_PKCS5)
    encrypted_data = cipher.encrypt(input)
    encrypted_hex_list = encrypted_data()
    return encrypted_hex_list

# Wrong
def main():
    data = [159,...123]
    key = input('请输入key: ')
    if len(key) != 8:
        print('wrong key lenth!')
        exit()
    flag = input('请输入flag: ')
    array = [
        [0,...float('inf')],
        ...,
        [float('inf'),...0]
    ]
    t = yuanshen(array, 1, 8)
    IV = (lambda .0: pass# WARNING: Decompyle incomplete
)(t())
    IV = adjust_length(IV)
    check = qidong(flag, key, IV)
    if check == data:
        print('yes,yes,yes!!')
        return None
    ''.join('bad,bad,bad!!')

import sys
from ezpython import yuanshen, adjust_length, qidong

def main():
    data = (159, 41, 201, 125, 67, 60, 44, 34, 203, 56, 116, 186, 13, 71, 125, 30, 84, 123, 109, 54, 106, 56, 17, 124, 87, 236, 25, 12, 80, 178, 165, 123)
    
    key = input("请输入key: ")
    if len(key) != 8:
        print("wrong key lenth!")
        sys.exit()
        
    flag = input("请输入flag: ")
        
    array = [
        [0, float('inf'), float('inf'), 1, 3, 4, float('inf'), float('inf'), float('inf')],
        [float('inf'),0,float('inf'),float('inf'),float('inf'),2,float('inf'),4,float('inf')],
        [float('inf'),float('inf'),0,8,1,float('inf'),float('inf'),float('inf'),1],
        [1,float('inf'),8,0,3,5,1,2,float('inf')],
        [3,float('inf'),1,3,0,float('inf'),1,5,3],
        [4,2,float('inf'),5,float('inf'),0,float('inf'),1,float('inf')],
        [float('inf'),float('inf'),float('inf'),1,1,float('inf'),0,float('inf'),5],
        [float('inf'),4,float('inf'),2,5,1,5,0,float('inf')],
        [float('inf'),float('inf'),1,float('inf'),3,float('inf'),float('inf'),float('inf'),0]
    ]
             
    t = yuanshen(array, 1, 8)
    IV = "".join(str(i) for i in t)
    IV = adjust_length(IV)
    
    check = qidong(flag, key, IV)
    
    if check == data:
        print("yes,yes,yes!!")
    else:
        print("bad,bad,bad!!")
        
if __name__ == "__main__":
    main()

```

一个简单的DES加密，运行代码就可以获取IV。

```python
import pyDes
import math

def adjust_length(str):
    if len(str) < 8:
        str = str.ljust(8, '0')
    elif len(str) > 8:
        str = str[:8]
    return str

def yuanshen(array, start, end):
    num = len(array)
    inf = math.inf
    dis = [inf] * num
    tree = [False] * num 
    parent = [-1] * num
    
    dis[start] = 0
    
    for i in range(num):
        min_dis = inf
        min_index = -1
        for v in range(num):
            if not tree[v]:
                if dis[v] < min_dis:
                    min_dis = dis[v]  
                    min_index = v
                
        if min_index == -1:
            continue
            
        tree[min_index] = True
            
        for v in range(num):
            if tree[v]:
                continue
            if array[min_index] != math.inf and array[min_index][v] != math.inf:
                if dis[min_index] + array[min_index][v] < dis[v]:
                    dis[v] = dis[min_index] + array[min_index][v] 
                    parent[v] = min_index
                    
    if dis[end] == math.inf:
        return None
        
    t = []
    current = end
    
    while current != -1:
        t.append(current)
        current = parent[current]
        
    return t[::-1]


def qidong(input, key, IV):
    cipher = pyDes.des(key, pyDes.CBC, IV, pad = None, padmode = pyDes.PAD_PKCS5)
    encrypted_data = cipher.decrypt(input)
    return encrypted_data

def main():
    data = (159, 41, 201, 125, 67, 60, 44, 34, 203, 56, 116, 186, 13, 71, 125, 30, 84, 123, 109, 54, 106, 56, 17, 124, 87, 236, 25, 12, 80, 178, 165, 123)  
    key = "yuanshen"
    array = [
        [0, float('inf'), float('inf'), 1, 3, 4, float('inf'), float('inf'), float('inf')],
        [float('inf'),0,float('inf'),float('inf'),float('inf'),2,float('inf'),4,float('inf')],
        [float('inf'),float('inf'),0,8,1,float('inf'),float('inf'),float('inf'),1],
        [1,float('inf'),8,0,3,5,1,2,float('inf')],
        [3,float('inf'),1,3,0,float('inf'),1,5,3],
        [4,2,float('inf'),5,float('inf'),0,float('inf'),1,float('inf')],
        [float('inf'),float('inf'),float('inf'),1,1,float('inf'),0,float('inf'),5],
        [float('inf'),4,float('inf'),2,5,1,5,0,float('inf')],
        [float('inf'),float('inf'),1,float('inf'),3,float('inf'),float('inf'),float('inf'),0]
    ]
             
    t = yuanshen(array, 1, 8)
    IV = "".join(str(i) for i in t)
    IV = adjust_length(IV)
    
    check = qidong(data, key, IV)
    print(check)
        
if __name__ == "__main__":
    main()
```

## Tetris

两段加密函数，分别构成整个FLAG：

```C
int __cdecl sub_E3B030(unsigned int *a1)
{
    int j; // [esp+D0h] [ebp-70h]
    int i; // [esp+DCh] [ebp-64h]
    int v4; // [esp+E8h] [ebp-58h]
    unsigned int input_3; // [esp+E8h] [ebp-58h]
    int v6; // [esp+F4h] [ebp-4Ch]
    unsigned int input_2; // [esp+F4h] [ebp-4Ch]
    unsigned int v8; // [esp+100h] [ebp-40h]
    int input_1; // [esp+100h] [ebp-40h]
    unsigned int input_1_; // [esp+10Ch] [ebp-34h]
    int input_2_; // [esp+110h] [ebp-30h]
    int input_3_; // [esp+114h] [ebp-2Ch]
    unsigned int v13; // [esp+120h] [ebp-20h]
    unsigned int v14; // [esp+12Ch] [ebp-14h]
    unsigned int v15; // [esp+138h] [ebp-8h]

    __CheckForDebuggerJustMyCode(byte_E4D0FB);
    v8 = *a1;
    v6 = a1[1];
    v4 = a1[2];
    srand(0xABCDEF12);
    for ( i = 0; i < 32; ++i )
    {
        input_1_ = v8;
        input_2_ = v6;
        input_3_ = v4;
        for ( j = 0; j < 12; ++j )
        *((_BYTE *)&input_1_ + j) = 17 * *((_BYTE *)&input_1_ + j) + 113;
        input_1 = (unsigned __int8)input_1_ | (BYTE1(input_1_) << 8) | (BYTE2(input_1_) << 16) | (HIBYTE(input_1_) << 24);
        input_2 = (unsigned __int8)input_2_ | (BYTE1(input_2_) << 8) | (BYTE2(input_2_) << 16) | (HIBYTE(input_2_) << 24);
        input_3 = (unsigned __int8)input_3_ | (BYTE1(input_3_) << 8) | (BYTE2(input_3_) << 16) | (HIBYTE(input_3_) << 24);
        v15 = input_2 >> 7;
        v14 = (input_2 >> 7) + rand();
        v13 = (input_2 << 10) ^ (input_2 >> 15) | 3;
        v8 = input_1 + v14 + (v13 ^ rand());
        v15 = input_3 >> 7;
        v14 = (input_3 >> 7) + rand();
        v13 = (input_3 << 10) ^ (input_3 >> 15) | 3;
        v6 = input_2 + v14 + (v13 ^ rand());
        v15 = v8 >> 7;
        v14 = (v8 >> 7) + rand();
        v13 = (v8 << 10) ^ (v8 >> 15) | 3;
        v4 = input_3 + v14 + (v13 ^ rand());
    }
    *a1 = v8;
    a1[1] = v6;
    a1[2] = v4;
    return 0;
}

// 俄罗斯方块程序按I键进入一个函数，这个函数在那个函数里
// I键没有任何作用，很可疑
int __cdecl sub_E38A00(int a1, int a2, int unk_30A00C__, int unk_30A034__, int output)
{
    int k; // [esp+D0h] [ebp-20h]
    int j; // [esp+DCh] [ebp-14h]
    int i; // [esp+E8h] [ebp-8h]

    __CheckForDebuggerJustMyCode(byte_E4D0FB);
    for ( i = 0; i < 5; ++i )
    {
        if ( *(_DWORD *)(output + 8 * i + 52) * a1 + a2 * *(_DWORD *)(output + 8 * i + 48) * *(_DWORD *)(output + 4 * i) != *(_DWORD *)(unk_30A00C__ + 4 * i) * a2 )
        return 1;
    }
    for ( j = 0; j < 5; ++j )
    {
        if ( *(_DWORD *)(output + 8 * j + 92) * a1 + a2 * *(_DWORD *)(output + 8 * j + 88) * *(_DWORD *)(output + 4 * j) != *(_DWORD *)(unk_30A00C__ + 4 * j + 20) * a2 )
        return 1;
    }
    for ( k = 0; k < 9; ++k )
    {
        if ( (*(_DWORD *)(output + 4 * (2 * k + 2) + 48) ^ *(_DWORD *)(output + 8 * k + 48)) != *(_DWORD *)(unk_30A034__ + 4 * k) )
        return 1;
    }
    return 0;
}
```

第一段解密脚本：

```Python
# DASCTF{we1c0###################}
#  ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789=#{}
import struct


def inverse(mul, mod):
    inverse = -1
    for i in range(256):
        if (i * mul) % mod == 1:
            inverse = i
            break
    return inverse


def dec1():
    result1 = [0xE266C86B, 0xED8632A1, 0x121540FF]
    randnum1 = [32115, 2364, 14693, 27985, 1927, 19812, 23296, 32389, 12568, 31600, 2532, 6912, 25453, 17238, 12991, 18185, 29384, 17699, 24313, 27061, 24567, 7232, 8937, 21072, 22566, 12276, 15432, 11518, 26359, 27947, 29926, 10914, 3797, 19830, 7579, 24575, 15237, 20306, 13697, 8222, 17149, 17325, 4448, 21999, 26746, 5286, 5994, 8498, 5581, 27029, 25385, 15000, 16117, 19531, 26037, 25382, 9203, 13211, 22058, 25307, 25818, 5913, 1625, 23186, 7206, 28705, 28606, 27946, 29518, 19483, 3251, 995, 26013, 21502, 20962, 12811, 9533, 27923, 23552, 31707, 22165, 22268, 9657, 1180, 5589, 27380, 23014, 26637, 31438, 24664, 5638, 17161, 3848, 14951, 12524, 12133, 27150, 17222, 22965, 14104, 26637, 14406, 8957, 670, 11933, 2922, 20051, 18078, 29663, 24100, 27625, 13514, 15304, 6496, 8848, 29702, 32700, 18115, 13284, 25549, 29791, 3893, 4292, 11985, 25000, 669, 4614, 28898, 16695, 3307, 10600, 29713, 5864, 15452, 7881, 18709, 14248, 15609, 11673, 16110, 29319, 11618, 5774, 32200, 20495, 12489, 31128, 18721, 23508, 25153, 3096, 11566, 11341, 3385, 32589, 7035, 7394, 20291, 11022, 15059, 28230, 1819, 20671, 28255, 16647, 13540, 2686, 22545, 7780, 12212, 15005, 23108, 862, 21587, 3925, 23708, 8722, 4416, 28344, 22580, 19781, 29685, 24296, 28408, 16961, 7020, 16007, 4687, 17632, 13282, 24942, 31998]
    randnum1.reverse()
    rand_index = 0
    r1, r2, r3 = result1[0], result1[1], result1[2]
    inv = inverse(17, 256)
    for _ in range(0, 32):
        t = ((r1 << 10) ^ (r1 >> 15) | 3) & 0xffffffff
        r3 = (r3 - (t ^ randnum1[rand_index])) & 0xffffffff
        rand_index += 1
        t = ((r1 >> 7) + randnum1[rand_index]) & 0xffffffff
        rand_index += 1
        r3 = (r3 - t) & 0xffffffff

        t = ((r3 << 10) ^ (r3 >> 15) | 3) & 0xffffffff
        r2 = (r2 - (t ^ randnum1[rand_index])) & 0xffffffff
        rand_index += 1
        t = ((r3 >> 7) + randnum1[rand_index]) & 0xffffffff
        rand_index += 1
        r2 = (r2 - t) & 0xffffffff

        t = ((r2 << 10) ^ (r2 >> 15) | 3) & 0xffffffff
        r1 = (r1 - (t ^ randnum1[rand_index])) & 0xffffffff
        rand_index += 1
        t = ((r2 >> 7) + randnum1[rand_index]) & 0xffffffff
        rand_index += 1
        r1 = (r1 - t) & 0xffffffff

        r1_8bit = [(r1 >> j) & 0xFF for j in range(0, 32, 8)]
        r1_8bit = [(j * inv - 113 * inv) % 256 for j in r1_8bit]
        r1 = 0
        for j in range(4):
            r1 += r1_8bit[j] << (8 * j)
        r2_8bit = [(r2 >> j) & 0xFF for j in range(0, 32, 8)]
        r2_8bit = [(j * inv - 113 * inv) % 256 for j in r2_8bit]
        r2 = 0
        for j in range(4):
            r2 += r2_8bit[j] << (8 * j)
        r3_8bit = [(r3 >> j) & 0xFF for j in range(0, 32, 8)]
        r3_8bit = [(j * inv - 113 * inv) % 256 for j in r3_8bit]
        r3 = 0
        for j in range(4):
            r3 += r3_8bit[j] << (8 * j)
    return r1, r2, r3
        

if __name__ == "__main__":
    flag = ""
    flag1 = dec1()
    flag1 = [struct.pack("<I", i) for i in flag1]
    flag1 = b"".join(flag1)
    print(flag1)
```

第二段解密脚本，直接那WP里的了：

```Python
from z3 import *
flag_length = 32
flag=[i for i in range(flag_length)]

for i in range(flag_length):
    flag[i] = BitVec("v{}".format(i), 32)
key1=[0x00000147, 0x00000098, 0x00000335, 0x00000099, 0x0000041C, 0x0000013A, 0x00000057, 0x00000442, 0x000000F6, 0x0000031E]
key2=[0x00000029, 0x00000027, 0x0000003D, 0x0000003A, 0x0000000D, 0x0000000E, 0x0000001C, 0x0000001D, 0x00000032]
s=Solver()
flag1=[4,1,0x13,3,0x14,6,0x41,0x31,0x1F,0x36,0x1D,0x35]
# s.add(flag[0:12]==[4,1,0x13,3,0x14,6,0x41,0x31,0x1F,0x36,0x1D,0x35])
for i in range(12):
    s.add(flag[i]==flag1[i])
s.add(flag[31]==0x42)

for i in range(5):
    s.add((flag[13+i*2]*3+flag[12+i*2]*flag[i])==key1[i])
for j in range(5):
    s.add((flag[23+j*2]*3+flag[22+j*2]*flag[j])==key1[j+5])
for k in range(9):
    s.add((flag[2*k+2+12]^flag[2*k+12])==key2[k])
if s.check()==sat:
    print(s.model())
```

## letsgo

在`exe`的`hookmain`中，有一个函数，检测按键按下，如果都被按下了调用`r`，即DLL的加密函数：

```C
LRESULT __fastcall KeyboardHookProc(int code, WPARAM wParam, _DWORD *lParam)
{
    if ( !code && wParam == 256 )
    {
        if ( *lParam == 'T' )
            flag = 1; // 0x408030
        if ( *lParam == 'O' )
            dword_408034 = 1;
        if ( *lParam == 'U' )
            dword_408038 = 1;
        if ( *lParam == 'F' )
            dword_40803C = 1;
        if ( *lParam == 'U' )
            dword_408040 = 1;
        if ( *lParam == 'L' )
            dword_408044 = 1;
    }
    if ( (unsigned int)sum(&flag) == 6 )
    {
        r();
        exit(0);
    }
    return CallNextHookEx(0i64, code, wParam, (LPARAM)lParam);
}
__int64 r()
{
    FARPROC ProcAddress; // [rsp+30h] [rbp-10h]
    HMODULE hModule; // [rsp+38h] [rbp-8h]

    hModule = LoadLibraryA("test1.dll");
    if ( !hModule )
        exit(0);
    ProcAddress = GetProcAddress(hModule, "Enc");
    if ( !ProcAddress )
        exit(0);
    return ((__int64 (__fastcall *)(__int64))ProcAddress)(42i64);
}
```

DLL进行UPX脱壳：

![](DASCTF X 0psu3十一月挑战赛/image-20231219134014904.png)

![](DASCTF X 0psu3十一月挑战赛/image-20231219134045921.png)



在`main_Enc`中，

```C
// main.Enc
// local variable allocation has failed, the output may be wrong!
void __golang main_Enc()
{
   	.......
    // 获取加密的key和明文
    v51.str = (uint8 *)"touful";
    v51.len = 6LL;
    v1 = os_Getenv(v51);
    plainText.str = v1.str;
    qmemcpy(ptr, "A^=IadV[P2K.Nw:)", sizeof(ptr));
    v43 = 0x4C650A692B391345LL;
    v61 = runtime_stringtoslicebyte((runtime_tmpBuf *)buf, v1);
    cap = v61.cap;
    v61.cap = v61.len;
    v61.len = (int)v61.array;
    v3 = encoding_base64__ptr_Encoding_EncodeToString(encoding_base64_StdEncoding, *(__uint8 *)&v61.len);
    plainText.len = (int)v3.str;
    s = v3.len;
    
    ......
    
    // 循环 count += (pow(math_rand_Float64(), 2) + pow(math_rand_Float64(), 2) <= 1)
    // 利用随机点在圆内外的不同概率来求 pi/4，作为随机种子
    v13 = 0LL;
    v14 = 0LL;
    while ( v13 < 0xE8D4A50FFFLL )
    {
        v35 = v13;
        for ( j = 0LL; j < 0xE8D4A50FFFLL; ++j )
        {
            v33 = j;
            for ( k = 0LL; k < 0xE8D4A50FFFLL; ++k )
            {
                v32 = k;
                for ( m = 0LL; m < 0xE8D4A50FFFLL; ++m )
                {
                    v29 = m;
                    for ( n = 0LL; n < 0xE8D4A50FFFLL; ++n )
                    {
                        v31 = n;
                        v24 = 0LL;
                        while ( v24 < 0xE8D4A50FFFLL )
                        {
                            v30 = v24;
                            v41 = v14;
                            x = math_rand_Float64();
                            v27 = math_rand_Float64();
                            v26 = math_pow(x, 2.0);
                            v25 = math_pow(v27, 2.0);
                            v14 = v41;
                            if ( v26 + v25 <= 1.0 )
                                v14 = v41 + 1;
                            v24 = v30 + 1;
                            v13 = v35;
                            j = v33;
                            k = v32;
                            m = v29;
                            n = v31;
                        }
                    }
                }
            }
        }
        ++v13;
    }
    v40 = v14;
    // 上面的循环一共有 9999999999 ** 6 次
    v16 = math_pow(9.99999999999e11, 6.0);
    // pi/4作为随机种子，异或ptr（math_rand_Int()结果被修改会异或0xA），即key
    math_rand__ptr_Rand_Seed(math_rand_globalRand, COERCE_UNSIGNED_INT64(4.0 * (double)(int)v40 / v16) % 0x5F5E100);
    for ( ii = 0LL; ii < 24; ii = v34 + 1 )
    {
        v34 = ii;
        ptr[ii] ^= math_rand_Int() % 100;
    }
    
    // 加密1
    if ( v1.len < 0x10uLL )
        runtime_panicSliceAlen();
    v53 = runtime_slicebytetostring((runtime_tmpBuf *)v45, ptr, 24LL);
    v57.str = plainText.str;
    v57.len = 16LL;
    v62 = main_encrypt(v53, v57);
    if ( v1.len < 0x20uLL )
        runtime_panicSliceAlen();
    
    // 加密2
    v39 = v62._r0.len;
    str = v62._r0.str;
    v54 = runtime_slicebytetostring((runtime_tmpBuf *)v44, ptr, 24LL);
    v58.str = plainText.str + 16;
    v58.len = 16LL;
    v63 = main_encrypt(v54, v58);
    
    // 比较1
    if ( v39 == 32 )
    {
        v48 = v63._r0.str;
        v38 = v63._r0.len;
        runtime_memequal();
        v63._r0.len = v38;
        v18 = v19;
    }
    else
    {
        v18 = 0;
    }
    if ( !v18 )
        goto LABEL_28;
    
    // 比较2
    if ( v63._r0.len == 32 )
        runtime_memequal();
    else
        v20 = 0;
    if ( v20 )
    {
        v55.str = (uint8 *)"TOUFUL";
        v55.len = 6LL;
        v59.str = (uint8 *)"yes you are right";
        v59.len = 17LL;
        os_Setenv(v55, v59);
    }
    else
    {
        LABEL_28:
        v56.str = (uint8 *)"TOUFUL";
        v56.len = 6LL;
        v60.str = (uint8 *)"no no no~~~";
        v60.len = 11LL;
        os_Setenv(v56, v60);
    }
}

// math/rand.Int
int __golang math_rand_Int()
{
    ......
    return (*((__int64 (__golang **)(void *))math_rand_globalRand->src.tab + 3))(math_rand_globalRand->src.data) & 0x7FFFFFFFFFFFFFFFLL ^ 0xA;
}

// AES加密
// main.encrypt
retval_37F67C700 __golang main_encrypt(string key, string plainText)
{
    ......
    plainText_8 = plainText.len;
    plainTexta = plainText.str;
    len = key.len;
    v21.str = key.str;
    v21.len = len;
    v23 = runtime_stringtoslicebyte((runtime_tmpBuf *)buf, v21);
    result = (retval_37F67C700)crypto_aes_NewCipher(v23);
    if ( result._r1.tab )
    {
        v9 = 0LL;
        v10 = 0LL;
    }
    else
    {
        v16 = result._r0.len;
        str = result._r0.str;
        v17 = runtime_makeslice((runtime__type *)&RTYPE_uint8_0, plainText_8, plainText_8);
        v22.str = plainTexta;
        v22.len = plainText_8;
        v24 = runtime_stringtoslicebyte(0LL, v22);
        (*((void (__golang **)(int, _BYTE *, int, int, uint8 *, int, int))str + 5))(
            v16,
            v17,
            plainText_8,
            plainText_8,
            v24.array,
            v24.len,
            v24.cap);
        v4 = (uint8 *)runtime_makeslice((runtime__type *)&RTYPE_uint8_0, 2 * plainText_8, 2 * plainText_8);
        v5 = 2 * plainText_8;
        v6 = v17;
        v7 = 0LL;
        v8 = 0LL;
        while ( plainText_8 > v7 )
        {
            v11 = v6[v7];
            if ( v8 >= v5 )
                runtime_panicIndex();
            v4[v8] = a0123456789abcd_0[v11 >> 4];
            v12 = a0123456789abcd_0[v11 & 0xF];
            if ( v5 <= v8 + 1 )
                runtime_panicIndex();
            v4[v8 + 1] = v12;
            ++v7;
            v8 += 2LL;
        }
        v13 = runtime_slicebytetostring(0LL, v4, v5);
        v10 = v13.len;
        v9 = v13.str;
        result._r1.tab = 0LL;
        result._r1.data = 0LL;
    }
    result._r0.len = v10;
    result._r0.str = v9;
    return result;
}
```

以上可知计算出来的`pi/4`就是种子，这里直接patch掉计算的部分，将`rand_seed`的参数直接设置为计算好的：`0x31a2818'`

这里用的是WP里获取种子的大小，这个脚本其他不知道为啥，计算的key和flag不对。

```Go
func hello()  {
    aeskey:=[]byte{65,94,61,73,97,100,86,91,80,50,75,46,78,119,58,41,69,19,57,43,105,10,101,76}
    key1:=(math.Float64bits(3.141592653589793238462643383279502884197)%100000000)//
    rand.Seed(int64(key1))
    for i:=0;i<len(aeskey);i++ {
        aeskey[i] = byte((rand.Int())%100 ^ int(aeskey[i]))
    }
    a1,_:=DecryptAES(string(aeskey),"ff44ac7700732a16589f7ff8bdbaa923")
    a2,_:=DecryptAES(string(aeskey),"57c29c367a781ead5fb143469d75f319")
    fmt.Println("seed is:",key1)
    fmt.Println("key is:",string(aeskey))
    fmt.Printf("flag is:%s%s",a1,a2)
}
func DecryptAES(key string, encryptText string) (string, error) {
    decodeText, _ := hex.DecodeString(encryptText)
    cipher, err := aes.NewCipher([]byte(key))
    if err != nil {
        return "", err
    }
    out := make([]byte, len(decodeText))
    cipher.Decrypt(out, decodeText)
    return string(out[:]), nil
}
```

然后获取加密的`key`：`[100, 111, 95, 121, 111, 117, 95, 116, 104, 105, 110, 107, 95, 116, 104, 105, 115, 95, 105, 115, 95, 107, 101, 121]`

然后就可以进行AES解密了：

```Python
import base64
# key = [0x5B566461493D5E41, 0x293A774E2E4B3250, 0x4C650A692B391345]
# key = b''.join([i.to_bytes(8, "little") for i in key])
# # key = base64.b64encode(key.encode()).decode()
# print(key)
# key = [i ^ j for i, j in zip(key, rand_num)]
key = [100, 111, 95, 121, 111, 117, 95, 116, 104, 105, 110, 107, 95, 116, 104, 105, 115, 95, 105, 115, 95, 107, 101, 121]
from Crypto.Cipher import AES
data = bytes.fromhex('ff44ac7700732a16589f7ff8bdbaa923' + '57c29c367a781ead5fb143469d75f319')
print(AES.new(bytearray(key), AES.MODE_ECB).decrypt(data))
```
