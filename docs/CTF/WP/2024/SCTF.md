# ez_cython

网上看到个思路，学习一下。

解包后得到python源码：

```python
import cy

def str_hex(input_str):
    # return (lambda .0: [ ord(char) for char in .0 ])(input_str)
    return [ ord(char) for char in input_str ]


def main():
    print('欢迎来到猜谜游戏！')
    print("逐个输入字符进行猜测，直到 'end' 结束。")
    while True:
        guess_chars = []
        char = input("请输入一个字符（输入 'end' 结束）：")
        if char == 'end':
            break
        elif len(char) == 1:
            guess_chars.append(char)
            continue
        print('请输入一个单独的字符。')
    guess_hex = str_hex(''.join(guess_chars))
    if cy.sub14514(guess_hex):
        print('真的好厉害！flag非你莫属')
    
    print('不好意思，错了哦。')
    retry = input('是否重新输入？(y/n)：')
    if retry.lower() != 'y':
        pass
    
    print('游戏结束')

if __name__ == '__main__':
    main()
```

`cy`是`pyd`文件

这里使用了类似`hook`的思路，来把`cy`中对输入数据的处理，打印出来。

```python
import cy

# 创建一个符号，来程序对其的操作
class Symbol:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __rshift__(self, other):
        if isinstance(other, Symbol):
            expression = Symbol(f"({self.name} >> {other.name})")
        else:
            expression = Symbol(f"({self.name} >> {other})")
        return expression

    def __lshift__(self, other):
        if isinstance(other, Symbol):
            expression = Symbol(f"({self.name} << {other.name})")
        else:
            expression = Symbol(f"({self.name} << {other})")
        return expression

    def __rxor__(self, other):
        if isinstance(other, Symbol):
            expression = Symbol(f"({self.name} ^ {other.name})")
        else:
            expression = Symbol(f"({self.name} ^ {other})")
        return expression

    def __xor__(self, other):
        if isinstance(other, Symbol):
            expression = Symbol(f"({self.name} ^ {other.name})")
        else:
            expression = Symbol(f"({self.name} ^ {other})")
        return expression

    def __add__(self, other):
        if isinstance(other, Symbol):
            expression = Symbol(f"({self.name} + {other.name})")
        else:
            expression = Symbol(f"({self.name} + {other})")
        return expression

    def __and__(self, other):
        if isinstance(other, Symbol):
            expression = Symbol(f"({self.name} & {other.name})")
        else:
            expression = Symbol(f"({self.name} & {other})")
        return expression

# 创建一个列表class，实现列表的各个方法
class AList:
    def __init__(self, nums):
        self.nums = [Symbol(str(num)) for num in nums]

    def __getitem__(self, key):
        return self.nums[key]

    def copy(self):
        return AList(self.nums)

    def __len__(self):
        return len(self.nums)

    def __setitem__(self, key, value):
        # print(f"new_{self.nums[key]} = {value}")
        # self.nums[key] = Symbol(f"new_{self.nums[key].name}")
        print(f"{self.nums[key]} = {value}")
        self.nums[key] = Symbol(f"{self.nums[key].name}")

    def __eq__(self, other):
        print(f"{self.nums} == {other}")
        return self.nums == other

inp = AList([f"a[{i}]" for i in range(32)])
res = cy.sub14514(inp)

if __name__ == '__main__':
    print(res)
```

