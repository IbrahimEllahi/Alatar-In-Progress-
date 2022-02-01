import pygame as pg
from settings import *
from os import path
import json
from random import choice,randint
from math import ceil

pg.init()


WINDOW = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
pg.display.set_caption('Alatar')


sprites = pg.sprite.Group()
obstacles = pg.sprite.Group()
lighting = pg.sprite.Group()


class Particle:
    def __init__(self,**attributes):
        self.attributes = attributes
        self.particles = []
        self.time = 0
        
        self.create_particles(self.attributes['colors'],self.attributes['particle_amount'])

        
    def create_particles(self,colors,amount):

        for i in range(amount):
            x,y = 0,1
            pos = [randint(self.attributes['xy_spawn'][x][0],self.attributes['xy_spawn'][x][1]),randint(self.attributes['xy_spawn'][y][0],self.attributes['xy_spawn'][y][1])]

            size = randint(self.attributes['size_range'][0], self.attributes['size_range'][1])
            self.particles.append([choice(colors),pg.Rect(pos[0],pos[1],size,size),size])


    def draw(self,surface):
        self.time += 1
            
        for particle in self.particles:
            if particle[2] <= 0:
                self.particles.remove(particle)
                if self.time < self.attributes['run_time'] or not self.attributes['run_time']:
                    self.create_particles(self.attributes['colors'],1)
                
            if not self.time % self.attributes['travel_speed']:
                particle[1].x += self.attributes['direction'][0]
                particle[1].y += self.attributes['direction'][1]

            if not self.time % (self.attributes['travel_speed'] * self.attributes['shrink_multiplier']):
                particle[2] -= 1
            
            pos = camera.apply_rect(particle[1])

            pg.draw.circle(surface, particle[0], (pos.x, pos.y), particle[2])


leaves = Particle(run_time = False,direction = [2,1],size_range = (1,2),particle_amount = 200,travel_speed = 1,shrink_multiplier = 1300,colors = [FOREST_GREEN,GREEN],xy_spawn = [(-1000,fullmap.width),(-1000,0)])



class Spritesheet:
    def __init__(self,filename):
        self.filename = filename
        self.sprite_sheet = load_image(filename)
        self.meta_data = self.filename.replace('png', 'json')
        with open(self.meta_data) as f:
            self.data = json.load(f)
    
    def get_sprite(self, x, y, w, h):
        sprite = pg.Surface((w,h))
        sprite.set_colorkey(BLACK)
        sprite.blit(self.sprite_sheet,(0,0),(x, y, w, h))
        return sprite

    def parse_sprite(self, name,transform=(TILESIZE+16,TILESIZE*2)):
        sprite = self.data['frames'][name]['frame']
        x, y, w, h = sprite['x'], sprite['y'], sprite['w'], sprite['h']
        image = scale(self.get_sprite(x,y,w,h),transform)
        return image

sheet = Spritesheet('player_sprite.png')


class Physics:

    def detect_collision(self,direction,entity,entity2=obstacles):
        if direction == 'x':
            hit = pg.sprite.spritecollide(entity, entity2, False)
            if hit:
                if entity.mx > 0:
                    entity.x = hit[0].rect.left - entity.rect.width
                if entity.mx < 0:
                    entity.x = hit[0].rect.right
                
                entity.mx = 0
                entity.rect.x = entity.x
                return True
            
            return False
        
        if direction == 'y':

            hit = pg.sprite.spritecollide(entity, entity2, False)
            if hit:

                if entity.my > 0:
                    entity.y = hit[0].rect.top - entity.rect.height
                    entity.fallvelocity = 0.3
                        

                if entity.my < 0:
                    entity.y = hit[0].rect.bottom

                    if entity.jumping:
                        entity.jumping = False
                        entity.jumpvelocity = JUMP_SPEED_LIMIT

                entity.my = 0
                entity.rect.y = entity.y
                return True
            
            return False

    def gravity(self,entity,platform):

        if not entity.jumping and not self.on_platform(entity,platform):
            entity.fallvelocity += FALL_ACCEL
            entity.my = entity.fallvelocity


    def on_platform(self,entity,platform):
        entity.rect.y += 1
        hit = pg.sprite.spritecollide(entity, platform, False)
        entity.rect.y -= 1
        if hit:

            return True
        return False

        

physics = Physics()




