# quark-n
quark-n的一些使用技巧

wiki: https://wiki.seeedstudio.com/cn/Quantum-Mini-Linux-Development-Kit/

大神项目地址：https://github.com/peng-zhihui/Project-Quantum

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

### TF卡有系统时启动到emmc分区
1. 将 npi-config 覆盖拷贝到 /usr/bin/npi-config
2. 运行sudo npi-config
3. 3 Boot Options -> B3 Boot device -> D3 emmc

### 使用新的dts的中的蓝色led设备
1. 将 sun8i-h3-atom_n.dtb 替换到 /boot/sun8i-h3-atom_n.dtb
2. 重启
3. Python代码
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

### 用于自带LCD屏的Clock（由群内大神 “海 风” 提供原始程序）
1. 拷贝WorkSpace下的Clock和Script到 quark-n 的 /home/pi/WorkSpace/ 下
2. 运行如下命令进行安装
   ```bash
    mkdir /home/pi/WorkSpace/Clock/logs
    sudo ln -s /home/pi/WorkSpace/Scripts/services/ui_clock.service /lib/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable ui_clock
   ```
3. 命令提示：
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
