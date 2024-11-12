import pygame
import sys
import random
import time
import serial

# 아두이노와 시리얼 연결 설정
ser = serial.Serial('COM5', 9600)  # COM 포트 번호는 시스템에 따라 수정

pygame.init()

# 조이스틱 중앙값 및 허용 오차 설정
JOYSTICK_MID = 512  # 아날로그 값이 0에서 1023 사이로 나오는 경우 중앙값은 512
JOYSTICK_THRESHOLD = 100  # 조이스틱이 움직였다고 판단할 최소값 차이

# 색상 설정   
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (228, 57, 72)
YELLOW = (234, 128, 0)
PINK = (204, 70, 64)
PURPLE = (58, 58, 135)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

# 폰트 설정
capsule_font = pygame.font.Font('DNFBitBitv2.ttf', 25)
result_font = pygame.font.Font('DNFBitBitv2.ttf', 100)

# 현재 모니터의 해상도를 얻어 화면 설정
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("IT's(아이티스) 행원제 캡슐 뽑기 게임")

# 이미지 로드
machine_img = pygame.image.load('machine.png')
capsule_pink_img = pygame.image.load('capsule_pink.png')
capsule_purple_img = pygame.image.load('capsule_purple.png')
capsule_yellow_img = pygame.image.load('capsule_yellow.png')
open_capsule_pink_img = pygame.image.load('open_capsule_pink.png')
open_capsule_purple_img = pygame.image.load('open_capsule_purple.png')
open_capsule_yellow_img = pygame.image.load('open_capsule_yellow.png')
fog_img = pygame.image.load('fog.png')

# 머신 이미지 비율 축소
m_width, m_height = machine_img.get_size()
m_new_width = int(m_width / 5.5)
m_new_height = int(m_height / 5.5)
machine_img = pygame.transform.scale(machine_img, (m_new_width, m_new_height))

# 머신 이미지 중앙 배치
m_x = (screen_width - m_new_width) // 2
m_y = (screen_height - m_new_height) // 2

# 그리드 개수 설정
grid_rows = 7
grid_cols = 10

# 그리드 간격 설정
grid_margin_x = 4.7
grid_margin_y = 21.5

# 그리드 좌표 설정
grid_start_x = m_x + 599
grid_start_y = m_y + 87
grid_width = m_new_width - 655
grid_height = m_new_height - 170
cell_width = (grid_width - (grid_cols - 1) * grid_margin_x) // grid_cols
cell_height = (grid_height - (grid_rows - 1) * grid_margin_y) // grid_rows

# 현재 위치 설정
current_row = 0
current_col = 0

# 안개 이미지 비율 조정 및 배치
fog_img_width, fog_img_height = fog_img.get_size()
fog_img = pygame.transform.scale(fog_img, (int(fog_img_width * 1.5), int(fog_img_height * 1.5)))
fog_left_x = m_x + 10
fog_left_y = m_y + 350
fog_right_x = m_x + 500
fog_right_y = m_y + 450

# 캡슐 배치 확률 설정
capsule_probabilities = {
    capsule_yellow_img: 0.4,
    capsule_pink_img: 0.4,
    capsule_purple_img: 0.2,
}

# 캡슐 이미지 리스트 생성
capsule_imgs = []
for capsule_img, prob in capsule_probabilities.items():
    capsule_imgs.extend([capsule_img] * int(prob * 100))

# 그리드에 배치할 캡슐 이미지 리스트 생성
grid_capsules = random.choices(capsule_imgs, k=grid_rows * grid_cols)

# 각 캡슐 이미지에 색상 매핑
capsule_colors = {
    capsule_yellow_img: YELLOW,
    capsule_pink_img: PINK,
    capsule_purple_img: PURPLE,
}

# 모서리 테두리 그리기 함수
def draw_corner_rect(surface, color, rect, thickness):
    pygame.draw.line(surface, color, rect.topleft, (rect.topleft[0] + thickness * 6, rect.topleft[1]), thickness)
    pygame.draw.line(surface, color, rect.topleft, (rect.topleft[0], rect.topleft[1] + thickness * 6), thickness)
    pygame.draw.line(surface, color, rect.topright, (rect.topright[0] - thickness * 6, rect.topright[1]), thickness)
    pygame.draw.line(surface, color, rect.topright, (rect.topright[0], rect.topright[1] + thickness * 6), thickness)
    pygame.draw.line(surface, color, rect.bottomleft, (rect.bottomleft[0] + thickness * 6, rect.bottomleft[1]), thickness)
    pygame.draw.line(surface, color, rect.bottomleft, (rect.bottomleft[0], rect.bottomleft[1] - thickness * 6), thickness)
    pygame.draw.line(surface, color, rect.bottomright, (rect.bottomright[0] - thickness * 6, rect.bottomright[1]), thickness)
    pygame.draw.line(surface, color, rect.bottomright, (rect.bottomright[0], rect.bottomright[1] - thickness * 6), thickness)

# 결과 저장할 변수 지정&시간 저장 변수
select_capsule = None
show_result = False
result_text = ""
selection_time = None
selected_positions = set()  # 선택된 캡슐 위치를 추적하는 집합

# 상품 확률
prize_number = {
    "1등": 0.015,
    "2등": 0.03,
    "3등": 0.143,
    "꽝": 0.812
}