class Player(pg.sprite.Sprite):
    
    def __init__(self, xy = (0,0)):

        pg.sprite.Sprite.__init__(self, sprites)

        self.mx, self.my = 0, 0
        self.x, self.y = [i * TILESIZE for i in xy]
        self.image = sheet.parse_sprite('idle (1).png')
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        self.animate = {
                        'attack1':[sheet.parse_sprite(f'attack1 ({i}).png', (TILESIZE*2,TILESIZE*2))  for i in range(1,9)],
                        'attack2':[sheet.parse_sprite(f'attack2 ({i}).png',(TILESIZE+28,TILESIZE*2))  for i in range(1,9)],
                        'run':    [sheet.parse_sprite(f'run ({i}).png',    (TILESIZE+28,TILESIZE*2))  for i in range(1,9)],
                        'death':  [sheet.parse_sprite(f'death ({i}).png')                             for i in range(1,8)],
                        'fall':   [sheet.parse_sprite(f'fall ({i}).png',(TILESIZE+16, TILESIZE*2+10)) for i in range(1,3)],
                        'jump':   [sheet.parse_sprite(f'jump ({i}).png')                              for i in range(1,3)],
                        'hurt':   [sheet.parse_sprite(f'hurt ({i}).png')                              for i in range(1,5)],
                        'idle':   [sheet.parse_sprite(f'idle ({i}).png')                              for i in range(1,7)]
                        }

        self.fallvelocity = 0.3
        self.jumping = JUMPING
        self.attack_stat = False
        self.frames = { 
                        'run'   :0,
                        'attack1':0,
                        'attack2':0,
                        'idle'  :0,
                        'jump'  :0,
                        'fall'  :0
                        }
        self.attack = False
        self.framecount = 0
        self.jumpvelocity = JUMP_SPEED_LIMIT
        self.direction = 'R'
        self.falling = False

    def movement(self):
        self.mx, self.my = 0, 0

        if self.jumping:
            if self.jumpvelocity >= 0:
                self.jumping = False
                self.jumpvelocity = JUMP_SPEED_LIMIT
                self.my = 0
                return
                
            self.jumpvelocity += JUMP_ACCELDROP
            self.my = self.jumpvelocity
            animate(self,'jump',8)
            

        physics.gravity(self,obstacles)

        
        MOVEMENT = PLAYER_SPEED if physics.on_platform(self,obstacles) else FALL_MOVESPEED


        keys = pg.key.get_pressed()
        RIGHT = keys[pg.K_d] or keys[pg.K_RIGHT]
        LEFT = keys[pg.K_a] or keys[pg.K_LEFT]


        
        if self.attack:
            if animate(self,'attack1',8) == 'Finish':
                self.attack = False
            return

        if RIGHT and LEFT:
            LEFT = False
            RIGHT = False

        if RIGHT:
        
            self.direction = 'R'
            self.mx = MOVEMENT

            if physics.on_platform(self,obstacles):
                animate(self,'run',8)
                self.falling = False
                return

        if LEFT:
            self.direction = 'L'
            self.mx = -MOVEMENT

            if physics.on_platform(self,obstacles):
                animate(self,'run',8)
                self.falling = False
                return

        afk = not LEFT and not RIGHT and not self.jumping and physics.on_platform(self,obstacles) and not player.attack_stat

        if afk:
            self.falling = False
            animate(self,'idle',8)
            return

        if not self.jumping:
            self.falling = True
            animate(self,'fall',8)
            return
        

            
    #Updates player location, collision and camera

    def update(self):
        walk_area = self.x + self.mx + self.rect.width -15 < fullmap.width and self.x + self.mx + 15 > 0
        if walk_area:
            self.x += self.mx

        self.y += self.my

        self.rect.x = self.x
        physics.detect_collision('x',self,obstacles)


        self.rect.y = self.y
        physics.detect_collision('y',self,obstacles)

        camera.update(self)

        

player = Player((1,20))


