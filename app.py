# -*- coding: utf-8 -*-
import sys
import pygame
from pygame.locals import *
from model import Model

WIN_SIZE = (600, 500)
WIN_TITLE = "ZombieACT"
img_back = pygame.transform.scale(pygame.image.load("asset/backGraund.png"), [600,500])
class View:
    def __init__(self, screen):
        self.screen = screen
        self.sprites = {}
        self.sprites["player1-1"] = pygame.image.load("asset/stop1.png") #asset内においてpathを通せば使える
        self.sprites["player1-2"] = pygame.image.load("asset/stop2.png") #stop

        self.sprites["player2-1"] = pygame.image.load("asset/go1.png") #front
        self.sprites["player2-2"] = pygame.image.load("asset/go2.png") 

        self.sprites["player3-1"] = pygame.image.load("asset/jump1.png") #jump
        self.sprites["player3-2"] = pygame.image.load("asset/jump2.png") 

        self.sprites["player4-1"] = pygame.image.load("asset/fall1.png") #fall
        self.sprites["player4-2"] = pygame.image.load("asset/fall2.png") 

        self.sprites["player5-1"] = pygame.image.load("asset/stopHit.png") #stopShot
        self.sprites["player5-2"] = pygame.image.load("asset/jumpHit.png") #jumpShot

        self.sprites["player6-1"] = pygame.image.load("asset/back1.png") #back
        self.sprites["player6-2"] = pygame.image.load("asset/back2.png") 

        self.sprites["bullet"] = pygame.image.load("asset/dangan.png")
        self.sprites["life"] = pygame.image.load("asset/life.png")
        self.sprites["enemy1-1"] = pygame.image.load("asset/flyEnemy1.png")
        self.sprites["enemy1-2"] = pygame.image.load("asset/flyEnemy2.png")
        self.sprites["enemy2-1"] = pygame.image.load("asset/flyEnemy3.png")
        self.sprites["enemy2-2"] = pygame.image.load("asset/flyEnemy4.png")
        self.sprites["enemy3-1"] = pygame.image.load("asset/walkEnemy1.png")
        self.sprites["enemy3-2"] = pygame.image.load("asset/walkEnemy2.png")
        self.sprites["item1"] = pygame.image.load("asset/lifeUp.png")
        self.sprites["item2"] = pygame.image.load("asset/jumpUp.png")
        self.sprites["item3"] = pygame.image.load("asset/item_speedUp.png")
        self.sprites["item4"] = pygame.image.load("asset/item_poison.png")
        self.sprites["block"] = pygame.image.load("asset/block.png")
        self.valueBackground=0

    def getScreenSize(self):
        return self.screen.get_size()

    def draw(self, movable_obj):
        """ 
        実行すると、スクリーンにmovable_objに格納されたentityを描画する
        """
        img = self.sprites[movable_obj.visual]
        #visual=movable_obj.pos
        resized = pygame.transform.scale(img, movable_obj.size)
        self.screen.blit(resized, movable_obj.pos)

    def setBackground(self,move):
        """
        背景をどれだけ動かすかを設定する
        """
        self.valueBackground=(move+self.valueBackground)%600

    def reloadBackground(self):
        """
        背景を描画する(背景を動かす)
        """
        self.screen.blit(img_back, [600-self.valueBackground,0])
        self.screen.blit(img_back, [-self.valueBackground,0])

    def setGauge(self,entity):
        """
        体力ゲージを出力する
        """
        if entity.name=="user":
            """
            player側
            """
            for i in range(0,entity.health):
                resized = pygame.transform.scale(self.sprites["life"], [50,50])#list内は体力を表す画像の大きさ
                self.screen.blit(resized, [i*30,10])#体力ゲージを表す場所
        elif entity.name=="boss":
            """
            boss側
            体力は30を想定。30-1の0~29までを10で割り、0,1,2の3つにして表す。
            """
            for i in range(0,int((entity.health-1)/10)+1):
                resized = pygame.transform.scale(self.sprites["life"], [50,50])#list内は体力を表す画像の大きさ。
                self.screen.blit(resized, [300+i*30,10])#体力ゲージを表す場

    
