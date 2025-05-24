from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
def draw_line(x1, y1, x2, y2, width=5):
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(x1,y1)
    glVertex2f(x2,y2)
    glEnd()

def draw_point(x, y, point_size=5.0):
    glPointSize(point_size)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def setup_viewport():
    glViewport(0, 0, 800, 800)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 800, 0.0, 800, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)

def is_inside_house(x, y):
    return house_x_left <= x <= house_x_right and house_y_bottom <= y<= house_y_top
def is_inside_roof(x,y):
    return house_x_left <= x <= house_y_top and  roof_peak_x<= y <= roof_peak_y

def update_raindrops(value):
    global raindrop_positions, wind_offset
    for i in range(20):
        x = random.randint(0, 800)
        y = random.randint(0, 800)
        while is_inside_house(x, y):
            x = random.randint(0, 800)
            y = random.randint(0, 800)
        raindrop_positions.append((x, y))

    updated_raindrops = []
    for x, y in raindrop_positions:
        y -= random.uniform(5, 10)
        if wind_offset == -1:
            x -= random.uniform(5, 20)
        elif wind_offset == 1:
            x += random.uniform(5, 20)
        if not is_inside_house(x, y) and not is_inside_roof(x,y):
            updated_raindrops.append((x, y))

    raindrop_positions[:] = updated_raindrops

    glutPostRedisplay()
    glutTimerFunc(30, update_raindrops, 0)

def render_scene():
    glClearColor(*background_day_color, 1.0)  
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
    glLoadIdentity()
    setup_viewport()
    glColor3f(*house_color_day)  

    # base
    draw_line(house_x_left, house_y_bottom, house_x_right, house_y_bottom)
    draw_line(house_x_left, house_y_bottom, house_x_left, house_y_top)
    draw_line(house_x_right, house_y_bottom, house_x_right, house_y_top)
    draw_line(house_x_left, house_y_top, house_x_right, house_y_top)

    # roof
    draw_line(house_x_left, house_y_top, roof_peak_x, roof_peak_y)
    draw_line(house_x_right, house_y_top, roof_peak_x, roof_peak_y)

    # window
    window_x_left = house_x_left + 50
    window_x_right = window_x_left + 50
    window_y_bottom = house_y_bottom + 100
    window_y_top = window_y_bottom + 50
    draw_line(window_x_left, window_y_bottom, window_x_right, window_y_bottom, width=3)
    draw_line(window_x_left, window_y_bottom, window_x_left, window_y_top, width=3)
    draw_line(window_x_right, window_y_bottom, window_x_right, window_y_top, width=3)
    draw_line(window_x_left, window_y_top, window_x_right, window_y_top, width=3)

    # window_design
    draw_line((window_x_left + window_x_right) / 2, window_y_bottom, (window_x_left + window_x_right) / 2, window_y_top,
              width=2)
    draw_line(window_x_left, (window_y_bottom + window_y_top) / 2, window_x_right, (window_y_bottom + window_y_top) / 2,
              width=2)

    # door
    door_x_left = house_x_right - 100
    door_x_right = door_x_left + 50
    door_y_bottom = house_y_bottom
    door_y_top = door_y_bottom + 120
    draw_line(door_x_left, door_y_bottom, door_x_left, door_y_top)
    draw_line(door_x_right, door_y_bottom, door_x_right, door_y_top)
    draw_line(door_x_left, door_y_top, door_x_right, door_y_top)

    # doorknob
    draw_point(door_x_right - 10, door_y_bottom + 60, point_size=8.0)

    # raindrops
    glColor3f(0.0, 0.0, 1.0) 
    for x, y in raindrop_positions:
        draw_line(x, y, x, y - 10, width=1)

    glutSwapBuffers()

def handle_key_press(key, x, y):
    global background_day_color, house_color_day, wind_offset
    if key == b'd':
        background_day_color = (1.0, 1.0, 1.0)
        house_color_day = (0.0, 0.0, 0.0)
    elif key == b'n':
        background_day_color = (0.0, 0.0, 0.0)
        house_color_day = (1.0, 1.0, 1.0)
    glutPostRedisplay()
def handle_special_key_press(key, x, y):
    global wind_offset
    if key == GLUT_KEY_LEFT:
        wind_offset = -1
    elif key == GLUT_KEY_RIGHT:
        wind_offset = 1
    glutPostRedisplay()

raindrop_positions = []
background_day_color = (1.0, 1.0, 1.0)
background_night_color = (0.0, 0.0, 0.0)
house_color_day = (0.0, 0.0, 0.0)
house_color_night = (1.0, 1.0, 1.0)
house_x_left = 250
house_x_right = 500
house_y_bottom = 300
house_y_top = 500
roof_peak_x = (house_x_left + house_x_right) / 2
roof_peak_y = house_y_top + 100
wind_offset = 0

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(800, 800)
glutInitWindowPosition(100, 100)
glutCreateWindow(b"Task1")
glutDisplayFunc(render_scene)
glutKeyboardFunc(handle_key_press)
glutSpecialFunc(handle_special_key_press)
glutTimerFunc(1, update_raindrops, 0)
glutMainLoop()