class Platform(pg.sprite.Sprite):

    def __init__(self, id, xy):
        pg.sprite.Sprite.__init__(self, (sprites, obstacles))
        self.x, self.y = [i * TILESIZE for i in xy]
        self.image = scale(load_image(game.assets['platforms'][id]),(TILESIZE,TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.x, self.y

class Decoration(pg.sprite.Sprite):

    def __init__(self, id, xy):
        pg.sprite.Sprite.__init__(self, sprites)
        self.x, self.y = [i * TILESIZE for i in xy]
        self.image = scale(load_image(game.assets['platforms'][id]),(TILESIZE,TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.x, self.y




class Background:
    def __init__(self,image):
        self.image = scale(load_image(image),(WIDTH,HEIGHT))
        self.rects = [self.image.get_rect()]
        self.scroll_speed = 1
        self.set_scroll()

    def set_scroll(self):
        fit = ceil(fullmap.width/self.rects[0].width) * int(self.scroll_speed)
        x = 0
        for i in range(fit):
            x+= self.rects[0].width
            self.rects.append(pg.Rect(x,0,self.rects[0].width,self.rects[0].height))


    def scroll(self):

        if player.mx < 0 and not camera.freeze:
            for rect in self.rects:
                rect.x += self.scroll_speed
        if player.mx > 0 and not camera.freeze:
            for rect in self.rects:
                rect.x -= self.scroll_speed

        for rect in self.rects:
            WINDOW.blit(self.image,(rect.topleft))
        

background = Background('background.png')

class Light(pg.sprite.Sprite):
    def __init__(self,rect):

        pg.sprite.Sprite.__init__(self, lighting)
        self.oi = scale(load_image(YELLOW_LIGHT),(rect.width,rect.height))
        self.image = self.oi
        self.transparency = 200
        self.image.set_alpha(self.transparency)
        self.orect = rect
        self.rect = self.image.get_rect()
        self.glow = True
        self.framecount = 0
        self.transform = [self.orect.width, self.orect.height]
        self.flicker = 2
        self.change = [rect.width/2,rect.height/2]

    
    def animate(self,speed):
        
        self.framecount += 1
        if self.glow and self.framecount % speed == 0:
            if self.transform == self.change:
                self.glow = False
                self.framecount = 0
            self.image = scale(self.oi,(self.transform))
            self.transform[0] -= self.flicker
            self.transform[1] -= self.flicker
            self.transparency += 3

            

        elif not self.glow and self.framecount % speed == 0:
            if self.transform == [self.orect.width,self.orect.height]:
                self.glow = True
                self.framecount = 0
            self.image = scale(self.oi,(self.transform))
            self.transform[0] += self.flicker
            self.transform[1] += self.flicker
            self.transparency -= 3
        
        self.rect = self.image.get_rect()
        self.rect.center = self.orect.center

        self.image.set_alpha(self.transparency)  


            


class Inventory:
    def __init__(self):
        self.image = scale(load_image('inv.png'),(128,128))
        self.slot_image = load_image('inv_slot.png')
        self.slot_box = pg.Rect(WIDTH-156,HEIGHT-156,128,128)
        self.slots = [pg.Rect(self.slot_box.center[0]-16,self.slot_box.center[1]-72,32,32),
                    pg.Rect(self.slot_box.center[0]-16,self.slot_box.center[1]+40,32,32),
                    pg.Rect(self.slot_box.center[0]+40,self.slot_box.center[1]-18,32,36),
                    pg.Rect(self.slot_box.center[0]-72,self.slot_box.center[1]-18,32,36)]
        

Inv = Inventory()



class Levels:
    def __init__(self):
        self.run = True
        self.clock = clock.tick(FPS)

    def key_events(self,event):

        if event.type == pg.QUIT:
            self.run = False
            pg.quit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and physics.on_platform(player,obstacles) and not player.jumping:
                player.fallvelocity = 0.3
                player.jumping = True
            
            if event.key == pg.K_x and physics.on_platform(player,obstacles) and not player.attack:
                player.attack = True



Level = Levels()












class Game:

    def __init__(self):
        self.assets = {'platforms':['wood.png','stone_brick.png','moss_brick.png','chain.png','temp_lantern.png','dark_sand.png','grass.png','dirt.png','leaf.png'],
                        'items': []
                        }
        self.brightness = DARK
        set_brightness(self.brightness,100,BLACK)

    def load_data(self,map):
        #Loads fullmap (platforms, obstacles, items)
        for row, tiles in enumerate(map):
            for col, tile in enumerate(tiles):
                try:
                    if int(tile) == 4:
                        Decoration(int(tile),(col,row))
                        Light(pg.Rect(col*TILESIZE,row*TILESIZE,64,64))
                    
                    elif int(tile) == 3:
                        Decoration(int(tile),(col,row))
                        
                    else: Platform(int(tile),(col,row))
                    
                except (ValueError, KeyError): pass

game = Game()

game.load_data(fullmap.data)


#Game loop
run = True
size = False
while run:


    clock.tick(FPS)

    for event in pg.event.get():
        Level.key_events(event)



    
    background.scroll()
    player.movement()
    sprites.update()
    leaves.draw(WINDOW)
    #All map sprites
    for sprite in sprites:
        WINDOW.blit(sprite.image,camera.apply(sprite))

    #Inventory/UI
    WINDOW.blit(Inv.image,(Inv.slot_box))
    for rect in Inv.slots:
        WINDOW.blit(Inv.slot_image,rect)


    #Draw light and darkness   
    WINDOW.blit(game.brightness,(0,0))
    for light in lighting:
        WINDOW.blit(light.image,(camera.apply_rect(light.rect)))
        light.animate(4)
    

    
    pg.display.update()
