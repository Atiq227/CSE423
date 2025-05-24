from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math 
import time


camera_pos = (0,300, 400)
camera_angle = 0
fovY = 120
GRID_LENGTH = 600
tile_size = 60


player_pos = [0, 0, 0]
gun_angle = 0
life = 5
bullets_missed = 0
game_over = False
score = 0
enemy_angles = []  
ANGLE_THRESHOLD = 10
last_fire_time = 0
fire_delay = 0.5 


bullets = []

enemies = []


first_person = False


cheat_mode = False
cheat_vision = False

BULLET_SPEED = 10
ENEMY_SPEED = 0.05
BULLET_RANGE = 1000

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2]+50)

    # Rotate body with gun
    if game_over:
        glRotatef(90, 1, 0, 0)  
    else:
        glRotatef(gun_angle, 0, 0, 1) 

    # Body (Cuboid) - Olive green
    glColor3f(0.5, 0.7, 0.2)
    glPushMatrix()
    glScalef(0.5, 1, 1.5)
    glutSolidCube(30)
    glPopMatrix()

    # Head (Sphere) - Black
    glPushMatrix()
    glTranslatef(0, 0, 35)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 10, 20, 20)
    glPopMatrix()

    # Left Leg (Cuboid) - Blue
    glPushMatrix()
    glTranslatef(0, -8, -45)
    glColor3f(0, 0, 1)
    glScalef(0.5, 0.5, 2)
    glutSolidCube(20)
    glPopMatrix()

    # Right Leg (Cuboid) - Blue
    glPushMatrix()
    glTranslatef(0, 8, -45)
    glColor3f(0, 0, 1)
    glScalef(0.5, 0.5, 2)
    glutSolidCube(20)
    glPopMatrix()

    # Left Arm (Cylinder) - Skin color
    glPushMatrix()
    glTranslatef(0, 15, 20)
    glRotatef(90, 0, 1, 0)
    glColor3f(1, 0.8, 0.6)
    gluCylinder(gluNewQuadric(), 5, 5, 30, 10, 10)
    glPopMatrix()

    # Right Arm (Cylinder) - Skin color
    glPushMatrix()
    glTranslatef(0, -15, 20)
    glRotatef(90, 0, 1, 0)
    glColor3f(1, 0.8, 0.6)
    gluCylinder(gluNewQuadric(), 5, 5, 30, 10, 10)
    glPopMatrix()

    # Gun (Cylinder) - Gray
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glRotatef(90, 0, 1, 0)
    glColor3f(0.7, 0.7, 0.7)
    gluCylinder(gluNewQuadric(), 4, 4, 30, 10, 10)
    glPopMatrix()

    glPopMatrix()

def draw_enemy(x, y, z, scale_factor):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(scale_factor, scale_factor, scale_factor)

    # Body - Red
    glColor3f(1, 0, 0)
    gluSphere(gluNewQuadric(), 15, 20, 20)

    # Head - Black
    glTranslatef(0, 0, 25)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 8, 20, 20)

    glPopMatrix()

def draw_bullet(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1, 0, 0)
    glutSolidCube(5)
    glPopMatrix()

def draw_grid():
    glPushMatrix()
    for x in range(-GRID_LENGTH, GRID_LENGTH, tile_size):
        for y in range(-GRID_LENGTH, GRID_LENGTH, tile_size):
            if ((x + y) // tile_size) % 2 == 0:
                glColor3f(0.7, 0.5, 0.95)
            else:
                glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + tile_size, y, 0)
            glVertex3f(x + tile_size, y + tile_size, 0)
            glVertex3f(x, y + tile_size, 0)
            glEnd()
    glPopMatrix()

    
    wall_height = 100

    
   
    glColor3f(0, 1, 1)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()

    
    glColor3f(0, 0, 1)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()


   
    glColor3f(0, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glEnd()



def keyboardListener(key, x, y):
    global player_pos, gun_angle, cheat_mode, cheat_vision, game_over, life, bullets_missed, bullets

    if game_over:
        if key == b'r':
            restart_game()
        return

    if key == b'w':
        player_pos[0] += 10 * math.cos(math.radians(gun_angle))
        player_pos[1] += 10 * math.sin(math.radians(gun_angle))

    if key == b's':
        player_pos[0] -= 10 * math.cos(math.radians(gun_angle))
        player_pos[1] -= 10 * math.sin(math.radians(gun_angle))

    if key == b'a':
        gun_angle += 5

    if key == b'd':
        gun_angle -= 5

    if key == b'c':
        cheat_mode = not cheat_mode

    if key == b'v':
        cheat_vision = not cheat_vision

def specialKeyListener(key, x, y):
    global camera_pos, camera_angle
    cx, cy, cz = camera_pos
    if key == GLUT_KEY_UP:
        cz += 10
    if key == GLUT_KEY_DOWN:
        cz -= 10
    if key == GLUT_KEY_LEFT:
        camera_angle -= 2
    if key == GLUT_KEY_RIGHT:
        camera_angle += 2
    camera_pos = (cx, cy, cz)

def mouseListener(button, state, x, y):
    global first_person
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_over:
            bullet_start_x = player_pos[0] + 20 * math.cos(math.radians(gun_angle))
            bullet_start_y = player_pos[1] + 20 * math.sin(math.radians(gun_angle))
            bullet_start_z = player_pos[2] + 70  
            bullets.append([bullet_start_x, bullet_start_y, bullet_start_z, gun_angle])
            print("Player Bullet Fired!")

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    cx, cy, cz = camera_pos
    if first_person:
       
        eye_x = player_pos[0]
        eye_y = player_pos[1]
        eye_z = player_pos[2] + 100
        
         
        center_x = player_pos[0] + 100 * math.cos(math.radians(gun_angle))
        center_y = player_pos[1] + 100 * math.sin(math.radians(gun_angle))
        center_z = player_pos[2] + 100
    if cheat_mode and cheat_vision:
          
        eye_x = player_pos[0]
        eye_y = player_pos[1] +10
        eye_z = player_pos[2] + 110            
        center_x = player_pos[0] + 100
        center_y = player_pos[1] + 50
        center_z = player_pos[2] -300
    else:
        
        r = math.sqrt(cx**2 + cy**2)
        eye_x = r * math.cos(math.radians(camera_angle))
        eye_y = r * math.sin(math.radians(camera_angle))
        eye_z = cz
        center_x, center_y, center_z = 0, 0, 0

    gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)

