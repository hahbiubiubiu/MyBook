## 序列化与反序列化

序列化其实就是将数据转化成一种可逆的数据结构，逆向的过程就叫做反序列化。

### 示例

```php
array('xiao','shi','zi');
// a:3:{i:0;s:4:"xiao";i:1;s:3:"shi";i:2;s:2:"zi";}
// a:array代表是数组，后面的3说明有三个属性
// i:代表是整型数据int，后面的0是数组下标
// s:代表是字符串，后面的4是因为xiao长度为4
    
class test{
    public $a;
    public $b;
    function __construct(){$this->a = "xiaoshizi";$this->b="laoshizi";}
    function happy(){return $this->a;}
}
// O:4:"test":2:{s:1:"a";s:9:"xiaoshizi";s:1:"b";s:8:"laoshizi";}
// O:代表Object是对象的意思，也是类
// 序列化后的内容只有成员变量，没有成员函数
    
class test{
    protected  $a;
    private $b;
    function __construct(){$this->a = "xiaoshizi";$this->b="laoshizi";}
    function happy(){return $this->a;}
}
// protected则会在变量名前加上\x00*\x00
// private则会在变量名前加上\x00类名\x00
// O:4:"test":2:{s:4:" * a";s:9:"xiaoshizi";s:7:" test b";s:8:"laoshizi";}
```

## 反序列化中常见的魔术方法

```php
__wakeup() //执行unserialize()时，先会调用这个函数
__sleep() //执行serialize()时，先会调用这个函数
__destruct() //对象被销毁时触发
__call() //在对象上下文中调用不可访问的方法时触发
__callStatic() //在静态上下文中调用不可访问的方法时触发
__get() //用于从不可访问的属性读取数据或者不存在这个键都会调用此方法
__set() //用于将数据写入不可访问的属性
__isset() //在不可访问的属性上调用isset()或empty()触发
__unset() //在不可访问的属性上使用unset()时触发
__toString() //把类当作字符串使用时触发
__invoke() //当尝试将对象调用为函数时触发
```

## 利用



序列化字符串中表示对象属性个数的值大于真实的属性个数时会跳过`__wakeup`的执行

```php
class test{
    public $a;
    public function __construct(){
        $this->a = 'abc';
    }
    public function __wakeup(){
        $this->a='666';
    }
    public function  __destruct(){
        echo $this->a;
    }
}

unserialize('O:4:"test":1:{s:1:"a";s:3:"abc";}');
// 输出结果为666
unserialize('O:4:"test":2:{s:1:"a";s:3:"abc";}');
// 输出结果为abc
```



