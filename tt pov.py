import pygame
from math import sin, cos, tan, atan, floor, sqrt
from random import randint as rand
from random import random as rand_float
from time import time as time_now

show_map = False

score = [0, 0]

player1_inputs = {"forward" : pygame.K_w,
                  "back" : pygame.K_s,
                  "right" : pygame.K_d,
                  "left" : pygame.K_a,
                  "shoot" : pygame.K_q}


player2_inputs = {"forward"  : pygame.K_UP,
                  "back" : pygame.K_DOWN,
                  "right" : pygame.K_RIGHT,
                  "left" : pygame.K_LEFT,
                  "shoot" : pygame.K_m}
 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (50, 50, 50)

REDISH = (150, 120, 120)
BLUEISH = (120, 120, 150)

bullet_colour = (100, 0, 100)

numRays = 101
fov = .75

rectWidth = 50
 
dirs = [[0,1],[1,0],[0,-1],[-1,0]]   #[E,S,W,N]

from timesave import addVecs
from maze_gen import buildmaze

mapsize = 9
world = buildmaze(mapsize-1)
#map modification:
removes = 0
while removes < mapsize:
    coords = [rand(1, mapsize-2),rand(1, mapsize-2)]
    #check that there are two empty neighbours
    if sum(world[addVecs(coords,d)[0]][addVecs(coords,d)[1]] for d in dirs) <= 2:
        world[coords[0]][coords[1]] = 0
        removes += 1
        

worldWidth = len(world)
 
# initialize pygame
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)
WIDTH, HEIGHT = rectWidth * len(world[0])*3, rectWidth * len(world)
screen_size = (WIDTH, HEIGHT)
 
mapWidth = rectWidth * len(world[0]) * 1.5
gameWidth = rectWidth * len(world[0]) * 1
# create a window
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("pygame Test")
 
# clock is used to set a max fps
clock = pygame.time.Clock()

roundVec = lambda x : [round(x[0]), round(x[1])]

def sign(x):
    if x != 0:
        return abs(x)/x
    else:
        return 1

spawn_points = []
def find_spawn():
    found = False
    while not found:
        attempt = [rand(1,mapsize-1),rand(1,mapsize-1)]
        if attempt not in spawn_points and world[attempt[1]][attempt[0]] == 0:
            found = True
    spawn_points.append(attempt)
    return [(attempt[0]+.5)*rectWidth, (attempt[1]+.5)*rectWidth]
        
        
        