def idle():
    global last_fire_time, fire_delay, bullets, enemies, game_over, life, bullets_missed, score, gun_angle

    if game_over:
        return

    # Move bullets and check for collisions
    new_bullets = []
    for b in bullets:
        bx, by, bz, angle = b
        hit = False
        bx += BULLET_SPEED * math.cos(math.radians(angle))
        by += BULLET_SPEED * math.sin(math.radians(angle))

        # Check bullet-enemy collision
        for i, e in enumerate(enemies):
            ex, ey, ez, _ = e
            if not cheat_mode:
                if math.sqrt((bx - ex)**2 + (by - ey)**2) < 30:
                    enemies[i] = random_enemy()
                    score += 1
                    hit = True
                    break
            else:
                if math.sqrt((bx - ex)**2 + (by - ey)**2) < 130:
                    enemies[i] = random_enemy()
                    score += 1
                    hit = True
                    break

        if not hit:
            if math.sqrt((bx - player_pos[0])**2 + (by - player_pos[1])**2) < BULLET_RANGE:
                new_bullets.append([bx, by, bz, angle])
            else:
                bullets_missed += 1
                print(f"Bullet missed: {bullets_missed}")
                if bullets_missed > 10:
                    bullets_missed -=1
                    game_over = True
                    draw_text(10, 650, "GAME OVER. Press R to Restart")

    bullets = new_bullets

    # Move enemies
    for i, e in enumerate(enemies):
        ex, ey, ez, phase = e
        dx = player_pos[0] - ex
        dy = player_pos[1] - ey
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            ex += ENEMY_SPEED * dx / distance
            ey += ENEMY_SPEED * dy / distance
        phase += 0.1
        scale_factor = 1.0 + 0.2 * math.sin(phase)
        enemies[i] = [ex, ey, ez, phase]

    # Enemy-Player collision
    for e in enemies:
        ex, ey, ez, _ = e
        if math.sqrt((player_pos[0] - ex)**2 + (player_pos[1] - ey)**2) < 20:
            life -= 1
            enemies[enemies.index(e)] = random_enemy()
            print(f"Remaining Player Life: {life}")
            if life <= 0:
                game_over = True
    

    if cheat_mode:
        global enemy_angles
        gun_angle = (gun_angle + 1) % 360  
        
        
        enemy_data = []
        for e in enemies:
            ex, ey, ez, _ = e
            dx = ex - player_pos[0]
            dy = ey - player_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            enemy_angle = math.degrees(math.atan2(dy, dx))
            if enemy_angle < 0:
                enemy_angle += 360
            enemy_data.append([enemy_angle, distance, ex, ey])
        
        
        enemy_data.sort(key=lambda x: x[1])
        
    
        enemy_angles = [data[0] for data in enemy_data]
        
        
        current_time = time.time()
        if enemy_angles and current_time - last_fire_time >= fire_delay:
            shots_fired = False
            
            for target_angle in enemy_angles:
                angle_diff = abs(gun_angle - target_angle)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                    
                
                if angle_diff < ANGLE_THRESHOLD:
                    bullet_start_x = player_pos[0] + 20 * math.cos(math.radians(gun_angle))
                    bullet_start_y = player_pos[1] + 20 * math.sin(math.radians(gun_angle))
                    bullet_start_z = player_pos[2] + 70
                    bullets.append([bullet_start_x, bullet_start_y, bullet_start_z, gun_angle])
                    shots_fired = True
            
           
            if shots_fired:
                last_fire_time = current_time
                
    glutPostRedisplay()


def random_enemy():
    return [random.randint(-GRID_LENGTH+100, GRID_LENGTH-100),
            random.randint(-GRID_LENGTH+100, GRID_LENGTH-100),
            0, random.uniform(0, 2 * math.pi)]

def restart_game():
    global life, bullets_missed, bullets, enemies, player_pos, gun_angle, game_over, score
    life = 5
    bullets_missed = 0
    bullets.clear()
    enemies.clear()
    for _ in range(5):
        enemies.append(random_enemy())
    player_pos = [0, 0, 0]
    gun_angle = 0
    game_over = False
    score = 0

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    draw_grid()

    if not game_over:
        for bullet in bullets:
            draw_bullet(bullet[0], bullet[1], bullet[2])

        for enemy in enemies:
            ex, ey, ez, phase = enemy
            scale_factor = 1.0 + 0.2 * math.sin(phase)
            draw_enemy(ex, ey, ez, scale_factor)

    draw_player()
    if not game_over:
        draw_text(10, 770, f"Player Life Remaining: {life}")
        draw_text(10, 740, f"Game Score: {score}")
        draw_text(10, 710, f"Player Bullet Missed: {bullets_missed}")

    if game_over:
        draw_text(10, 770, f"Game is Over. Your Score is {score}.")
        draw_text(10, 750, "Press 'R' to RESTART the Game.")


    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy 3D Game")

    glEnable(GL_DEPTH_TEST)

    restart_game()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