########################Task 2########################
def draw_dots():
    global blink_mode, blink_start_time, pause_mode
    glEnable(GL_POINT_SMOOTH)
    glPointSize(dot_diameter)
    glBegin(GL_POINTS)

    for i in range(len(dots)):
        x, y, color, move_x, move_y = dots[i]
        if pause_mode:
            move_x = 0
            move_y = 0
            blink_mode = False
        if blink_mode and not pause_mode:
            current_time = glutGet(GLUT_ELAPSED_TIME)
            time_diff = (current_time - blink_start_time) % 800
            if time_diff < 100:
                color = (0.0, 0.0, 0.0)
            else:
                original_color = initial_colors[i]
                color = original_color
        glColor3f(*color)
        glVertex2f(x, y)
        x += movement_speed * move_x
        y += movement_speed * move_y
        if x < boundary_left + dot_diameter:
            x = boundary_left + dot_diameter
            move_x = -move_x
        if x > boundary_right - dot_diameter:
            x = boundary_right - dot_diameter
            move_x = -move_x
        if y < boundary_bottom + dot_diameter:
            y = boundary_bottom + dot_diameter
            move_y = -move_y
        if y > boundary_top - dot_diameter:
            y = boundary_top - dot_diameter
            move_y = -move_y
        dots[i] = (x, y, color, move_x, move_y)
    glEnd()
def generate_random_dot(x, y):
    if boundary_left < x < boundary_right and boundary_bottom < y < boundary_top:
        r, g, b = (random.random(), random.random(), random.random())
        color = (r, g, b)
        move_x = random.choice([-1, 1])
        move_y = random.choice([-1, 1])
        for existing_dot in dots:
            if (
                abs(existing_dot[0] - x) < dot_diameter * 4
                and abs(existing_dot[1] - y) < dot_diameter * 4
            ):
                return
        dots.append((x, y, color, move_x, move_y))
        initial_colors.append(color)

def mouse_event(button, state, x, y):
    global blink_mode, blink_start_time, pause_mode

    if pause_mode:
        return
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        generate_random_dot(x, 600 - y)
        print("New dot added")
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if blink_mode == False:
            blink_mode = not blink_mode
            blink_start_time = glutGet(GLUT_ELAPSED_TIME)
            print("blink mode activated")
        else:
            blink_mode = not blink_mode
            print("blink mode deactivated")

def special_keys_event(key, x, y):
    global movement_speed, blink_mode, pause_mode
    if key == GLUT_KEY_UP:
        if movement_speed<=0.8:
            movement_speed += 0.07
            print("Speed increased")
    elif key == GLUT_KEY_DOWN:
        if movement_speed>0.1:
            movement_speed -= 0.07
            print("Speed decreased")

def keyboard_event(key, x, y):
    global pause_mode, movement_speed, blink_mode, blink_mode_prev
    if key == b" ":
        pause_mode = not pause_mode
        if pause_mode:
            blink_mode_prev = blink_mode
            blink_mode = False
            for i in range(len(dots)):
                x, y, color, move_x, move_y = dots[i]
                move_x = 0
                move_y = 0
                dots[i] = (x, y, color, move_x, move_y)
            print("Dots frozen")
        else:
            blink_mode = blink_mode_prev
            blink_mode_prev = None
            for i in range(len(dots)):
                move_x = random.choice([-1, 1])
                move_y = random.choice([-1, 1])
                dots[i] = (dots[i][0], dots[i][1], dots[i][2], move_x, move_y)
            print("Dots unfrozen")
def draw_boundary():
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex2f(boundary_right, boundary_top)
    glVertex2f(boundary_left, boundary_top)
    glVertex2f(boundary_left, boundary_top)
    glVertex2f(boundary_left, boundary_bottom)
    glVertex2f(boundary_right, boundary_bottom)
    glVertex2f(boundary_left, boundary_bottom)
    glVertex2f(boundary_right, boundary_bottom)
    glVertex2f(boundary_right, boundary_top)
    glEnd()
def setup_view():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 800, 0, 600, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    setup_view()
    glColor3f(1.0, 1.0, 1.0)
    draw_boundary()
    draw_dots()
    glutSwapBuffers()



dots = []
boundary_left = 0
boundary_right = 800
boundary_bottom = 0
boundary_top = 600
dot_diameter = 15
movement_speed = 0.05
blink_mode = False
blink_mode_prev = None
blink_start_time = 0
pause_mode = False
initial_colors = []
glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(800, 600)
glutCreateWindow(b"Taks2")
glutDisplayFunc(display)
glutMouseFunc(mouse_event)
glutSpecialFunc(special_keys_event)
glutKeyboardFunc(keyboard_event)
glutIdleFunc(display)
glutMainLoop()