class Player():
    def __init__(self, controls, draw_screen = False, screen_offset=0):
        self.pos = find_spawn()
        self.speed = 1.2
        self.rotationSpeed = .058
        self.dir = rand_float() * 10
        self.length = 50
        self.radius = .2
        self.inputs = controls
        self.commands = {}
        self.screen_offset=screen_offset
        self.draw_screen = draw_screen
        #still need to add this to the draw
        self.height = 140
        self.bullet_speed=2
        self.last_fired = 0
        self.cooldown = 2

    def update(self):
        self.commands["forward"] = keys[self.inputs["forward"]]
        self.commands["backwards"] = keys[self.inputs["back"]]
        self.commands["left"] = keys[self.inputs["left"]]
        self.commands["right"] = keys[self.inputs["right"]]
        self.commands["shoot"] = keys[self.inputs["shoot"]]

        #shoot bullet
        if self.commands["shoot"] and time_now() - self.last_fired > self.cooldown:
            self.last_fired = time_now()
            bullets.append(
                Bullet(self.pos, self.bullet_speed, self.dir, time_now())
                )

        #death
        for bullet in bullets:
            if time_now() - bullet.birth_time > .4:
                if (self.pos[0] - bullet.pos[0])**2 + (self.pos[1] - bullet.pos[1])**2 < ((self.radius + bullet.radius) * rectWidth)**2:
                    score[self.opp_index] += 1
                    reset_round()

        #collisions
        fb = self.commands["forward"]-self.commands["backwards"]
        location = [floor(self.pos[0] / rectWidth),
 floor(self.pos[1] / rectWidth)]
        no_move = [0, 0]
        for d in dirs[::-1]:
            location2 = [floor(self.pos[0] / rectWidth + d[0]*self.radius),
 floor(self.pos[1] / rectWidth + d[1]*self.radius)]
            if show_map:
                pygame.draw.circle(screen, BLUEISH, [(self.pos[0] / rectWidth + d[0]*self.radius)*rectWidth,
                                                 (self.pos[1] / rectWidth + d[1]*self.radius)*rectWidth], 4)
            if world[location2[1]][location2[0]] == 1:
                for i in d:
                    if d[i]:
                        no_move[i] = d[i]
                        
        #movement
        if no_move[0] != sign(fb  * sin(self.dir)):
            self.pos[0] += fb  * sin(self.dir) * self.speed
        if no_move[1] != sign(fb * cos(self.dir)):
            self.pos[1] += fb  * cos(self.dir) * self.speed
        if self.commands["left"]:
            self.dir += self.rotationSpeed
        if self.commands["right"]:
            self.dir -= self.rotationSpeed
            

        # raycasting
        location = [floor(self.pos[0] / rectWidth),
                    floor(self.pos[1] / rectWidth)]

        pos = roundVec(self.pos)

        rays_one_side = int((numRays - 1) / 2)
        for ray in range(-rays_one_side, rays_one_side):

            to_draw = []

            fractionalAngle = fov/((numRays-1)/2) * ray
            finalAngle = self.dir - fractionalAngle

            x, y = [self.pos[0] / rectWidth,
                           self.pos[1] / rectWidth]
                    
            xi, yi = x + sin(finalAngle) ,y + cos(finalAngle)

            m = (y - yi) / (x - xi) if x - xi != 0 else 10**10

            c = y - m * x
            
            # up or down
            UoD = int(sign(cos(finalAngle)))
            # left or right
            LoR = int(sign(sin(finalAngle)))
            
            # tb collide
            collide = False
            y = floor(y)
            if UoD == -1:
                y += 1
            while not collide:
                y += UoD
                x = (y - c) / m

                if 0 <= x < worldWidth and 0 <= y < worldWidth:
                    if world[y if UoD == 1 else y - 1][floor(x)] == 1:
                        collide = True
                else:
                    collide = True
            y_collide = [x, y]
            
            # lr collide
            x, y = [self.pos[0] / rectWidth,
                           self.pos[1] / rectWidth]
            
            collide = False
            x = floor(x)
            if LoR == -1:
                x += 1
            while not collide:
                x += LoR
                y = m*x + c

                if 0 <= x < worldWidth and 0 <= y < worldWidth:
                    if world[floor(y)][x if LoR == 1 else x - 1] == 1:
                        collide = True
                else:
                    collide = True
            x_collide = [x, y]

            x, y = [self.pos[0] / rectWidth,
                           self.pos[1] / rectWidth]
            if (x-x_collide[0])**2 + (y-x_collide[1])**2 < (x-y_collide[0])**2 + (y-y_collide[1])**2:
                collide = x_collide
                wall_colour = BLUEISH
            else:
                collide = y_collide
                wall_colour = REDISH
            if show_map:
                pygame.draw.line(screen, RED, pos, [collide[0] * rectWidth,
                                                collide[1] * rectWidth])

            player_pos = players[self.opp_index].pos
            player_pos = [player_pos[0]/rectWidth,
                                   player_pos[1]/rectWidth]

            #bullet view
            for bullet in bullets:
                bullet_pos = [bullet.pos[0]/rectWidth,
                                      bullet.pos[1]/rectWidth]
                p_collide = self.intersect_circle(m, c, bullet_pos[0],  bullet_pos[1], bullet.radius)
                if p_collide and self.check_in_view([x, y], collide, p_collide):
                    dist = self.get_screen_dist([x,y], p_collide, fractionalAngle)
                    if dist != 0:
                        barHeight = bullet.view_height/dist
                    else:
                        barHeight = HEIGHT
                    to_draw.append({'distance' : dist, 'barHeight' : barHeight, 'colour' : bullet_colour})
                

            #player view
            p_collide = self.intersect_circle(m, c, player_pos[0],  player_pos[1], self.radius) #technically should use the radius of the other player but yeah ik theyre the same
            if p_collide and self.check_in_view([x, y], collide, p_collide):
                dist = self.get_screen_dist([x,y], p_collide, fractionalAngle)
                if dist != 0:
                    barHeight = self.height/dist
                else:
                    barHeight = HEIGHT
                to_draw.append({'distance' : dist, 'barHeight' : barHeight, 'colour' : (100,100,0)})

            if self.draw_screen:
                dist = self.get_screen_dist([x, y], collide, fractionalAngle)
    
                barSize = gameWidth / numRays
                if dist != 0:
                    barHeight = 200/dist
                else:
                    barHeight = HEIGHT + 100
                to_draw.append({'distance' : dist, 'barHeight' : barHeight, 'colour' : wall_colour})

                #sort by height

                to_draw = sorted(to_draw, key = lambda d : d['distance'])[::-1]

                max_height = 0
                for bar in to_draw:
                    pygame.draw.rect(screen, bar['colour'], [self.screen_offset + (ray+rays_one_side) * barSize, (screen_size[1] - bar['barHeight'])/2,
                                                            barSize+1, bar['barHeight']])
                    if bar['barHeight'] > max_height:
                        max_height = bar['barHeight']
                pygame.draw.rect(screen, GRAY, [self.screen_offset + (ray+rays_one_side) * barSize, (screen_size[1] + max_height)/2,
                                                            barSize+1, (screen_size[1] - max_height)/2])
                

                self.draw()
                 
    def intersect_circle(self, m, c, a, b, r):
        x, y = [self.pos[0] / rectWidth,
                           self.pos[1] / rectWidth]
                    
        a_q = 1+m**2
        b_q = 2 * ( m * c - a - b * m )
        c_q = c**2 - 2 * b * c - r**2 + a**2 + b**2

        discriminant = b_q**2 - 4 * a_q * c_q

        if discriminant >= 0:
            sqrt_discriminant = sqrt(discriminant)
            x1 = ( -b_q + sqrt_discriminant) / ( 2 * a_q )
            y1 = m * x1 + c
            x2 = ( -b_q - sqrt_discriminant) / ( 2 * a_q )
            y2 = m * x2 + c

            if (x-x1)**2 + (y-y1)**2 < (x-x2)**2 + (y-y2)**2:
                p_collide = [x1,y1]
            else:
                p_collide = [x2,y2]
            return p_collide
        return False

    def get_screen_dist(self, a,b, angle):
        dist = sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2) * cos(angle)
        return dist

    def check_in_view(self, pos, r_collide, p_collide):
        return min(pos[0], r_collide[0]) <= p_collide[0] <= max(pos[0], r_collide[0]) and min(pos[1], r_collide[1]) <= p_collide[1] <= max(pos[1], r_collide[1])

    def draw(self):
        pos = roundVec(self.pos)
        #crosshair
        screen_center = [self.screen_offset + gameWidth/2, HEIGHT/2]
        c_width, c_height = 20, .5
        gap = 7
        gray = (180, 180, 180)
        pygame.draw.rect(screen, gray, [screen_center[0] - c_width, screen_center[1] - c_height, c_width - gap, c_height * 2])
        pygame.draw.rect(screen, gray, [screen_center[0] + gap, screen_center[1] - c_height, c_width - gap, c_height * 2])
        pygame.draw.rect(screen, gray, [screen_center[0] - c_height, screen_center[1] - c_width, c_height * 2, c_width - gap])
        pygame.draw.rect(screen, gray, [screen_center[0] - c_height, screen_center[1] + gap, c_height * 2, c_width - gap])
    

