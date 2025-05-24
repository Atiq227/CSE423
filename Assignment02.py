from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
display_width = 800
display_height = 800
diamond= None
diamond_width = 20
catcher_width = 65
catcher_height = 80
falling_speed = 2.5
diamond_count = 10
restart_key = b"r"
DIAMONDS= [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 1.0, 0.0), (1.0, 0.0, 1.0)] 
WHITE= (1.0, 1.0, 1.0)
RED= (1.0, 0.0, 0.0)
TEAL= (0.0, 1.0, 1.0)
AMBER= (1.0, 0.75, 0.0)
score = 0
diamonds = []
gameover= False
COLOR_BAR= WHITE
live=1
pause_status= False
exit_status= False
catcher_x = display_width // 2

def zone_find(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) >= abs(dy) and (dx >= 0 and dy >= 0):
        zone = 0
        return x1, y1, x2, y2, zone
    elif abs(dy) > abs(dx) and (dx >= 0 and dy >= 0):
        zone = 1
        return y1, x1, y2, x2, zone
    elif abs(dy) > abs(dx) and (dx < 0 and dy >= 0):
        zone = 2
        return y1, -x1, y2, -x2, zone
    elif abs(dx) >= abs(dy) and (dx < 0 and dy >= 0):
        zone = 3
        return -x1, y1, -x2, y2, zone
    elif abs(dx) >= abs(dy) and (dx < 0 and dy < 0):
        zone = 4
        return -x1, -y1, -x2, -y2, zone
    elif abs(dy) > abs(dx) and (dx < 0 and dy < 0):
        zone = 5
        return -y1, -x1, -y2, -x2, zone
    elif abs(dy) > abs(dx) and (dx >= 0 and dy < 0):
        zone = 6
        return -y1, x1, -y2, x2, zone
    elif abs(dx) >= abs(dy) and (dx >= 0 and dy < 0):
        zone = 7
        return x1, -y1, x2, -y2, zone
    
def backtoorg(x, y, zone): 
    if zone == 0:
        return x, y
    elif zone == 1:
        return y , x
    elif zone == 2:
        return -y , x
    elif zone == 3:
        return -x , y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y , -x
    elif zone == 6:
        return y , -x
    elif zone == 7:
        return x , -y
    else:
        print("Error: Invalid zone")
        return x , y

def draw_pixel(x, y, color=(1, 1, 1)):
    glColor3fv(color)
    glBegin(GL_POINTS)
    glVertex2i(int(x), int(y))
    glEnd()

def midpoint_line(x1, y1, x2, y2, color=(1, 1, 1)):
    x1, y1, x2, y2, zone = zone_find(x1, y1, x2, y2)
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x, y = x1, y1
    while x <= x2:
        real_x, real_y = backtoorg(x, y, zone)
        draw_pixel(real_x, real_y, color)
        if d > 0:
            y += 1
            d += incNE
        else:
            d += incE
        x += 1

def draw_diamond(x, y, color):
    size = diamond_width * 0.6
    midpoint_line(x, y + (size+7), x - size, y, color) 
    midpoint_line(x - size, y, x, y - (size+7), color)  
    midpoint_line(x, y - (size+7), x + size, y, color)  
    midpoint_line(x + size, y, x, y + (size+7), color)  


def draw_catcher(x, color):
    y = 50  
    w = catcher_width
    top = y + 5     
    bottom = y - 10 
    midpoint_line(x - w, top, x - w + 15, bottom, color)        
    midpoint_line(x - w + 15, bottom, x + w - 15, bottom, color) 
    midpoint_line(x + w - 15, bottom, x + w, top, color)         
    midpoint_line(x + w, top, x - w, top, color)                 


