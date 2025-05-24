from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

# Window setup
width, height = 1000, 800

# Player settings
player_pos = [0, 0, -400]
player_size = 20
is_jumping = False
jump_velocity = 0
gravity = -0.5

# Game settings
camera_pos = [0, 200, -700]  
camera_angle = 0  
MAX_OBSTACLES = 30
game_over = False
score = 0
lives = 5
last_score_checkpoint = 0
minimum_to_span = 1

# Obstacle settings
obstacles = []
obstacle_speed = 0
spawn_interval = 600
frame_count = 0

# Collectible dots
dots = []

#For 2x
powerups = []
double_score = False
powerup_end_time = 0

#For life
life_powerups = []

#For decreasing life
minus_powerups = []

#For bullets

bullets = 5
bullet_powerups = []
fired_bullets = []

#cheat mode
cheat_mode = False
cheat_start_time = 0
cheat_code_buffer = ""

first_person = False

#night mode
night_mode = False
sky_transition = 0.0  # 0=day 1=night
sun_to_moon = False

transition_direction = 0


def draw_ground():
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-300, -10, 1000)
    glVertex3f(300, -10, 1000)
    glVertex3f(300, -10, -1000)
    glVertex3f(-300, -10, -1000)
    glEnd()

def draw_player():
    glPushMatrix()

    if game_over:
        # lying on the ground
        glTranslatef(player_pos[0], player_pos[1], player_pos[2] + 50)
        glRotatef(90, 0, 0, 1)
    else:
        # Normal
        glTranslatef(player_pos[0], player_pos[1] + 20, player_pos[2] + 50)
        glRotatef(-90, 1, 0, 0)

    glScalef(0.7, 0.7, 0.7)

    glColor3f(0.5, 0.7, 0.2)
    glPushMatrix()
    glScalef(0.8, 0.4, 1.2)
    glutSolidCube(30)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, 25)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 8, 20, 20)
    glPopMatrix()

    # Left leg
    glPushMatrix()
    glTranslatef(10, 0, -35)
    glColor3f(0, 0, 1)
    glScalef(0.4, 0.4, 1.8)
    glutSolidCube(18)
    glPopMatrix()

    # Right leg
    glPushMatrix()
    glTranslatef(-10, 0, -35)
    glColor3f(0, 0, 1)
    glScalef(0.4, 0.4, 1.8)
    glutSolidCube(18)
    glPopMatrix()

    # Left arm
    glPushMatrix()
    glTranslatef(10, -5, 20)
    glRotatef(90, 1, 0, 0)
    glColor3f(1, 0.8, 0.6)
    gluCylinder(gluNewQuadric(), 4, 4, 25, 10, 10)
    glPopMatrix()

    # Right arm
    glPushMatrix()
    glTranslatef(-10, -5, 20)
    glRotatef(90, 1, 0, 0)
    glColor3f(1, 0.8, 0.6)
    gluCylinder(gluNewQuadric(), 4, 4, 25, 10, 10)
    glPopMatrix()

    if bullets > 0:
        glPushMatrix()
        glTranslatef(0, -5, 15)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.7, 0.7, 0.7)
        gluCylinder(gluNewQuadric(), 4, 4, 25, 10, 10)
        glPopMatrix()

    glPopMatrix()

    

def draw_obstacles():
    glColor3f(1, 0, 0)
    for obs in obstacles:
        glPushMatrix()
        glTranslatef(obs[0], obs[1] + player_size / 2, obs[2])
        glutSolidCube(player_size)
        glPopMatrix()

def draw_dots():
    glColor3f(1, 1, 0)
    for dot in dots:
        glPushMatrix()
        glTranslatef(dot[0], dot[1], dot[2])
        gluSphere(gluNewQuadric(), 5, 10, 10)
        glPopMatrix()

