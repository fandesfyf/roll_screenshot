# roll_screenshot
用python实现的滚动截屏功能,本功能集成自[Jamtools](https://github.com/fandesfyf/JamTools)和[Jamscreenshot](https://github.com/fandesfyf/Jamscreenshot)项目

如果你还需要普通区域截屏类似qq截屏的功能,可以看看(https://github.com/fandesfyf/Jamscreenshot)

## 具体思路
滚动截屏的步骤：滚动-->截屏-->寻找拼接点-->拼接

##### 滚动
滚动部分主要用了pynput模块的滚动功能,该模块还可以实现[全局快捷键](https://editor.csdn.net/md/?articleId=103226341),具体方法本文不深究。

##### 截屏
由于我的小工具集是采用pyqt作为界面的，就直接用qt的截屏方法了，可以自行改为pil或win32的截屏方法

截屏中止(滚动中止)采用了双重判定，当前后两张图片相同(到了尽头)时可以自动停止，当按下鼠标左键时也会停止

##### 寻找拼接点
寻找拼接点就是比较相邻的图片，寻找下一张图片在前一张图片的相同部分的位置，并记录下来。

但考虑到有些截屏区域是包含不滚动部分的，即所有图片都有相同的头部或边框，所以截取的图片就不能直接用来寻找拼接点，需要比较多张图片并去除相同部分的影响；

所以这一部分又可以分几步：把图片灰度化(不然就要比较rgb3个通道,处理时间大大增加)-->把图片的灰度值储存于数组中-->比较前n张图片并找出所有相同的边界点(上、左、右三处，下方由于拼接的时候会覆盖掉就不用识别了)-->排除相同的部分开始寻找拼接的界限(逐行比较)

更具体的实现已经在代码中标明了,仔细看注释应该可以看懂,可以根据需要改动代码,例如可以完全去除qt库(这个库是真的大!)

听说还可以用opencv实现图片拼接功能(而且效率upup的),等我研究一下再来改蛤

-----20210226更新-------

使用opencv进行特征提取和匹配,拼接效率更快,需要安装opencv-contrib-python==3.4.2.17(包含sift算法)
