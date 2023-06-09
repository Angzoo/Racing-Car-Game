import pygame
import random
import RPi.GPIO as GPIO
from time import sleep
from pygame.locals import *
import spidev

#1. GPIO Setting
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# SPI 인스턴스 spi생성
spi = spidev.SpiDev()

# 라즈베리와 SPI통신 시작
spi.open(0,0)

# SPI 통신 속도 설정
spi.max_speed_hz = 100000

# 딜레이 시간(센서 측정 간격)
delay = 0.5

# MCP3008채널 중 센서에 연결한 채널 설정
sw_ch = 0
vrx_ch = 1
vry_ch = 2

led_r = 2
buzzer = 14

GPIO.setup(led_r, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)

# Frq = 1

p= GPIO.PWM(buzzer, 1)

# led_r와 buzzer를 3번 울리는 함수
def alarm():
    for i in range(3):
        p.start(50)
        GPIO.output(led_r, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(led_r, GPIO.LOW)
        p.stop()
        sleep(0.5)

# 0~7까지 8개의 채널에서 SPI데이터를 읽음
# 조이스틱 값 읽기 함수
def readadc(adcnum):
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, (8 + adcnum)<<4,0])
    data = ((r[1] & 3) << 8) + r[2]
    return data
   
#2. Game Setting
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (150,150,150)
RED = (255,0,0)

# frame settings
clock = pygame.time.Clock()
fps = 120

class Car:
    # 게임 캐릭터 생성하기
    image_car = [
        'RacingCar01.png', 'RacingCar02.png', 'RacingCar03.png', 'RacingCar04.png', 'RacingCar05.png',
        'RacingCar06.png', 'RacingCar07.png', 'RacingCar08.png', 'RacingCar09.png', 'RacingCar10.png',
        'RacingCar11.png', 'RacingCar12.png', 'RacingCar13.png', 'RacingCar14.png', 'RacingCar15.png',
        'RacingCar16.png', 'RacingCar17.png', 'RacingCar18.png', 'RacingCar19.png', 'RacingCar20.png',
    ]
   
    def __init__(self, x=0, y=0, dx = 0, dy =0):
        self.image = ""
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.rect = Rect(x,y,dx,dy)
       
    def load_image(self):
        self.image = pygame.image.load(random.choice(self.image_car))
        self.width = self.image.get_rect().size[0]
        self.height = self.image.get_rect().size[1]
       
    def draw_image(self):
        screen.blit(self.image,[self.x, self.y])
       
    def move_x(self):
        self.x += self.dx
   
    def move_y(self):
        self.y += self.dy
   
    def check_out_of_screen(self):
        if self.x + self.width > WINDOW_WIDTH or self.x < 0 :
            self.x -= self.dx
   
    def check_crash(self, car):
        if(self.x + self.width > car.x) and (self.x < car.x + car.width) and (self.y < car.y + car.height) and (self.y + self.height > car.y):
            return True
        else:
            return False
       
    # Car 클래스에 충돌 여부를 판단하는 메서드
    def check_collision(self, other):
        if (self.x + self.width > other.x) and (self.x < other.x + other.width) and (self.y < other.y + other.height) and (self.y + self.height > other.y):
            return True
        else:
            return False