def draw_powerups():
    #  2x score power-ups
    for p in powerups:
        glPushMatrix()
        glColor3f(1, 1, 1)
        glRasterPos3f(p[0], p[1] + 10, p[2])  # Position above powerup
        for ch in "2x":
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        glPopMatrix()

    #  life power-ups (+)
    for p in life_powerups:
        glPushMatrix()
        glColor3f(1, 1, 1)  # Use a different color for life power-ups
        glRasterPos3f(p[0], p[1] + 10, p[2])  # Position above powerup
        for ch in "+":
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        glPopMatrix()

    #   life reduction power-ups (-)
    for p in minus_powerups:
        glPushMatrix()
        glColor3f(1, 1, 1)  # Use a color for life reduction power-ups (same as life power-ups)
        glRasterPos3f(p[0], p[1] + 10, p[2])  # Position above powerup
        for ch in "-":
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        glPopMatrix()

    #   bullet power-ups
    for p in bullet_powerups:
        glPushMatrix()
        glColor3f(1, 1, 1)  # White for bullet power-ups
        glRasterPos3f(p[0], p[1] + 10, p[2])
        for ch in "B":
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        glPopMatrix()

def draw_fired_bullets():
    glColor3f(1, 1, 1)
    for bullet in fired_bullets:
        glPushMatrix()
        glTranslatef(bullet[0], bullet[1], bullet[2])
        gluSphere(gluNewQuadric(), 3, 10, 10)
        glPopMatrix()



def update_obstacles():
    global obstacles, obstacle_speed, score
    update_obstacle_speed()
    for obs in obstacles:
        obs[2] -= obstacle_speed
    obstacles = [obs for obs in obstacles if obs[2] > -600]

def update_dots():
    global dots
    for dot in dots:
        dot[2] -= obstacle_speed
    dots = [dot for dot in dots if dot[2] > -600]

