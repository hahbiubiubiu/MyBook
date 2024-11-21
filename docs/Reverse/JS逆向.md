# 无限debugger

`console`中执行：

```js
Function.prototype.temp_constructor = Function.prototype.constructor;
Function.prototype.temp_prototype = Function.prototype.constructor.prototype;
Function.prototype.constructor = function() {
    if (arguments && typeof arguments[0] === "string") {
        if (arguments[0].includes("debugger"))
            return "";
    }
    return Function.prototype.temp_constructor.apply(this, arguments);
};
Function.prototype.constructor.prototype = Function.prototype.temp_prototype;
```