if __name__ == '__main__':
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Racing Car Game")
    clock = pygame.time.Clock()
   
    # 충돌 이미지
    crash_img = pygame.image.load('crash.png')
    crash_img_rect = crash_img.get_rect()
   
    # 게임 사운드
    pygame.mixer.init()
    pygame.mixer.music.load('race.wav')
    sound_crash = pygame.mixer.Sound('crash.wav')
    sound_engine = pygame.mixer.Sound('engine.wav')
     
    # 사용자 레이싱 카 생성
    player = Car(WINDOW_WIDTH / 2, (WINDOW_HEIGHT - 150), 0, 0)
    player.load_image()
   
    # 컴퓨터 레이싱 카 생성
    cars = []
    car_cnt = 3
   
    for i in range(car_cnt):
        x = random.randrange(0, WINDOW_WIDTH-55)
        car = Car(x, random.randrange(-150, -50), 0, random.randint(5, 10))
        car.load_image()
        cars.append(car)
       
    # 도로 차선 생성
    lanes = []
    lane_width = 10
    lane_height = 80
    lane_margin = 20
    lane_cnt = 10
    lane_x = (WINDOW_WIDTH - lane_width)/2
    lane_y = -10

    for i in range(lane_cnt):
        lanes.append([lane_x, lane_y])
        lane_y += lane_height + lane_margin
       
    score = 0
    crash = True
    game_on = True
    while game_on:
        pygame.init()
        pygame.font.init()
        sw_val = readadc(sw_ch) # 클릭하면 0
        vrx_val = readadc(vrx_ch)
        vry_val = readadc(vry_ch)
       
        #이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_on = False
               
            # 게임 다시 시작
            if crash:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    crash = False
                    for i in range(car_cnt):
                        cars[i].x = random.randrange(0, WINDOW_WIDTH - cars[i].width)
                        cars[i].y = random.randrange(-150, -50)
                        cars[i].load_image()
                   
                    player.load_image()
                    player.x = 175
                    player.dx = 0
                    pygame.mouse.set_visible(False)
                    sound_engine.play()
                    sleep(5)
                    pygame.mixer.music.play(-1)
                   
        print("x : ", vrx_val, "  y : ", vry_val)

        if vry_val > 1015:
            player.dx = 4
        elif vry_val <= 100:
            player.dx = -4
        else:
           player.dx = 0
                       
        # 배경화면 채우기
        screen.fill(GRAY)

        #게임 화면 출력
        if not crash:
            # 도로 차선 이동
            for i in range(lane_cnt):
                pygame.draw.rect(screen, WHITE, [lanes[i][0], lanes[i][1], lane_width, lane_height])
                lanes[i][1] += 10
                if lanes[i][1] > WINDOW_HEIGHT:
                    lanes[i][1] = -40 - lane_height
               
            # 사용자 레이싱 카
            player.draw_image()
            player.move_x()
            player.check_out_of_screen()
                 
            # 컴퓨터 레이싱 카
            for i in range(car_cnt):
                cars[i].draw_image()
                cars[i].y += cars[i].dy
                if cars[i].y > WINDOW_HEIGHT:
                    score += 10
                    cars[i].y = random.randrange(-150,-50)
                    cars[i].x = random.randrange(0, WINDOW_WIDTH-cars[i].width)
                    cars[i].dy = random.randint(4,9)
                    cars[i].load_image()
                       
            # 레이싱 카 충돌사고 체크
            for i in range(car_cnt):
                if player.check_crash(cars[i]):
                    crash = True
                    crash_img_rect.center = [player.rect.center[0], player.rect.top]
                    screen.blit(crash_img, crash_img_rect)
                    pygame.display.update()
                    pygame.mixer.music.stop()
                    sound_crash.play()
                    sleep(2)
                    pygame.mouse.set_visible(True)
                    alarm()
                    break
               
            font_30 = pygame.font.SysFont("FixedSys", 30, True, False)
            txt_score = font_30.render("Score : " + str(score), True, BLACK)
            screen.blit(txt_score,[15, 15])
            pygame.display.update()
           
        else:
            draw_x = (WINDOW_WIDTH / 2) - 200
            draw_y = WINDOW_HEIGHT / 2
                   
            image_intro = pygame.image.load('PyCar.png')
            screen.blit(image_intro,[draw_x, draw_y - 280])
                   
            font_40 = pygame.font.SysFont("FixedSys", 40, True, False)
            font_30 = pygame.font.SysFont("FixedSys", 30, True, False)
            text_title = font_40.render("Racing Car Game", True, BLACK)
            screen.blit(text_title,[draw_x, draw_y])
                   
            score_text = font_40.render("Score : " + str(score), True, WHITE)
            screen.blit(score_text,[draw_x, draw_y+70])
                   
            text_start = font_30.render("Press Space Key to Start!", True, RED)
            screen.blit(text_start,[draw_x, draw_y+140])
            pygame.display.update()
               
        clock.tick(fps)
    pygame.quit()