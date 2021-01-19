from periphery import GPIO
from periphery import LED
import time

gpio_l = GPIO("/dev/gpiochip1", 3, "in")
gpio_r = GPIO("/dev/gpiochip0", 203, "in")
# led = GPIO("/dev/gpiochip1", 7, "out") # 直接使用gpio
# ledPower = LED("pwr_led", True)
# ledStatus = LED("status_led", True)
ledUser = LED("usr_led", True)

while True:
    l = gpio_l.read()
    r = gpio_r.read()
    print("L-{} R-{}".format(l,r))

    time.sleep(0.1)
    ledUser.write(255 if l else 0)



gpio_l.close()
gpio_r.close()
ledUser.close()

