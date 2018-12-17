# this file was created by Gavin Carreira
# Sources: goo.gl/2KMivS - Chris Bradfield your the man!
# availble in github
#https://www.youtube.com/channel/UCNaPQ5uLX5iIEHUCLmfAgKg
#https://www.zapsplat.com/?s=jump
#https://www.youtube.com/watch?v=qnUVjACD3WM

'''
**********Gameplay ideas:
have bullets shoot out of the enemy to destroy incoming mobs 

*****failed ideas 
My main goal in creating this project was to have the chracter fire bullets at the 
incoming eneimies, much like a concept from the orginal doodle jump. I started out watching Kids can code 
videos and coding along, but later realized I was way over my head and some of the code I was beginning 
to put was stuff I had never seen before, this ultimatley caused me to start over

**********Cosmetics
change clouds, enemies, sound, jump, explorer

**********Bugs
will not read spritesheet... "name 'Spritesheet' is not defined"

**********Gameplay fixes
increased boost and jump to decrese impossible jump zones 

**********Features
increased mobs, with added boosts, and higher powerups and jumps 
'''
import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
    ##### INIT METHODF
    def __init__(self):
        #init game window
        # init pygame and create window
        pg.init()
        # init sound mixer
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Space explorer")
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()
    ##### LOAD DATA METHOD
    def load_data(self):
        print("load data is called...")
        # sets up directory name for images
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        # opens file with write options
        ''' with is a contextual option that handles both opening and closing of files to avoid
        issues with forgetting to close
        '''
        try:
            # changed to r to avoid overwriting error
            with open(path.join(self.dir, "highscore.txt"), 'r') as f:
                self.highscore = int(f.read())
                print(self.highscore)
        except:
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                self.highscore = 0
                print("exception")
        # loads spritesheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET)) 
        #loads space portal images
        self.cloud_images = []
        for i in range(1,4):
            self.cloud_images.append(pg.image.load(path.join(img_dir, 'cloud{}.png'.format(i))).convert())
        # load sounds
        # awesome place to find sounds - https://www.zapsplat.com/?s=jump 
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = [pg.mixer.Sound(path.join(self.snd_dir, 'boing.mp3')),
                            pg.mixer.Sound(path.join(self.snd_dir, 'Jump29.wav'))]
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'swoosh.mp3'))
        self.head_jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'footjump.mp3'))
    ##### NEW METHOD
    def new(self):
        self.score = 0
        self.paused = False
        # add all sprites to the pg group
        # below no longer needed - using LayeredUpdate group
        # self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        # create platforms group
        self.platforms = pg.sprite.Group()
        # create clouds group
        self.clouds = pg.sprite.Group()
        # add powerups
        self.powerups = pg.sprite.Group()
        # add cacti
        self.cacti = pg.sprite.Group()
        
        self.mob_timer = 0
        # add a player 1 to the group
        self.player = Player(self)
        # add mobs
        self.mobs = pg.sprite.Group()
        # no longer needed after passing self.groups in Sprites library file
        # self.all_sprites.add(self.player)
        # instantiate new platform 
        for plat in PLATFORM_LIST:
            # no longer need to assign to variable because we're passing self.groups in Sprite library
            # p = Platform(self, *plat)
            Platform(self, *plat)
            # no longer needed because we pass in Sprite lib file
            # self.all_sprites.add(p)
            # self.platforms.add(p)
        for i in range(8):
            c = Cloud(self)
            c.rect.y += 500
        # load spaceship/shuttle music 
        pg.mixer.music.load(path.join(self.snd_dir, 'spaceshuttle.mp3'))
        # call the run method
        self.run()
    def run(self):
        # game loop
        # play music
        # for spaceshuttle music 
        pg.mixer.music.play(loops=-1)
        # set boolean playing to true
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(1000)
        # other things that happen when not playing anymore
    ##### UPDATE METHOD
    def update(self):
        self.all_sprites.update()
        # shall we spawn a mob?
        now = pg.time.get_ticks()
        # check for mob collisions
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)
        # now using collision mask to determine collisions
        # can use rectangle collisions here first if we encounter performance issues
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
        if mob_hits:
            # can use mask collide here if mob count gets too high and creates performance issues
            ''' I created the below code as an added feature:
                I wanted to create an option to jump on the enemies'
                heads to prevent getting stuck...'''
            if self.player.pos.y - 35 < mob_hits[0].rect.top:
                print("hit top")
                print("player is " + str(self.player.pos.y))
                print("mob is " + str(mob_hits[0].rect.top))
                self.head_jump_sound.play()
                self.player.vel.y = -BOOST_POWER
            else:
                print("player is " + str(self.player.pos.y))
                print("mob is " + str(mob_hits[0].rect.top))
                self.playing = False
        # check to see if player can jump - if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                ''' set var to be current hit in list to find which to 'pop' to 
                when two or more collide with player'''
                find_lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > find_lowest.rect.bottom:
                        print("hit rect bottom " + str(hit.rect.bottom))
                        find_lowest = hit
                # fall if center is off platform
                if self.player.pos.x < find_lowest.rect.right + 5 and self.player.pos.x > find_lowest.rect.left - 5:
                    if self.player.pos.y < find_lowest.rect.centery:
                        self.player.pos.y = find_lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False
        # if player reaches top 25th percentile of the screen spawn a portal....
        if self.player.rect.top <= HEIGHT / 4:
            # spawn a portal 
            if randrange(100) < 13:
                Cloud(self)
            # set player location based on velocity
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / randrange(2,10)), 2)
            # creates slight scroll at the top based on player y velocity
            # scroll plats and mobs with player
            for mob in self.mobs:
                # creates slight scroll based on player y velocity
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                # creates slight scroll based on player y velocity
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT + 40:
                    plat.kill()
                    self.score += 10
        # if player hits a power up
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False
        cacti_hits = pg.sprite.spritecollide(self.player, self.cacti, False)
        if cacti_hits:    
            if self.player.vel.y > 0 and self.player.pos.y > cacti_hits[0].rect.top:
                    print("falling")
                    print("player is " + str(self.player.pos.y))
                    print("mob is " + str(cacti_hits[0].rect.top))
        # Die space explorer!
        if self.player.rect.bottom > HEIGHT:
            '''make all sprites fall up when player falls'''
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                '''get rid of sprites as they fall up'''
                if sprite.rect.bottom < -25:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False
        # generate new random platforms
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            ''' removed widths and height params to allow for sprites '''
            """ changed due to passing into groups through sprites lib file """
            # p = Platform(self, random.randrange(0,WIDTH-width), 
            #                 random.randrange(-75, -30))
            Platform(self, random.randrange(0,WIDTH-width), 
                            random.randrange(-75, -30))
            # self.platforms.add(p)
            # self.all_sprites.add(p)
    ##### EVENTS METHOD
    def events(self):
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    if self.playing:
                        self.playing = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.player.jump()
                if event.type == pg.KEYUP:
                    if event.key == pg.K_SPACE:
                        """ # cuts the jump short if the space bar is released """
                        self.player.jump_cut()
                if event.type == pg.KEYUP:
                    if event.key == pg.K_p:
                        """ pause """
                        self.paused = True
    ##### DRAW METHOD
    def draw(self):
        self.screen.fill(SKY_BLUE)
        self.all_sprites.draw(self.screen)
        """ # not needed now that we're using LayeredUpdates """
        # self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        # double buffering - renders a frame "behind" the displayed frame
        pg.display.flip()
    ##### WAIT FOR KEY METHOD
    def wait_for_key(self): 
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type ==pg.KEYUP:
                    waiting = False
    ##### SHOW START SCREEN METHOD
    def show_start_screen(self):
        """ # game splash screen """
        self.screen.fill(BLACK)
        self.draw_text(TITLE, 48, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("WASD to move, Space to jump", 22, WHITE, WIDTH/2, HEIGHT/2)
        self.draw_text("Press any key to play...", 22, WHITE, WIDTH / 2, HEIGHT * 3/4)
        self.draw_text("High score " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
    ##### SHOW GO SCREEN METHOD
    def show_go_screen(self):
        """ # game splash screen """
        if not self.running:
            print("not running...")
            return
        self.screen.fill(BLACK)
        self.draw_text(TITLE, 48, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("WASD to move, Space to jump", 22, WHITE, WIDTH/2, HEIGHT/2)
        self.draw_text("Press any key to play...", 22, WHITE, WIDTH / 2, HEIGHT * 3/4)
        self.draw_text("High score " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT/2 + 40)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("new high score!", 22, WHITE, WIDTH / 2, HEIGHT/2 + 60)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))

        else:
            self.draw_text("High score " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT/2 + 40)


        pg.display.flip()
        self.wait_for_key()
    ##### DRAW TEXT METHOD
    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()

g.show_start_screen()

while g.running:
    g.new()
    try:
        g.show_go_screen()
    except:
        print("can't load go screen...")