def update_obstacle_speed():
    global obstacle_speed, minimum_to_span, score, MAX_OBSTACLES, spawn_interval,last_score_checkpoint
    speed_increase_factor = 0.05 
    obstacle_speed = 0.5 + (score // 10) * speed_increase_factor
    if score > 0 and (score > last_score_checkpoint + 10 or score % 10 == 0):
        MAX_OBSTACLES = 30 + (score // 10)
        if spawn_interval > 200:
            spawn_interval= 600- (20 * (score // 10))
        if minimum_to_span<5:
            minimum_to_span = 1 + (score//20)
        if score % 10 == 0:
            last_score_checkpoint = score   
        else:
            last_score_checkpoint = (score // 10) * 10



    
    max_speed = 5
    if obstacle_speed > max_speed:
        obstacle_speed = max_speed


def update_powerups():
    global powerups, life_powerups, minus_powerups , bullet_powerups
    # Updating 2x score power-ups
    for p in powerups:
        p[2] -= obstacle_speed
    # Updating life power-ups
    for p in life_powerups:
        p[2] -= obstacle_speed
    for p in minus_powerups:
        p[2] -= obstacle_speed
    # Updating bullet power-ups
    for p in bullet_powerups:
        p[2] -= obstacle_speed

    # Removing power-ups that are out of bounds
    powerups = [p for p in powerups if p[2] > -600]
    life_powerups = [p for p in life_powerups if p[2] > -600]
    minus_powerups = [p for p in minus_powerups if p[2] > -600]
    bullet_powerups = [p for p in bullet_powerups if p[2] > -600]

def is_lane_occupied(lane, z, objects, z_margin=40):
    for obj in objects:
        if obj[0] == lane and abs(obj[2] - z) < z_margin:
            return True
    return False


def spawn_obstacle():
    all_objects = obstacles + dots + powerups + life_powerups + minus_powerups + bullet_powerups
    
    available_lanes = [-150, -100, -50, 0, 50, 100, 150]
    random.shuffle(available_lanes)
    
    z_pos = 800
    obstacle_placed = False
    
    for lane in available_lanes:
        if not is_lane_occupied(lane, z_pos, all_objects):
            obstacles.append([lane, 0, z_pos])
            obstacle_placed = True
            break
    
    if not obstacle_placed:
        return
        
    safe_lanes = [l for l in available_lanes if l != obstacles[-1][0]]
    if not safe_lanes:
        return
        
    # spawn dot
    if random.random() < 0.7:
        all_objects = obstacles + dots + powerups + life_powerups + minus_powerups + bullet_powerups
        dot_lanes = safe_lanes.copy()
        random.shuffle(dot_lanes)
        
        for dot_lane in dot_lanes:
            if not is_lane_occupied(dot_lane, z_pos, all_objects):
                dots.append([dot_lane, 10, z_pos])
                break
    
    # spawn powerup
    if random.random() < 0.1:
        all_objects = obstacles + dots + powerups + life_powerups + minus_powerups + bullet_powerups
        powerup_lanes = safe_lanes.copy()
        random.shuffle(powerup_lanes)
        
        for powerup_lane in powerup_lanes:
            if not is_lane_occupied(powerup_lane, z_pos, all_objects):
                r = random.random()
                if r < 0.33:
                    powerups.append([powerup_lane, 10, z_pos])  # 2x powerup
                elif r < 0.66:
                    bullet_powerups.append([powerup_lane, 10, z_pos])  # Bullet powerup
                elif r < 0.8:
                    life_powerups.append([powerup_lane, 10, z_pos])  # Life powerup
                else:
                    minus_powerups.append([powerup_lane, 10, z_pos])  # Life reduction powerup
                break




# def spawn_dot(lane):
#     z_pos = 800
#     if (
#         not is_lane_occupied(lane, z_pos, obstacles) and
#         not is_lane_occupied(lane, z_pos, powerups + bullet_powerups + life_powerups + minus_powerups)
#     ):
#         dots.append([lane, 10, z_pos])


# def spawn_powerup(preferred_lane=None):
#     z_pos = 800
#     all_lanes = [-150, -100, -50, 0, 50, 100, 150]

#     if preferred_lane is not None:
#         lanes_to_try = [preferred_lane] + [l for l in all_lanes if l != preferred_lane]
#     else:
#         lanes_to_try = all_lanes[:]

#     random.shuffle(lanes_to_try)

#     for lane in lanes_to_try:
#         if (
#             not is_lane_occupied(lane, z_pos, obstacles) and
#             not is_lane_occupied(lane, z_pos, dots) and
#             not is_lane_occupied(lane, z_pos, powerups + bullet_powerups + life_powerups + minus_powerups)
#         ):
#             r = random.random()
#             if r < 0.33:
#                 powerups.append([lane, 10, z_pos]) 
#             elif r < 0.66:
#                 bullet_powerups.append([lane, 10, z_pos])
#             elif r < 0.8:
#                 life_powerups.append([lane, 10, z_pos])
#             else:
#                 minus_powerups.append([lane, 10, z_pos])
#             return 




        

def update_jump():
    global player_pos, jump_velocity, is_jumping
    if is_jumping:
        jump_velocity += gravity
        player_pos[1] += jump_velocity
        if player_pos[1] <= 0:
            player_pos[1] = 0
            is_jumping = False
            jump_velocity = 0

def update_fired_bullets():
    global fired_bullets, obstacles, score

    updated_bullets = []

    for bullet in fired_bullets:
        bullet[2] += 1.5  # Moving bullet forward

        bullet_x, bullet_z = bullet[0], bullet[2]
        hit_obstacle = None
        
        for obs in obstacles:
            obs_x, obs_z = obs[0], obs[2]
            
            # collision check: between bullet and obstacle
            if abs(bullet_x - obs_x) < player_size * 0.5 and bullet_z >= obs_z - player_size * 0.5:
                hit_obstacle = obs
                break

        if hit_obstacle:
            obstacles.remove(hit_obstacle)
            score += 5
            print(f"Hit! Score: {score}")
        else:
            if bullet_z < 800:  # Keep bullets within a specific range
                updated_bullets.append(bullet)

    fired_bullets = updated_bullets



def check_collision():
    global game_over, lives, fired_bullets, obstacles, score

    # --- Player vs Obstacle Collision ---
    player_x_min = player_pos[0] - player_size / 2
    player_x_max = player_pos[0] + player_size / 2
    player_y_min = player_pos[1]
    player_y_max = player_pos[1] + player_size
    player_z_min = player_pos[2] + 50 - player_size / 2
    player_z_max = player_pos[2] + 50 + player_size / 2

    remaining_obstacles = []

    for obs in obstacles:
        obs_x_min = obs[0] - player_size / 2
        obs_x_max = obs[0] + player_size / 2
        obs_y_min = obs[1]
        obs_y_max = obs[1] + player_size
        obs_z_min = obs[2] - player_size / 2
        obs_z_max = obs[2] + player_size / 2

        # player collision with obstacle
        player_hit = (
            player_x_min < obs_x_max and player_x_max > obs_x_min and
            player_y_min < obs_y_max and player_y_max > obs_y_min and
            player_z_min < obs_z_max and player_z_max > obs_z_min
        )

        if player_hit:
            if not cheat_mode: 
                lives -= 1
                print(f"Hit! Lives left: {lives}")
                if lives <= 0:
                    game_over = True
                    print("Game Over!")
            else:
                score+=1
        else:
            remaining_obstacles.append(obs)  # removing obstacle
    obstacles = remaining_obstacles

def check_dot_collection():
    global dots, score
    new_dots = []
    for dot in dots:
        if abs(player_pos[0] - dot[0]) < player_size and abs(player_pos[2] - dot[2]) < 60:
            gained = 2 if double_score else 1
            score += gained
            print(f"Score +{gained}: {score}")
        else:
            new_dots.append(dot)
    dots = new_dots


def keyboardListener(key, x, y):
    global player_pos, is_jumping, jump_velocity, bullets
    global cheat_mode, cheat_start_time, cheat_code_buffer, first_person, night_mode,sun_to_moon,sky_transition, transition_direction

    if not game_over:
        if key == b'd':
            player_pos[0] -= 10
            if player_pos[0] < -150:
                player_pos[0] = -150
        elif key == b'a':
            player_pos[0] += 10
            if player_pos[0] > 150:
                player_pos[0] = 150
        elif key == b' ' and not is_jumping:
            is_jumping = True
            jump_velocity = 10
        elif key == b'w' and bullets > 0:
            bullets -= 1

            if first_person:
            # Firing position in first-person view
                eye_x = player_pos[0]
                eye_y = player_pos[1] 
                eye_z = player_pos[2] + 80
                fired_bullets.append([eye_x, eye_y, eye_z])
            else:
            # third-person shooting
                fired_bullets.append([player_pos[0], player_pos[1]+40, player_pos[2]+50])

            print(f"Fired! Bullets left: {bullets}")

        elif key == b'f': 
            first_person = not first_person
            view_mode = "First-Person" if first_person else "Third-Person"
            print(f"Switched to {view_mode} View")

            
        
        elif key == b'n':
            if not night_mode:
                night_mode = True
                sun_to_moon = True
                transition_direction = 1 
                print("Night mode activated!")
            else:
                night_mode = False
                transition_direction = -1  # Reset back to day
                print("Day mode activated!")
        elif key == b'+':
            if camera_pos[2] < player_pos[2] - 200:
                camera_pos[2] += 10  # Zoom in (move forward)
        elif key == b'-':
            camera_pos[2] -= 10

        # Cheat code detecting (type 'pop' to activate)
        try:
            char = key.decode('utf-8')
            cheat_code_buffer += char
            cheat_code_buffer = cheat_code_buffer[-3:]  # keep last 3 characters only
            if cheat_code_buffer == "pop" and not cheat_mode:
                cheat_mode = True
                cheat_start_time = time.time()
                print("Cheat mode activated for 46 seconds!")
        except Exception as e:
            pass 

    else:
        if key == b'r':
            restart_game()
def special_key_handler(key, x, y):
    global camera_pos, camera_angle
    cx, cy, cz = camera_pos
    if key == GLUT_KEY_UP:
        cy += 10
    elif key == GLUT_KEY_DOWN:
        cy -= 10
    elif key == GLUT_KEY_RIGHT:
        camera_angle -= 2
    elif key == GLUT_KEY_LEFT:
        camera_angle += 2
    camera_pos = [cx, cy, cz]



def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, width / height, .01, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person:
        # camera at player head position, looking forward along Z
        eye_x = player_pos[0]
        eye_y = player_pos[1] + 50  
        eye_z = player_pos[2] + 40
        center_x = eye_x
        center_y = eye_y 
        center_z = eye_z + 100  

        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 1, 0)
    else:
        #third-person view
        cx, cy, cz = camera_pos
        rad = math.radians(camera_angle)
        center_x = cx + 100 * math.sin(rad)
        center_y = cy
        center_z = cz + 100 * math.cos(rad)
        gluLookAt(cx, cy, cz, center_x, center_y, center_z, 0, 1, 0)



def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def draw_first_person_hands_and_gun():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluPerspective(70, width / height, 0.01, 2000)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # --- LEFT HAND ---
    glPushMatrix()
    glTranslatef(-0.15, -0.3, -0.6)
    glRotatef(110, 1, 0, 0)
    glColor3f(1.0, 0.8, 0.6)
    gluCylinder(gluNewQuadric(), 0.05, 0.05, 0.25, 10, 10)
    glTranslatef(0, 0, 0.25)
    gluSphere(gluNewQuadric(), 0.06, 10, 10) 
    glPopMatrix()

    # --- RIGHT HAND ---
    glPushMatrix()
    glTranslatef(0.15, -0.3, -0.6)
    glRotatef(110, 1, 0, 0)
    glColor3f(1.0, 0.8, 0.6)
    gluCylinder(gluNewQuadric(), 0.05, 0.05, 0.25, 10, 10)
    glTranslatef(0, 0, 0.25)
    gluSphere(gluNewQuadric(), 0.06, 10, 10)
    glPopMatrix()

    # --- GUN (CENTERED BETWEEN HANDS) ---
    glPushMatrix()
    glTranslatef(0.0, -0.3, -0.6)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.7, 0.7, 0.7)
    gluCylinder(gluNewQuadric(), 0.04, 0.04, 0.5, 10, 10) 
    glPopMatrix()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)




def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, width, height)
    setup_camera()
    draw_sky_and_sun()

    draw_ground()
    if first_person:
        draw_first_person_hands_and_gun()
    else:
        draw_player()
    draw_obstacles()
    draw_dots()
    draw_powerups()
    draw_fired_bullets()


    # Showing score on top-left
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 0)
    draw_text(10, height - 30, f"Score: {score}")
    draw_text(10, height - 60, f"Lives: {lives}")
    draw_text(10, height - 90, f"Bullets: {bullets}")
    if cheat_mode:
        seconds_left = int(46 - (time.time() - cheat_start_time))
        if seconds_left < 0:
            seconds_left = 0
        glColor3f(1, 0, 1)  
        draw_text(10, height - 120, f"CHEAT MODE ACTIVE! {seconds_left}s left")
    if game_over:
        glColor3f(1, 1, 1)
        draw_text(width // 2 - 50, height // 2, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(width // 2 - 90, height // 2 - 40, "Press 'r' to Restart", GLUT_BITMAP_HELVETICA_18)
    # draw_text(10, height-200 , f"Obstacle_Speed: {obstacle_speed}")
    # draw_text(10, height-230 , f"Max_Obstacles: {MAX_OBSTACLES}")
    # draw_text(10, height-260 , f"Spawn_Interval: {spawn_interval}")
    # draw_text(10, height-280, f"Minimum to span {minimum_to_span}")
    if not game_over and double_score:
        seconds_left = int(powerup_end_time - time.time())
        if seconds_left < 0:
            seconds_left = 0
        glColor3f(0, 1, 1)
        if not cheat_mode:
            draw_text(10, height - 120, f"2× ACTIVE! {seconds_left}s left")
        else:
            draw_text(10, height - 150, f"2× ACTIVE! {seconds_left}s left (CHEAT MODE)")
    
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()

def check_powerup_collection():
    global powerups, life_powerups, minus_powerups, double_score, powerup_end_time, lives, game_over, bullets, bullet_powerups
    new_powerups = []
    new_life_powerups = []
    new_minus_powerups = []
    new_bullet_powerups = []



    # 2x check
    for p in powerups:
        distance_x = abs(player_pos[0] - p[0])
        distance_z = abs(player_pos[2] - p[2])
        distance_y = abs(player_pos[1] - p[1])
        
        if distance_x < player_size and distance_z < 50 and distance_y < player_size:
            double_score = True
            powerup_end_time = time.time() + 30  # 30 seconds from now
            print("2× Activated!")
        else:
            new_powerups.append(p)
    
    # + check
    for p in life_powerups:
        distance_x = abs(player_pos[0] - p[0])
        distance_z = abs(player_pos[2] - p[2])
        distance_y = abs(player_pos[1] - p[1])
        
        if distance_x < player_size and distance_z < 50 and distance_y < player_size:
            lives += 1
            print(f"Life +1! Lives left: {lives}")
        else:
            new_life_powerups.append(p)

    # - check
    for p in minus_powerups:
        distance_x = abs(player_pos[0] - p[0])
        distance_z = abs(player_pos[2] - p[2])
        distance_y = abs(player_pos[1] - p[1])
        
        if distance_x < player_size and distance_z < 50 and distance_y < player_size:
            if not cheat_mode:
                lives -= 1
                if lives == 0:
                    game_over = True
                    print(f"Life -1! Lives left: {lives}")
                    print("Game Over!")
                else:
                    print(f"Life -1! Lives left: {lives}")
        else:
            new_minus_powerups.append(p)

    # bullet power-up check
    for p in bullet_powerups:
        distance_x = abs(player_pos[0] - p[0])
        distance_z = abs(player_pos[2] - p[2])
        distance_y = abs(player_pos[1] - p[1])
        
        if distance_x < player_size and distance_z < 50 and distance_y < player_size :
            bullets += 1
            print(f"Collected Bullet! Bullets: {bullets}")
        else:
            new_bullet_powerups.append(p)

    # power-up list update
    powerups = new_powerups
    life_powerups = new_life_powerups
    minus_powerups = new_minus_powerups
    bullet_powerups = new_bullet_powerups

def restart_game():
    global player_pos, is_jumping, jump_velocity, gravity
    global camera_pos, camera_angle
    global MAX_OBSTACLES, game_over, score, lives
    global obstacles, dots, powerups, double_score, powerup_end_time, spawn_interval
    global life_powerups, minus_powerups, bullets, bullet_powerups, fired_bullets
    global cheat_mode, cheat_start_time, cheat_code_buffer
    global first_person, night_mode, sky_transition, sun_to_moon, transition_direction
    global frame_count

    player_pos = [0, 0, -400]
    is_jumping = False
    jump_velocity = 0
    camera_pos = [0, 200, -700]
    camera_angle = 0
    MAX_OBSTACLES = 30
    game_over = False
    score = 0
    lives = 5
    spawn_interval = 500

    obstacles.clear()
    dots.clear()
    powerups.clear()
    life_powerups.clear()
    minus_powerups.clear()
    bullet_powerups.clear()
    fired_bullets.clear()

    bullets = 5
    double_score = False
    powerup_end_time = 0

    cheat_mode = False
    cheat_start_time = 0
    cheat_code_buffer = ""

    first_person = False
    night_mode = False
    sky_transition = 0.0
    sun_to_moon = False
    transition_direction = 0

    frame_count = 0

    print("Game restarted.")


def draw_sky_and_sun():

    r = 0.15 - (0.1 * sky_transition)   
    g = 0.5 - (0.4 * sky_transition)  
    b = 1 - (0.5 * sky_transition) 
    glClearColor(r, g, b, 1.0)
    glColor3f(r, g, b)

    glBegin(GL_QUADS)
    glVertex3f(-1000, 500, -1000)
    glVertex3f(1000, 500, -1000)
    glVertex3f(1000, 500, 1000)
    glVertex3f(-1000, 500, 1000)
    glEnd()

   
    sun_x, sun_y, sun_z = 300, 400, 1000

    glPushMatrix()
    #from yellow sun to pale moon
    sun_r = (1 - sky_transition) * 1.0 + sky_transition * 0.9
    sun_g = (1 - sky_transition) * 1.0 + sky_transition * 0.9
    sun_b = (1 - sky_transition) * 0.0 + sky_transition * 1.0
    glColor3f(sun_r, sun_g, sun_b)
    glTranslatef(sun_x, sun_y, sun_z)
    gluSphere(gluNewQuadric(), 50, 30, 30)
    glPopMatrix()

 
    glLineWidth(2)
    glColor3f(sun_r, sun_g, sun_b)
    glBegin(GL_LINES)
    num_rays = 16
    ray_length = 80 * (1 - sky_transition)  
    for i in range(num_rays):
        angle = i * (360 / num_rays)
        rad = math.radians(angle)
        dx = ray_length * math.cos(rad)
        dy = ray_length * math.sin(rad)
        glVertex3f(sun_x, sun_y, sun_z)
        glVertex3f(sun_x + dx, sun_y + dy, sun_z)
    glEnd()





def idle():
    global frame_count, minimum_to_span, powerup_timer, double_score, cheat_mode, cheat_start_time, sky_transition, sun_to_moon,transition_direction
    if not game_over:
        update_jump()
        update_obstacles()
        update_dots()
        check_collision()
        check_dot_collection() 
        check_powerup_collection()
        update_fired_bullets()

        if double_score and time.time() >= powerup_end_time:
            double_score = False
            print("2× Expired!")
        if cheat_mode and time.time() - cheat_start_time >= 46:
            cheat_mode = False
            print("Cheat mode expired.")
        transition_speed = 0.005  # for smooth transition

        if transition_direction == 1 and sky_transition < 1.0:
            sky_transition += transition_speed
            if sky_transition >= 1.0:
                sky_transition = 1.0
                transition_direction = 0

        elif transition_direction == -1 and sky_transition > 0.0:
            sky_transition -= transition_speed
            if sky_transition <= 0.0:
                sky_transition = 0.0
                transition_direction = 0




        update_powerups()
        frame_count += 1
        if frame_count % spawn_interval == 0 and len(obstacles) < MAX_OBSTACLES:
            obstacles_to_spawn = min(minimum_to_span, MAX_OBSTACLES - len(obstacles))  # spawn up to 3 at once
            for _ in range(obstacles_to_spawn):
                spawn_obstacle()
    else:
        global dots, powerups, life_powerups, minus_powerups, bullet_powerups
        obstacles.clear()
        dots.clear()
        powerups.clear()
        life_powerups.clear()
        minus_powerups.clear()
        bullet_powerups.clear()
        update_jump()  
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Obstacle Dodger")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(special_key_handler)
    glutMainLoop()

if __name__ == "__main__":
    main()
