# quark-n
quark-n的一些使用技巧

wiki: https://wiki.seeedstudio.com/cn/Quantum-Mini-Linux-Development-Kit/

大神项目地址：https://github.com/peng-zhihui/Project-Quantum

对应的外壳：https://gitee.com/coolflyreg163/quark-n-3d

1. 启动网络
http://wiki.friendlyarm.com/wiki/index.php/Use_NetworkManager_to_configure_network_settings

2. 镜像文件
https://files.seeedstudio.com/wiki/Quantum-Mini-Linux-Dev-Kit/quark-n-21-1-11.zip

3. 将TF卡系统拷贝到emmc，count的值需要先确定emmc的扇区数量
```bash
sudo dd if=/dev/mmcblk0 of=/dev/mmcblk1 bs=512 count=30717952 &
sudo watch -n 5 pkill -USR1 ^dd$
```

4. 擦除emmc，count的值需要先确定emmc的扇区数量
sudo dd if=/dev/zero of=/dev/mmcblk1 bs=512 count=30717952

5. 重启网卡设备
```bash
sudo ifconfig wlan0 down
sudo ifconfig wlan0 up
```

6. 连接网络的时候，如果需要输入提示密码
sudo nmcli --ask c up SSID

7. 如果总是出现提示密码未提供时，并且wifi的加密是wpa/wpa2个人级时，按照下方配置参数
主要参数：
- 802-11-wireless-security.key-mgmt:      wpa-psk
- 802-11-wireless-security.proto:         wpa
- 802-11-wireless-security.pairwise:      ccmp,tkip
- 802-11-wireless-security.group:         ccmp,tkip
- 802-11-wireless-security.psk-flags:     1 (agent-owned)

密码写入文件，wpa-psk类型内容格式：802-11-wireless-security.psk:secret12345

执行如下命令启动wifi连接
```bash
sudo nmcli c up [CONNECTION NAME | UUID] passwd-file /home/pi/.nmcli/passwd-wlan0
```

8. Linux下声卡独占的原因和解决
简单解决办法如下：
在/boot/defaults/loader.conf或/etc/sysctl.conf中加入下面两行。
```conf
hw.snd.pcm0.vchans=4
hw.snd.maxautovchans=4
```

9. 播放视频
```bash
sudo mplayer -vo fbdev2:/dev/fb1 -x 240 -y 135 -zoom /home/pi/Videos/BadApple.mp4
```
**视频最好转换到和屏幕一个分辨率，不然就会卡顿掉帧**

10. 视频分辨率转换
```
ffmpeg -i /home/pi/Videos/BadApple.mp4 -strict -2 -s 240x134 /home/pi/Videos/BadApple_240x134.mp4
```
分辨率必须是2的倍数所以，所以不能是240x135，而是240x134

11. 录音测试
查看录音设备：
```bash
sudo arecord –l
```
录音和播放
```bash
sudo arecord -Dhw:2,0 -d 10 -f cd -r 44100 -c 2 -t wav test.wav
sudo arecord -Dhw:2,0 -f cd -r 16000 -c 1 -t wav record.wav
sudo aplay -Dhw:2,0 /home/pi/Music/test.wav
```
参数解析
- -D 指定了录音设备，0,1 是card 0 device 1的意思，也就是TDM_Capture
- -d 指定录音的时长，单位时秒
- -f 指定录音格式，通过上面的信息知道只支持 cd cdr dat 
- -r 指定了采样率，单位时Hz
- -c 指定channel 个数
- -t 指定生成的文件格式

12. apt-get强制使用Ipv4
```bash
sudo apt-get -o Acquire::ForceIPv4=true update
```
永久解决办法：
```note
创建文件 /etc/apt/apt.conf.d/99force-ipv4
加入代码: Acquire::ForceIPv4 "true";
```

### TF卡有系统时启动到emmc分区
1. 将 npi-config 覆盖拷贝到 /usr/bin/npi-config
2. 运行sudo npi-config
3. 3 Boot Options -> B3 Boot device -> D3 emmc

### 使用新的dts的中的蓝色led设备
1. 下载源代码
   ```bash
   mkdir ~/GIT
   cd ~/GIT
   git clone https://gitee.com/coolflyreg163/quark-n.git 
   ```
