from os import path
import pygame as pg
import pytmx




#Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
YELLOW = (255,255,0)
BLUE = (0, 255, 255)
RED = (255,0,0)
SILVER = (192,192,192)
GRAY = (128,128,128)
FOREST_GREEN = (34, 139, 34)


#Game settings
Game_Folder = path.dirname(__file__)

WIDTH, HEIGHT = 600,900
FPS = 60
MAP = []
TILESIZE = 64

GRIDWIDTH = WIDTH/TILESIZE

GRIDHEIGHT = HEIGHT/TILESIZE



#Player settings
PLAYER_SPEED = 7
JUMPING = False
FALL_MOVESPEED = PLAYER_SPEED * 0.75
FALL_ACCEL = 0.4
JUMP_SPEED_LIMIT = -25
JUMP_ACCELDROP = 0.7
DARK = pg.Surface((WIDTH, HEIGHT))
YELLOW_LIGHT = 'yellowlight.png'



#Load Functions and Classes

class Tiledmap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha = True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm
    
    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x,y,gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile,(x*self.tmxdata.tilewidth, y*self.tmxdata.tileheight))


    def create_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

class Textmap:
    def __init__(self,filename):
        with open(path.join(Game_Folder, filename),'r') as file:
            self.data = [line.strip() for line in file]
            
        
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE



fullmap = Textmap("map.txt")


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0,0,width,height)
        self.width = width
        self.height = height
        self.freeze = False

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
    
    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)
    
    
    def update(self, target):
        offset_x = -target.rect.x + (WIDTH/2)
        offset_y = -target.rect.y + (HEIGHT/2)
        #Calculates the player offset


        offset_x = min(0, offset_x) #left
        offset_y = min(0,offset_y) #top
        offset_x = max(-(self.width - WIDTH), offset_x) #right
        offset_y = max(-(self.height - HEIGHT), offset_y) #bottom
        #Keeps same offset If near end of screen

        self.freeze = True if offset_x == 0 or offset_x == -(self.width - WIDTH) else False
        self.camera.x, self.camera.y = offset_x, offset_y

camera = Camera(fullmap.width, fullmap.height)



h_flip = lambda image: pg.transform.flip(image,True,False)


def animate(object, frametype, slow):
    if object.frames[frametype] == len(object.animate[frametype])-1:
        object.frames[frametype] = 0
        object.framecount = 0
        return 'Finish'

    object.framecount += 1

    if object.framecount % slow == 0:
        object.frames[frametype] += 1

    object.image = object.animate[frametype][object.frames[frametype]] if object.direction == 'R' else h_flip(object.animate[frametype][object.frames[frametype]])
    if frametype != 'fall' and frametype != 'jump' and frametype!= 'run':
        object.rect = object.image.get_rect()


load_image = lambda image: pg.image.load(image).convert_alpha()

def set_brightness(fade,transparency,color):
    fade.fill(color)
    fade.set_alpha(transparency)

scale = lambda image,location: pg.transform.scale(image,location)

print(WIDTH,HEIGHT)