class Bullet:
    def __init__(self, pos, speed, angle, birth_time):
        self.pos = pos
        self.vel = [sin(angle)*speed,
                        cos(angle)*speed]
        self.radius = .05
        self.birth_time = birth_time
        self.lifespan = 8
        self.view_height = 60

    def update(self):
        self.pos = addVecs(self.pos, self.vel)

        no_move = [0, 0]
        for d in dirs[::-1]:
            location2 = [floor(self.pos[0] / rectWidth + d[0]*self.radius),
 floor(self.pos[1] / rectWidth + d[1]*self.radius)]
            if show_map:
                pygame.draw.circle(screen, BLUEISH, [(self.pos[0] / rectWidth + d[0]*self.radius)*rectWidth,
                                                 (self.pos[1] / rectWidth + d[1]*self.radius)*rectWidth], 4)
            if world[location2[1]][location2[0]] == 1:
                for i in d:
                    if d[i]:
                        self.vel[i] *= -1 


        self.draw()

    def draw(self):
        if show_map:
            pygame.draw.circle(screen, bullet_colour, self.pos, self.radius * rectWidth)


def reset_round():
    spawn_points = []
    for player in players:
        player.pos = find_spawn()
        player.last_fired = 0
    #for bullet in bullets:
    #    bullets.pop(0)
    global bullets
    bullets = []
            

        
players = [
                Player(player1_inputs, True, mapsize*rectWidth*show_map),
                Player(player2_inputs, True, gameWidth + mapsize*rectWidth)
                ]

#jank i know its late
players[0].opp_index = 1
players[1].opp_index = 0

bullets = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
     
    #clear the screen
    screen.fill(BLACK)
     
    # draw to the screen
    if show_map:
        for y, level in enumerate(world):
            for x, block in enumerate(level):
                if block == 1:
                    pygame.draw.rect(screen, WHITE, [x * rectWidth + 1, y * rectWidth + 1,
                                              rectWidth - 2, rectWidth - 2])
            
    #score
    if not show_map:
        text_surface = my_font.render(f'{score[0]} - {score[1]}', False, (150, 150, 150))
        screen.blit(text_surface, ((WIDTH - text_surface.get_width())/2,(HEIGHT - text_surface.get_height())/2))
        for i, each_score in enumerate(score):
            if each_score == 3:
                print(f'Player {i} wins!')
                running = False
            
    for player in players:
        player.update()

    for bullet in bullets:
        bullet.update()
        if bullet.birth_time + bullet.lifespan < time_now():
            bullets.remove(bullet)


    pygame.display.flip()

    # how many updates per second
    clock.tick(60)
 
pygame.quit()
