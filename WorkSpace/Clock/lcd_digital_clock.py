from datetime import datetime
import pygame
import os
import socket
import time

def cputempf():
    f = open("/sys/class/thermal/thermal_zone0/temp")
    CPUTemp = f.read()
    f.close()
    StringToOutput = "CPU {0} C".format(int(CPUTemp) /1000.0)
    return StringToOutput


if not os.getenv('SDL_FBDEV'):
    os.putenv('SDL_FBDEV', '/dev/fb1')#利用quark自带tft屏幕显示

def get_host_ip(): 
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

pygame.init()

# icon = pygame.image.load('digitalClock.png')
# pygame.display.set_icon(icon)
display_info = pygame.display.Info()
w = display_info.current_w
h = display_info.current_h
window_size=(w,h)

screen = pygame.display.set_mode(window_size, pygame.FULLSCREEN)
pygame.mouse.set_visible( False )
# pygame.display.set_caption('Digital Clock')
print(os.path.dirname(__file__))
fontPath = os.path.dirname(__file__) + "/fonts/DS-DIGIT.TTF"
bigFont = pygame.font.Font(fontPath, 82)
middleFont = pygame.font.Font(fontPath, 40)
smallFont = pygame.font.Font(fontPath, 30)
miniFont = pygame.font.Font(fontPath, 26)

# bigFont = pygame.font.SysFont('DS-Digital',130)#Comic Sans MS
# smallFont = pygame.font.SysFont('DS-Digital',30)

white = (255,255,255)
black = (0,0,0)
green = (0,255,0)

months = ['January', 'February', 'March', 'April', 'May', 
'June', 'July', 'August', 'September', 'October', 'November', 'December']
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ]

cputemp = cputempf()
running = True
while running:
    screen.fill(black)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            running = False
            pygame.quit()
            
    now = datetime.now()
    today = datetime.today()

    minute = now.strftime('%M')
    second = now.strftime('%S')
    hour = int(now.strftime('%H'))
    month = now.strftime('%m')
    date = now.strftime('%d')
    year = now.strftime("%Y")
    day = today.weekday()
    day = days[day]
    
    if int(second) % 5 == 0:
        cputemp = cputempf()
    #month = months[month-1]
    
    am = 'AM'
    
    if hour > 12:
        hour = hour-12
        am = 'PM'
    shour = str(hour)
    if len(shour) == 1:
        shour = '0' + shour
    timeStr = shour + ':' + minute
    timeText = bigFont.render(timeStr,True,green)
    secondText = middleFont.render(second, True, green)
    monthText = smallFont.render(year + '-' + month + '-' + date,True,green)
    yearText = smallFont.render(year,True,green)
    amText = middleFont.render(am,True,green)
    dayText = smallFont.render( day,True,green)

    cputempText = smallFont.render(cputemp, True, white)

    ip = get_host_ip()
    ipText = miniFont.render(ip, True, white)
    
    screen.blit(cputempText, (10,0))
    screen.blit(timeText, (4,16))
    screen.blit(secondText, (190, 52))
    screen.blit(monthText, (15,86))
    # screen.blit(yearText, (145,120))
    screen.blit(amText,(190,22))
    screen.blit(dayText,(170,86))
    screen.blit(ipText,(15,112))

    pygame.display.update()
    time.sleep(1.0/24.0)
