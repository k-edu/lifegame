# Example file showing a basic pygame "game loop"
import random
import numpy as np
import pygame
import scipy
import scipy.signal
import json
from patterns2 import grider2
from patterns import grider


def paste_pattern(grid, pattern, x, y, color):
    for i in range(len(pattern)):
        for j in range(len(pattern[0])):
            if 0 <= y + i < len(grid) and 0 <= x + j < len(grid[0]):
                grid[y + i][x + j] = pattern[i][j] * color


# pygame setup
pygame.init()
screen = pygame.display.set_mode((360, 180), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

grid_width = 500
grid_height = 300

scale = 1.0

background_color = "white"



def get_color(id: int) -> str:
    return {
        0: background_color,
        1: (75, 178, 255),
        2: (255, 75, 178),
        3: (178, 255, 75),
    }[id]


def gen_count_matrix_with_id(grid: np.ndarray, id: int) -> np.ndarray:
    convolution = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    return scipy.signal.convolve2d(
        grid == id, convolution, mode="same", boundary="fill", fillvalue=0
    )


def next_generation(grid: np.ndarray) -> np.ndarray:
    count_mats = [gen_count_matrix_with_id(grid, i) for i in range(1, 4)]
    count_mat = sum(count_mats)

    alive_mat = ((grid != 0) & (count_mat == 2)) | (count_mat == 3)
    most_id = np.argmax(count_mats, axis=0) + 1
    next = most_id * alive_mat
    return next

blue_n, green_n, red_n = 0, 0, 0

grid = np.zeros((grid_height, grid_width), dtype=int)
for _ in range(grid_height * grid_width // 5):
    i = random.randint(0, grid_height - 1)
    j = random.randint(0, grid_width - 1)
    radian = np.arctan2(i - grid_height / 2, j - grid_width / 2)
    deg = np.degrees(radian)
    deg %= 360
    if 0 <= deg < 120:
        grid[i][j] = 1
        blue_n += 1
    elif 120 <= deg < 240:
        grid[i][j] = 2
        red_n += 1
    else:
        grid[i][j] = 3
        green_n += 1


next_grid = grid.copy()
reset_screen = True
playing = False
menu = False
point = 0
scrollx=0
scrolly=0
n1 = 0
n2 = 0
n3 = 0


w, h = pygame.display.get_surface().get_size()
font1 = pygame.font.SysFont("Serif", bold=True, size=40)
font2 = pygame.font.SysFont("ubuntu", bold=True, size=20)
menu_width = 105
menu_height =50


k = None
def test_push(d):
    K = [pygame.K_1,
    pygame.K_2,
    pygame.K_3,
    pygame.K_4][d - 1]
    if k == K:
        return True

while running:
    cell_width = int(10 * scale)
    cell_height = int(10 * scale)
    b=0
    k=0
    save_button=pygame.Rect((screen.get_width()//2)-menu_width//2,100,menu_width,menu_height)
    save_button_text=font1.render("save",True,(255,255,255))
    load_button=pygame.Rect((screen.get_width()//2)-menu_width//2,160,menu_width,menu_height)
    load_button_text=font1.render("load",True,(255,255,255))
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN: # マウスボタンが押されたとき
            x,y = event.pos                             # マウスカーソルの座標を取得
            b  = event.button
            if save_button.collidepoint(event.pos):
                f = open('myfile.txt', 'w')
                f.write(json.dumps(grid.tolist()))
                f.close()
            if load_button.collidepoint(event.pos):
                f = open('myfile.txt', 'r')
                next_grid=np.array(json.loads(f.read()))
                f.close()
                print("load")
        elif event.type == pygame.KEYDOWN:
            k = event.key
            if k == pygame.K_ESCAPE:
                playing = False
                menu = not menu
                print(menu)
    changed_positions = np.argwhere(next_grid != grid)
    past_grid = grid.copy()
    grid = next_grid.copy()

    # draw grid
    for pos in changed_positions:
        y, x = pos
        if past_grid[y][x] == 1:
            blue_n -= 1
        if past_grid[y][x] == 2:
            red_n -= 1
        if past_grid[y][x] == 3:
            green_n -= 1
        if grid[y][x] == 1:
            blue_n += 1
        if grid[y][x] == 2:
            red_n += 1
        if grid[y][x] == 3:
            green_n += 1
        pygame.draw.rect(
            screen,
            get_color(int(grid[y][x])),
            (x * cell_width+scrollx, y * cell_height+scrolly, cell_width, cell_height),
        )

    if playing:
        next_grid = next_generation(grid)

    # # draw grid
    if reset_screen:
        reset_screen = False
        screen.fill(background_color)
        for y in range(grid_height):
            for x in range(grid_width):
                if grid[y][x]:
                    color = get_color(grid[y][x])
                    pygame.draw.rect(
                        screen,
                        color,
                        (x * cell_width+scrollx, y * cell_height+scrolly, cell_width, cell_height),
                    )
    
    # point per second
    if playing:
        point += 1
    text = font1.render(str(point), True, (255,0,0))
    pygame.draw.rect(
        screen, "white", (10 , 10, 150, 40)
    )
    screen.blit(text, (10,10))

    # count cells
    gcn = font2.render(str(green_n), True, (178, 255, 75))
    rcn = font2.render(str(red_n), True, (255, 75, 178))
    bcn = font2.render(str(blue_n), True, (75, 178, 255))
    text_c_cell = font2.render("セルの数：", True, (0, 0, 0, 255))
    kanma = font2.render(',', True, (0, 0, 0, 255))
    pygame.draw.rect(
        screen, "white", (10, 140, 185, 20)
    )
    screen.blit(gcn, (10, 140))
    screen.blit(rcn, (70, 140))
    screen.blit(bcn, (130, 140))

    # ontouch
    if pygame.mouse.get_pressed()[0]:
        x, y = pygame.mouse.get_pos()
        x = x // cell_width
        y = y // cell_height
        if 0 <= x < grid_width and 0 <= y < grid_height:
            next_grid[y][x] = random.randint(1, 3)

    if pygame.mouse.get_pressed()[2]:
        x, y = pygame.mouse.get_pos()
        x = x // cell_width
        y = y // cell_height
        for i in range(1):
            for j in range(1):
                paste_pattern(
                    next_grid,
                    grider2,
                    x + len(grider2[0]) * i,
                    y + len(grider2) * j,
                    2,
                )                    # メッセージを所得
                                     # ボタンの種類を取得
    
    if menu:
        pygame.draw.rect(screen,(20,20,20),save_button)
        screen.blit(save_button_text,(save_button.left+5,save_button.top+5))
        pygame.draw.rect(screen,(20,20,20),load_button)
        screen.blit(load_button_text,(load_button.left+5,load_button.top+5))


    if b==4:
        scale *= 1.1
        reset_screen = True
    if b==5:
        scale /= 1.1
        reset_screen = True
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        scrollx += 10
        reset_screen = True
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        scrollx -= 10
        reset_screen = True
    if pygame.key.get_pressed()[pygame.K_UP]:
        scrolly += 10
        reset_screen = True
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        scrolly -= 10
        reset_screen = True
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        playing = not pygame.key.get_pressed()[pygame.K_LSHIFT]
    new_w, new_h = pygame.display.get_surface().get_size()
    if (w != new_w) or (h != new_h):
         reset_screen = True
         w = new_w
         h = new_h
    # flip() the display to put your work on screen
    if n1 >= 1:
        k = None
        mouseX, mouseY = pygame.mouse.get_pos()
        paste_pattern(
            next_grid,
            grider,
            (mouseX - scrollx ) // cell_width - len(grider[0]) // 2 ,
            (mouseY - scrolly) // cell_height - len(grider) // 2 ,
            2,
        )
        n1 = n1 - 1
    if n2 >= 1:
        k = None
        mouseX, mouseY = pygame.mouse.get_pos()
        paste_pattern(
            next_grid,
            grider2,
            (mouseX - scrollx ) // cell_width - len(grider2[0]) // 2 ,
            (mouseY - scrolly) // cell_height - len(grider2) // 2 ,
            2,
        )
        n2 = n2 - 1
    if n3 >= 1:
        k = None
        mouseX, mouseY = pygame.mouse.get_pos()
        paste_pattern(
            next_grid,
            grider,
            (mouseX - scrollx ) // cell_width,
            (mouseY - scrolly) // cell_height,
            2,
    )
        n3 = n3 - 1
        
    if point >200:
        if test_push(1) == True:
            n1 = n1 + 1
            point = point - 200
    if point >1000:
        if test_push(2) == True:
            n2 = n2 + 1
            point = point - 1000
    if point > 10000:
        if test_push(3) == True:
            n3 = n3 + 1
            point = point - 100000
    
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