# 상품 리스트
prize_texts=[]
for prize_text, prob in prize_number.items():
    prize_texts.extend([prize_text] * int(prob*72))

# 반투명 검정 배경 그리기 함수
def draw_transparent_black_background(surface, alpha):
    background = pygame.Surface((screen_width, screen_height))
    background.set_alpha(alpha)
    background.fill(BLACK)
    surface.blit(background, (0, 0))

# 메인 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        data = line.split()

        if len(data) == 3 and 'X:' in data[0] and 'Y:' in data[1] and 'Button:' in data[2]:
            x_val = int(data[0].split(':')[1])
            y_val = int(data[1].split(':')[1])
            button_state = int(data[2].split(':')[1])

            if not show_result:
                if x_val > JOYSTICK_MID + JOYSTICK_THRESHOLD:
                    current_col = (current_col + 1) % grid_cols
                elif x_val < JOYSTICK_MID - JOYSTICK_THRESHOLD:
                    current_col = (current_col - 1) % grid_cols
                if y_val > JOYSTICK_MID + JOYSTICK_THRESHOLD:
                    current_row = (current_row + 1) % grid_rows
                elif y_val < JOYSTICK_MID - JOYSTICK_THRESHOLD:
                    current_row = (current_row - 1) % grid_rows

                if button_state == 0:  # 버튼이 눌림
                    select_capsule = (current_row, current_col)
                    selected_index = current_row * grid_cols + current_col
                    if grid_capsules[selected_index] is not None:  # 캡슐이 있는 경우에만
                        show_result = True
                        selection_time = time.time()  # 선택된 시간 저장
                        selected_positions.add(select_capsule)
                        result = random.choice(prize_texts)
                        if result == "1등":
                            result_text = "1등"
                            result_color = pygame.Color(GOLD)
                        elif result == "2등":
                            result_text = "2등"
                            result_color = pygame.Color(SILVER)
                        elif result == "3등":
                            result_text = "3등"
                            result_color = pygame.Color(BRONZE)
                        else: #꽝
                            result_text = "꽝"
                            result_color = pygame.Color(BLACK)
                        prize_texts.remove(result)

    # 화면 그리기
    screen.fill(WHITE)
    screen.blit(machine_img, (m_x, m_y))

    for row in range(grid_rows):
        for col in range(grid_cols):
            x = grid_start_x + col * (cell_width + grid_margin_x)
            y = grid_start_y + row * (cell_height + grid_margin_y)

            # 캡슐 이미지 배치
            capsule_img = grid_capsules[row * grid_cols + col]
            if capsule_img is not None:
                resized_capsule_img = pygame.transform.scale(capsule_img, (cell_width, cell_height))
                screen.blit(resized_capsule_img, (x, y))

                # 캡슐에 따른 색상으로 텍스트 생성 및 배치
                number = row * grid_cols + col + 1
                capsule_num_color = capsule_colors[capsule_img]
                capsule_num = capsule_font.render(str(number), True, capsule_num_color)
                capsule_num_rect = capsule_num.get_rect(center=(x + cell_width // 2, y + cell_height // 2))
                screen.blit(capsule_num, capsule_num_rect)

            # 모서리 테두리 배치
            rect = pygame.Rect(x, y, cell_width, cell_height)
            if row == current_row and col == current_col:
                draw_corner_rect(screen, RED, rect, 3)

    # 선택된 캡슐 결과창
    if show_result and select_capsule:
        draw_transparent_black_background(screen, 128)  # 투명도 50% 검정 배경 그리기
        screen.blit(fog_img, (fog_left_x, fog_left_y)) # 안개 이미지1 배치하기
        screen.blit(fog_img, (fog_right_x, fog_right_y)) # 안개 이미지2 배치하기

        # 1초 후에 열린 캡슐 이미지와 결과 텍스트 표시
        if time.time() - selection_time > 1:
            # 선택한 캡슐 이미지에 맞는 열린 캡슐 이미지 선택
            selected_row, selected_col = select_capsule
            selected_capsule_img = grid_capsules[selected_row * grid_cols + selected_col]
            if selected_capsule_img == capsule_pink_img:
                open_capsule_img = open_capsule_pink_img
            elif selected_capsule_img == capsule_purple_img:
                open_capsule_img = open_capsule_purple_img
            elif selected_capsule_img == capsule_yellow_img:
                open_capsule_img = open_capsule_yellow_img

            # 열린 캡슐 이미지 중앙 배치
            open_capsule_width, open_capsule_height = open_capsule_img.get_size()
            open_capsule_x = (screen_width - open_capsule_width) // 2
            open_capsule_y = (screen_height - open_capsule_height) // 2
            screen.blit(open_capsule_img, (open_capsule_x, open_capsule_y))

            # 결과 텍스트 표시
            result_surface = result_font.render(result_text, True, result_color)
            result_rect = result_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(result_surface, result_rect)

            # 결과창 3초 후 제거 및 캡슐 제거
            if time.time() - selection_time > 3:
                show_result = False
                grid_capsules[selected_row * grid_cols + selected_col] = None  # 선택된 캡슐 제거

    pygame.display.flip()

pygame.quit()
sys.exit()