class Controller:
    def __init__(self, model):
        self.model = model

        self.countClock=[0,0,0,0]
        self.key_down_bind = {}
        self.key_down_bind[K_LEFT] = lambda: self.model.move(-1)
        self.key_down_bind[K_RIGHT] = lambda: self.model.move(1)
        self.key_down_bind[K_SPACE] = lambda: self.model.shoot()


    def shortPress(self,key):
        if key==K_SPACE:
            self.key_down_bind[key]()
        if key==K_1:
            self.model.jumping=1    

    def longPress(self, key):
        if key[K_LEFT]:
            #pygame.key.set_repeat(1,10) 
            self.countClock[0]+=1 
            if self.countClock[0]==5:#小さいほど早く進む
                self.key_down_bind[K_LEFT]()
                self.countClock[0]=0

        if key[K_RIGHT]:
            #pygame.key.set_repeat(1,10)
            self.countClock[1]+=1
            if self.countClock[1]==5:
                self.key_down_bind[K_RIGHT]()
                self.countClock[1]=0

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WIN_SIZE)
        pygame.display.set_caption(WIN_TITLE)
        self.view = View(self.screen)
        self.model = Model(self.view)
        self.controller = Controller(self.model)
        self.screen.blit(img_back, [739,0])
        self.screen.blit(img_back, [0,0])
        self.title = True
        self.select = False
        self.game = False
        self.result1 = False
        self.result2 = False
        self.WIN_TITLE = WIN_TITLE
    def event_loop(self):
        title_bg = pygame.image.load("asset/title3.png").convert()  # タイトル背景
        select_bg = pygame.image.load("asset/stageSelect.png").convert()  # セレクト画面背景
        result1_bg = pygame.image.load("asset/result_die.png").convert()
        result2_bg = pygame.image.load("asset/result_clear.png").convert()
        font = pygame.font.SysFont("georgia", 100)  # フォント
        button_start = pygame.Rect(282, 260, 214, 60)  # startボタン
        button_exit = pygame.Rect(310,335,160, 60)
        button_stage1 = pygame.Rect(25,170,305,60)
        button_stage2 = pygame.Rect(25,250,305,60)
        button_stage3 = pygame.Rect(25,330,305,60)
        buttonExit = pygame.Rect(395,430,200,60)
        self.model.playMusic("asset/鏡の世界は眠らない.mp3",1,1)
        pygame.display.update()

        title = self.title
        select = self.select
        game = self.game
        result1 = self.result1
        result2 = self.result2
        enemyCount = 0
        
        while title:
            self.screen.blit(pygame.transform.scale(
                title_bg, (WIN_SIZE)), (0, 0))  # 背景描画
            pygame.draw.rect(self.screen, (255,155,0), button_start,1)  # ボタン描画 
            pygame.draw.rect(self.screen, (255,155,0), button_exit,1)  

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:  # 終了イベント
                    sys.exit(0)  # システム終了

                if event.type == MOUSEBUTTONDOWN:
                    # スタートボタンが押された場合の処理
                    if button_start.collidepoint(event.pos):
                        select = True
                        title = False
                    if button_exit.collidepoint(event.pos):
                        sys.exit()
        self.model.playMusic("asset/トレメイン夫人の厳格な規律.mp3",1,1)
        while select:
            # 画面設定
            pygame.init()
            self.screen.fill((30, 30, 30))
            self.screen.blit(pygame.transform.scale(select_bg, (WIN_SIZE)), (0, 0))
            pygame.draw.rect(self.screen, (255,155,0),button_stage1 ,1)  # ボタン描画
            pygame.draw.rect(self.screen, (255,155,0),button_stage2 ,1)
            pygame.draw.rect(self.screen, (255,155,0),button_stage3 ,1)
            pygame.draw.rect(self.screen, (255,155,0),buttonExit ,1)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    if button_stage1.collidepoint(event.pos):
                        pygame.init()
                        self.model.difficulty = 1
                        self.WIN_TITLE = "奥へ進もう"
                        pygame.display.set_caption(self.WIN_TITLE)
                        select = False
                        game = True
                    if button_stage2.collidepoint(event.pos):
                        pygame.init()
                        self.model.difficulty = 2
                        self.WIN_TITLE = "生き残ろう"
                        pygame.display.set_caption(self.WIN_TITLE)
                        select = False
                        game = True
                        self.model.firstTime=pygame.time.get_ticks()
                    if button_stage3.collidepoint(event.pos):
                        pygame.init()
                        self.model.difficulty = 3
                        self.WIN_TITLE = "逃げる敵を仕留めよう"
                        pygame.display.set_caption(self.WIN_TITLE)
                        select = False
                        game = True
                    if buttonExit.collidepoint(event.pos):
                        sys.exit()
        self.model.playMusic("asset/殺した.mp3",1,5)
        while game:
            i=0
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                    elif event.type == KEYDOWN:
                        self.controller.shortPress(event.key)
                pygame.event.pump()
                key=pygame.key.get_pressed()
                self.controller.longPress(key)
                self.model.update()
                pygame.display.update()
                if self.model.finished != 0:
                    enemyCount = self.model.enmCount
                    break
            if self.model.finished == 1:
                result1 = True
                game = False
                self.model.finished = 0
            else:
                result2 = True
                game = False
                self.model.finished = 0
        self.model.playMusic("asset/黒雲序曲.mp3",1,1)
        while result1:
            pygame.init()
            self.screen.fill((30, 30, 30))
            self.screen.blit(pygame.transform.scale(result1_bg, (WIN_SIZE)), (0, 0))
            self.screen.blit(font.render(str(enemyCount),True,(255,155,0)),(450,150))
            pygame.draw.rect(self.screen, (255,155,0),buttonExit ,1)
            pygame.display.update()
            for event in pygame.event.get():                   
                if event.type == MOUSEBUTTONDOWN:
                    if buttonExit.collidepoint(event.pos):
                        sys.exit()
        self.model.playMusic("asset/ここはどろぼうの国.mp3",1,1)
        while result2:
            pygame.init()
            self.screen.fill((30, 30, 30))
            self.screen.blit(pygame.transform.scale(result2_bg, (WIN_SIZE)), (0, 0))
            self.screen.blit(font.render(str(enemyCount), True, (255,155,0)), (450,150))
            pygame.draw.rect(self.screen, (255,155,0),buttonExit ,1)
            pygame.display.update()
            for event in pygame.event.get():            
                if event.type == MOUSEBUTTONDOWN:
                    if buttonExit.collidepoint(event.pos):
                        sys.exit()

if __name__ == "__main__":
    app = App()
    app.event_loop()