2. 将 sun8i-h3-atom_n.dtb 替换到 /boot/sun8i-h3-atom_n.dtb
   ```bash
   cp ~/GIT/quark-n/sun8i-h3-atom_n.dtb /boot/
   ```
3. 重启
   ```bash
   sudo shutdown -r now
   ```
4. 用于测试的Python代码，gpio_key_led.py
   ```python
   from periphery import LED
   import time
   ledUser = LED("usr_led", True)
   while True:
      time.sleep(1)
      ledUser.write(255)
      time.sleep(1)
      ledUser.write(0)

   ledUser.close()
   ```
4. gpio_key_led.py是按下Key后，亮起蓝色led
5. 在/sys/class/leds下，显示 pwr_led(黄), status_led(白), usr_led(蓝)
   ```bash
   ls /sys/class/leds/
   ```
   或运行以下命令
   ```bash
   sudo cat /sys/kernel/debug/gpio
   ```
   输出结果里有一行
   ```
   gpio-359 (                    |usr_led             ) out hi
   ```
   即表示成功

### 用于自带LCD屏的数码时钟
**需要先执行：使用新的dts的中的蓝色led设备**
1. 下载源代码
   ```bash
   mkdir ~/GIT
   cd ~/GIT
   git clone https://gitee.com/coolflyreg163/quark-n.git 
   ```
2. 如果很早之前已经下载过源代码，需要更新，可以运行如下命令（这一步非必须）
   ```bash
   cd ~/GIT/quark-n
   git pull origin master
   ```
3. 备份之前的Clock
   ```bash
   cd /home/pi/WorkSpace/
   mv Clock Clock_bak
   ```
4. 将Clock放置到指定位置
   ```bash
   ln -s /home/pi/GIT/quark-n/WorkSpace/Clock ~/WorkSpace/
   ```
5. 将启动脚本放置到指定位置
   ```bash
   chmod +x /home/pi/GIT/quark-n/WorkSpace/Scripts/start_ui_clock.sh
   mkdir -p ~/WorkSpace/Scripts/services
   ln -s /home/pi/GIT/quark-n/WorkSpace/Scripts/services/ui_clock.service ~/WorkSpace/Scripts/services/
   ln -s /home/pi/GIT/quark-n/WorkSpace/Scripts/start_ui_clock.sh ~/WorkSpace/Scripts/
   ```
6. 从这里，下载2个字体文件：“STHeiti Light.ttc”，“PingFang.ttc”，拷贝到~/WorkSpace/Clock/fonts。
   ```
   https://gitee.com/coolflyreg163/quark-n/releases/Fonts
   ```
   或运行命令
   ```bash
   cd ~/WorkSpace/Clock/fonts
   wget https://gitee.com/coolflyreg163/quark-n/attach_files/603438/download/STHeiti%20Light.ttc
   wget https://gitee.com/coolflyreg163/quark-n/attach_files/603439/download/PingFang.ttc
   ```
7. 运行如下命令进行安装
   ```bash
   cd /home/pi/WorkSpace/Clock/
   sudo python -m pip install --index http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
   mkdir /home/pi/WorkSpace/Clock/logs
   sudo ln -s /home/pi/WorkSpace/Scripts/services/ui_clock.service /lib/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable ui_clock
   ```
   ** ruamel.yaml 需要使用阿里云的镜像来安装，豆瓣的镜像里没有！ **
   **到达这一步，已经在重启后会自动启动。下面是手动命令**
8. 命令提示：
   1. 启动 （手动启动后按Ctrl + C可脱离）
        ```bash
        sudo systemctl start ui_clock
        ```
   2. 停止
        ```bash
        sudo systemctl stop ui_clock
        ```
   3. 查看状态
        ```bash
        sudo systemctl status ui_clock
        ```
   4. 重启系统
        ```bash
        sudo shutdown -r now
        ```

#### 操作方式
1. GPIO按钮操作
   1. 按一下松开，界面上元素循环显示，不同界面，有不同反应
   2. 长按会显示进度条，根据时间不同，有不同的功能
      1. 长按 小于 2秒，不做任何操作
      2. 长按 大于等于 2秒 和 小于 3秒之间，界面显示YES，执行确认操作
      3. 长按 大于等于 3秒 和 小于 5秒之间，界面显示Menu View，进入到菜单界面
      4. 长按 大于等于 5秒 和 小于 10秒之间，界面目前无任何操作，会渐渐显示出POWER OFF
      5. 长按 大于等于 10秒，关机
