* 小米10s
* HyperOS 1.0.4.TGACNXM

# 解BL锁

之前拿这台备用机体验了下HyperOS，没成想正规解锁BL有那么多限制。

好在可以绕过👉[澎湃绕五级解锁BL锁教程](https://www.bilibili.com/video/BV1eYtDehEVJ/?spm_id_from=333.999.0.0)（工具网上都能搜到）

但还是得等小米账号与手机绑定168小时……

# Root

通过小米设置里的系统更新下载最新的完整包，来获取卡刷包。

解压卡刷包后得到`payload.bin`

使用[payload-dumper-go](https://github.com/ssut/payload-dumper-go)执行`.\payload-dumper-go.exe .\payload.bin`得到`boot.img`

下载安装Delta版本的Magisk👉[Release v26.4-kitsune-2](https://github.com/HuskyDG/magisk-files/releases/tag/v26.4-kitsune-2)

使用Magisk修补`boot.img`，放到电脑上。

手机重启，长按音量下键，进入fastboot模式。

下载个fastboot，执行` .\fastboot.exe flash boot .\Mi-Root\magisk_patched-26400_y3axM.img`

> 如果手机变砖，刷入原来的boot.img

然后就ok啦。