def draw_buttons():
    #restart_button
    midpoint_line(20, display_height - 50, 50, display_height - 70, TEAL)
    midpoint_line(20, display_height - 50, 50, display_height - 30, TEAL)
    #pause_play_button
    if not pause_status:
        midpoint_line(display_width // 2 - 10, display_height - 70, display_width // 2 - 10, display_height - 30, AMBER)
        midpoint_line(display_width // 2 + 10, display_height - 70, display_width // 2 + 10, display_height - 30, AMBER)
    else:
        midpoint_line(display_width // 2 - 10, display_height - 70,
                  display_width // 2 - 10, display_height - 30, AMBER)
        midpoint_line(display_width // 2 - 10, display_height - 70,
                  display_width // 2 + 10, display_height - 50, AMBER)
        midpoint_line(display_width // 2 + 10, display_height - 50,
                  display_width // 2 - 10, display_height - 30, AMBER)
    #exit_button
    midpoint_line(display_width - 60, display_height - 60, display_width - 40, display_height - 40, RED)
    midpoint_line(display_width - 60, display_height - 40, display_width - 40, display_height - 60, RED)

def mouse_click(button, state, x, y):
    global score, diamond, COLOR_BAR, pause_status, gameover, exit_status
    y = display_height - y
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if 20 <= x <= 50 and display_height - 70 <= y <= display_height - 30:
            score = 0
            diamond = None
            gameover = False
            falling_speed = 2.5
            pause_status = False
            COLOR_BAR = WHITE
            create_diamonds()
        if display_width // 2 - 10 <= x <= display_width // 2 + 10 and display_height - 70 <= y <= display_height - 30:
            pause_status = not pause_status
        if display_width - 60 <= x <= display_width - 40 and display_height - 60 <= y <= display_height - 40:
            print(f"Goodbye! Score: {score}")
            exit_status = True

def special_keys(key, x, y):
    global catcher_x
    if not gameover and not pause_status:
        if key == GLUT_KEY_LEFT:
            catcher_x = max(catcher_x - 20, catcher_width)
        elif key == GLUT_KEY_RIGHT:
            catcher_x = min(catcher_x + 20, display_width - catcher_width)

def update(value):
    global diamond, score, gameover, COLOR_BAR, falling_speed
    if not gameover and not pause_status:
        if diamond:
            x, y, color = diamond
            y -= falling_speed
            falling_speed += 0.003
            diamond = (x, y, color)
            if y < 60 and abs(x - catcher_x) < catcher_width:
                score += 1
                print("Score:", score)
                diamond = None
            elif y < 0:
                print("Game Over! Score:", score)
                COLOR_BAR = RED
                gameover = True
                diamond = None
                falling_speed = 2.5
        else:
            if not diamonds:
                create_diamonds()
            diamond = diamonds.pop(0)
    if exit_status:
        glutLeaveMainLoop()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def draw_text(x, y, text, color=(1, 1, 1)):
    glColor3fv(color)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

def keyboard(key, x, y):
    global gameover, score, pause_status, COLOR_BAR, diamond
    if gameover and key == restart_key:
        score = 0
        pause_status = False
        falling_speed = 2.5
        gameover = False
        COLOR_BAR = WHITE
        diamond = None
        create_diamonds()


def display():
    global catcher_x
    glClear(GL_COLOR_BUFFER_BIT)
    draw_catcher(catcher_x, COLOR_BAR)
    if diamond:
        draw_diamond(diamond[0], diamond[1], diamond[2])
    draw_buttons()
    if gameover:
        draw_text(display_width // 2 - 80, display_height // 2 + 10, "Game Over! :(", RED)
        draw_text(display_width // 2 - 140, display_height // 2 - 20, "Press R to restart the game", WHITE)
    glutSwapBuffers()

def create_diamonds():
        x = random.randint(60, display_width - 60)
        y = display_height - 40
        color = random.choice(DIAMONDS)
        diamonds.append((x, y, color))

def init():
    glClearColor(0, 0, 0, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, display_width, 0, display_height)

def main():
    global catcher_x
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(display_width, display_height)
    glutCreateWindow(b"Catch the Diamond")
    init()
    create_diamonds()
    glutDisplayFunc(display)
    glutMouseFunc(mouse_click)
    glutSpecialFunc(special_keys)
    glutKeyboardFunc(keyboard) 
    glutTimerFunc(16, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()