2. 鼠标操作
   1. 点击界面元素，会有变化，不同界面有不同反应
3. 界面说明
   1. 除了菜单界面的，任意界面，将鼠标移动到最左侧，将显示进入菜单的提示，点击鼠标即可进入菜单界面
   2. 欢迎界面
      1. 无任何操作，定时跳转到数字表盘
   3. 数字表盘界面
      1. 界面元素，分为4行
         1. 第一行循环显示，鼠标可点击
            1. CPU温度 + CPU占比
            2. MEM（内存）剩余空间 + 使用量占比
            3. DSK（磁盘，TF或EMMC）剩余空间 + 使用量占比
         2. 第二行时间，12/24小时切换显示，鼠标可点击
         3. 第三行日期
         4. 第四行，鼠标可点击
            1. IP + 下载速度
            2. 上行速度 + 下载速度
      2. GPIO单按，同时循环以上所有元素
   4. 菜单界面，任意界面长按 大于等于 3秒 和 小于 5秒之间，界面显示Menu View，进入到菜单界面
      1. 界面元素
         1. 时钟：切换到数字表盘（由群内大神 “海 风” 提供原始Clock界面程序）
         2. 孙悟空：开启关闭wukong-robot。需要修改后的悟空版本。参见 https://gitee.com/coolflyreg163/wukong-in-quark-n
         3. 相机：可以支持PS3 Eye摄像头进行拍照，或者其他USB免驱动摄像头
         4. 相册：可以查看通过摄像头拍摄的照片
         5. 启动画面：切换启动图
         6. 设置：正在开发中
         7. 关闭：退出ui_clock
      2. GPIO操作
         1. 长按 大于等于 2秒 和 小于 3秒之间，界面显示YES时，执行确认操作
      3. 其他功能正在开发中

#### 功能列表
- [X] 数字表盘
- [X] 启动画面：切换启动欢迎图界面
- [X] 相机：从USB摄像头拍照
- [X] 相册：查看摄像头拍照的列表
- [X] 孙悟空：集成wukong-robot，需细化功能需求
- [ ] 加入MPU6050，进行姿态操作，增加甩飞Quark-N的几率
- [ ] 实现设置界面的功能，可调整一些参数

#### 与WuKong-robot共同使用
**注意：需要先执行：Linux下声卡独占的原因和解决**
1. 备份原始自带的WuKong
   ```bash
   cd /home/pi/WorkSpace/WuKong
   mv wukong-robot wukong-robot_bak
   ```
2. 从 https://gitee.com/coolflyreg163/wukong-in-quark-n 下载WuKong
   ```bash
   cd /home/pi/WorkSpace/WuKong
   git clone https://gitee.com/coolflyreg163/wukong-in-quark-n wukong-robot
   ```
3. 创建所需目录，执行如下命令：
   ```bash
   mkdir /home/pi/WorkSpace/WuKong/wukong-robot/temp
   chmod 777 /home/pi/WorkSpace/WuKong/wukong-robot/temp
   ```
4. 把这个库里的 /WuKong/contrib/LcdDisplay.py 替换到 /home/pi/.wukong/contrib/ 文件夹下的同名文件
   ```bash
   cp ~/GIT/quark-n/WuKong/contrib/LcdDisplay.py /home/pi/.wukong/contrib/
   ```
5. 在 /home/pi/.wukong/config.yml 中添加配置。注意要符合格式
   ```yaml
   quark_ui:
       api_host: 'http://127.0.0.1:4096'
       validate: '57b7d993ffbd75aca3fe2060cf204f93' 
       enable: true
   ```
5. 目前snowboy的在线训练无法使用了，暂时在配置中改为：hotword: 'wukong.pmdl'，唤醒词：孙悟空
6. 其他可以参考wukong-robot原版的配置
7. 如果需要使用悟空进行拍照，需要安装fswebcam，运行如下命令安装
   ```bash
   sudo apt-get install fswebcam
   ```

#### 其他驱动
- RTL8821CU（8811cu）： https://gitee.com/coolflyreg163/rtl8821cu  内有ko文件，quark-n可直接可使用
- RTL8723DU：https://gitee.com/coolflyreg163/rtl8723du    内有ko文件，quark-n直接可使用