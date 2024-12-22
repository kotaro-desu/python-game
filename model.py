import random
import sys
import pygame 
COURSCLEAR=2000
CLEARTIME=30000
WIN_SIZE = (600,500)

class Rect:
    """
    あたり判定など、Entityの接触判定全般を扱う。
    当たり判定の範囲、当たり判定を行う。
    """
    def __init__(self, top_left, bottom_right):
        """
        引数はそれぞれ長さ２のリスト([x,y])
        あたり判定を行うための範囲を指定する。値はリスト型
        """
        self.setDim(top_left, bottom_right)

    def setDim(self, top_left, bottom_right):
        """
        引数はそれぞれ長さ２のリスト([x,y])
        右上が[0,0]、左下が画面の最大値
        """
        self.min = top_left
        self.max = bottom_right

    def contains(self,p):
        """
        点p([x,y])が内側にあるか
        setDimで設定した値の内側にある場合、接触していると判断する。
        """
        return self.min[0] < p[0] and p[0] < self.max[0] \
           and self.min[1] < p[1] and p[1] < self.max[1]

    def len(self, i):
        """
        次元iの長さを出力する。
        """
        return self.max[i] - self.min[i]

    def center(self, i):
        """
        次元iの中心を出力する。
        """
        return (self.max[i] + self.min[i])/2

    def intersects(self, r):
        """
        設定した当たり判定の範囲に入っているかを判定する。
        """
        for i in range(2):
            d = abs(self.center(i)-r.center(i))
            if d > (self.len(i) + r.len(i))/2:
                return False
        return True

class Entity(Rect):
    """ オブジェクトの既定クラス """
    def __init__(self,health, size:list, name:str=None, visual=None, algorithms=None):
        """ 
        Args:
            size:矩形サイズ(長さ２のリスト)
            name:名前（文字列）
            health:0になると消える(playerの場合は終了)
            visual:割り当てられるグラフィック名（文字列）
            algorithm:動きを決定するオブジェクト 
        """
        self.pos = [0,0]
        self.size = size
        self.name = name
        self.health=health
        self.coolTime=0
        self.algorithms = algorithms
        self.visual = visual
        self.will_disappear = False #Trueにすることで消滅する
        self.setDim()

    def isDied(self):
        """
        healthは0になっているかの確認
        """
        if self.health==0:
            return True
            #finish
        
    def add(self,a,b):
        """
        list型a,bの要素を足し合わせるための関数
        """
        return [a[0]+b[0], a[1]+b[1]]

    def decreaseHealth(self):
        """
        healthを1減らす。"1000"の部分を減らすことで被弾後の無敵時間の変更が可能。
        """
        if self.name=="user":
            if (pygame.time.get_ticks()-self.coolTime)>=1000:
                self.health-=1
                self.coolTime=pygame.time.get_ticks()
        elif self.name=="boss":
            if (pygame.time.get_ticks()-self.coolTime)>=1000:
                self.health-=1
                self.coolTime=pygame.time.get_ticks()
        elif self.name=="block":
            if (pygame.time.get_ticks()-self.coolTime)>=1000:
                self.health-=1
                self.coolTime=pygame.time.get_ticks()
        

    def setDim(self):
        super().setDim(self.pos, self.add(self.pos, self.size))

    def disapper(self): 
        """
        self.will_disappearの値をTrueに変える。
        """
        self.will_disappear = True

    def disappeared(self):
        """
        self.will_disappearの値を返す。
        """
        return self.will_disappear

    def getPos(self) -> list: 
        """
        オブジェクトの現在位置を返す
        """
        return self.pos

    def setPos(self,p : list):
        """
        オブジェクトの次の位置をセットする。
        """
        self.pos = list(p)
    
    def update(self, delta: float):
        """
        entityにセットされたalgorithmsの中のupdateを実行する
        """
        for a in self.algorithms:
            a.update(self,delta)

        self.setDim()

class LinearMotion:
    """一定速度で動くオブジェクト"""
    def __init__(self, initial=[0,0]):
        self.vel = initial

    def update(self, entity, delta):
        """
        オブジェクトの移動速度
        setVelでセットされた値分移動する。delta倍される。
        deltaはapp,py側で指定される。値はclock.get_time()/1000。
        """
        if entity.name!="user":
            p = entity.getPos()#entityの現在の位置
            p[1] -= self.vel[1]*0.005
            p[0] -= self.vel[0]*0.005+delta
            entity.setPos(p)

class BossMotion:
    """
    Bossのためのオブジェクト。
    self.num : bossが最初に現れる位置。
    self.high : Trueで上昇、Falseで降下する。
    """
    def __init__(self):
        self.num=400
        self.high=True
    def update(self, entity, delta):
        """
        オブジェクトの移動速度及びその動き。
        """
        p = entity.getPos()
        if self.high:
            self.num+=0.3
            if self.num>=450:   #最大降下位置
                self.high=False
        else:
            self.num-=0.3
            if self.num<=250:    #最大上昇位置
                self.high=True
        p[1] = self.num
        p[0] += 0.3-delta          #移動速度
        entity.setPos(p)

class Item:
    """itemのためのオブジェクト"""
    def __init__(self, _algo):
        self.algo=_algo         #itemの効果を決めるオブジェクト。
        self.haveItem=False     #itemを持っているか持っていないかを判断する。

    def update(self, entity, delta):
        """
        itemを持っていれば使う
        itemは動かない
        """
        if self.haveItem:
            self.algo.effect()
            self.haveItem=False
            #print("item使用")
        P=entity.getPos()
        P[0]-=delta
        entity.setPos(P)       

class ItemFuncSpeed:
    """
    speedを上げるitemのためのオブジェクト
    """
    def __init__(self,_model):
        self.model=_model       #modelが持つメンバ変数にアクセスするために必要
    
    def effect(self):
        """
        移動速度の倍率が4以下ならば、倍率を1つ増やす。
        """
        if self.model.moveMag<4:
            self.model.moveMag+=1
            #print("speed up")

class ItemFuncRecover:
    """
    healthを1つ回復させるitemのためのオブジェクト
    """
    def __init__(self,_entity):
        self.entity=_entity     #entity(player:引数じゃないよ)が持つメンバ変数にアクセスするために必要
    
    def effect(self):
        """
        healthが3より小さい場合、healthを1増やす。
        """
        if self.entity.health<3:
            self.entity.health+=1
            #print("recover health")

class ItemFuncJumpUp:
    """
    jumpを上げるitemのためのオブジェクト
    """
    def __init__(self,_model):
        self.model=_model       #modelが持つメンバ変数にアクセスするために必要
    
    def effect(self):
        """
        ジャンプ力が10より小さいならば、ジャンプ力を1つ増やす。
        """
        if self.model.jumpMag<10:
            self.model.jumpMag+=1
            #print("jump power up")

class ItemPoison:
    """
    毒のitemのためのオブジェクト
    """
    def __init__(self,_entity):
        self.entity=_entity       #_entityが持つメンバ変数にアクセスするために必要
    
    def effect(self):
        """
        体力を１減らす。
        """
        if self.entity.health>0:
            self.entity.health-=1

class Block:
    """
    障害物を作るオブジェクト
    """
    def __init__(self):
        pass
    def update(self, entity, delta):
        """
        ブロックは動かない
        """
        P=entity.getPos()
        P[0]-=delta
        entity.setPos(P)

class WithinScreen:
    """
    スクリーン外に出たentityを削除するためのオブジェクト。
    """
    def __init__(self, screen_size):
        self.screen_size = screen_size  #スクリーンのサイズを取得する
        
    def update(self, entity, delta):
        """
        スクリーンより外側に出た場合entityのdisapper関数を使用して、self.will_disappearをTrueに変更する。
        """
        rect = Rect([0,0], self.screen_size)
        if not rect.contains(entity.getPos()):
            entity.disapper()

class Model:
    """
    modelオブジェクト。プログラムの中核になる。
    """
    def __init__(self, view):
        """
        self.view                       :viewオブジェクトを入れる
        self.player_controller          :LinearMotion()オブジェクトを入れる
        self.constraint                 :WithinScreenの引数にスクリーンサイズを入れたオブジェクトを入れる
        self.player                     :player用のオブジェクトを入れる
        self.player.setPos([190,250])   :playerの初期位置を指定
        self.entites                    :entityを格納するためのメンバ変数
        self.count                      :jumpを実行するためのメンバ変数。大きくするとjump(上昇と下降)が早くなる。
        self.jumping=0                  :jumpをしているかしていないかを判断する。
        self.gravity=-9.8               :重力加速度
        self.v0=19.6                    :初速
        self.high=self.player.getPos()  :playerの初期のy軸方向の位置を保存する。jump関数に必要。
        self.moveDist=0                 :動いた距離を計測し続ける。移動距離でクリア判定をする時に必要。
        self.remainingBullet=0          :現在発車している弾丸を記憶する。3発以上打てない縛りに必要。
        self.jumpMag=5                  :jumpの最大位置の倍率
        self.moveMag=2                  :moveの最大速度の倍率
        self.difficulty=3               :コース選択に使用　1は距離でのクリア判定、2は時間でのクリア判定、3はboss撃破でのクリア判定
        self.timer =1
        self.boss=True                  :bossが出現しているかどうかを判定
        self.movable_obj=0              :進む量を表す
        self.enmCount=0                 :倒した敵の数
        self.frame1=0                   :敵描画用の変数1
        self.frame2=0                   :敵描画用の変数2
        self.frame3=0                   :敵描画用の変数3
        self.finsihJump=0               :着地後すぐであることを表す変数
        self.finsihShot=0               :射撃後すぐであることを表す変数
        self.finished=0                 :ゲームが終了した状態を保存　１でゲームオーバー　２でクリア
        self.firstTime=0
        """
        self.view = view
        self.player_controller = LinearMotion()
        self.constraint = WithinScreen(self.view.getScreenSize())
        self.player = Entity(4,[30,72],name="user",visual="player",algorithms=[self.player_controller])
        self.player.setPos([300,426])
        self.entites = [self.player]
        self.count=0
        self.jumping=0
        self.gravity=-9.8
        self.v0=19.6
        self.high=self.player.getPos()
        self.moveDist=0
        self.remainingBullet=0
        self.jumpMag=5
        self.moveMag=2
        self.difficulty=3
        self.timer = 100
        self.boss=True
        self.popUpSpeed=0
        self.time=0
        self.movable_obj=0
        self.enmCount=0
        self.frame1=0
        self.frame2=0
        self.frame3=0
        self.finsihJump=0
        self.finsihShot=0
        self.playerFrame1=0
        self.playerFrame2=0
        self.playerFrame3=0
        self.playerFrame4=0
        self.playerFrame5=0
        self.walkCont=0
        self.finished=0
        self.firstTime=0
        self.font = pygame.font.SysFont("georgia", 100)  # フォント
        self.screen = pygame.display.set_mode(WIN_SIZE)
        self.times = pygame.time.get_ticks()-self.firstTime

    def setPopUpSpeed(self):
        """
        雑魚敵の出現率の制御を行う
        """
        if self.difficulty==1:
            if (COURSCLEAR-500)>self.moveDist:
                self.popUpSpeed=100-int(50*(self.moveDist/(COURSCLEAR-500)))
            else:
                self.popUpSpeed=50+int(((self.moveDist-(COURSCLEAR-500))/500)*50)
            #print(self.popUpSpeed)
        if self.difficulty==2:
            if self.time>int((CLEARTIME*2)/3):
                self.popUpSpeed=70
            elif self.time>int(CLEARTIME/3):
                self.popUpSpeed=50
            else:
                self.popUpSpeed=90
        if self.difficulty==3:
            self.popUpSpeed=70

    def move(self, velx):
        """
        プレイヤーの動きを行う。正確にはプレイヤーが動くのではなく、背景と自分以外のentityが動く
        """
        velx=velx*self.moveMag
        if (self.moveDist+velx)>=0:         #0より小さいところ、つまり初期位置よりは進めない。
            self.moveDist+=velx
            self.movable_obj=velx*2
            self.view.setBackground(velx)   #viewにある背景を動かす関数
    
    def jump(self):
        """
        jumpを行うための関数。
        """
        if self.jumping==1 or self.jumping==2:     #2段ジャンプみたいなことを禁止するif文
            jumpPos= list(self.high)
            self.count+=0.03
            t=self.count
            x=(self.v0*t+(1/2)*self.gravity*t**2)*self.jumpMag
            if x>0:
                y=jumpPos[1]
                jumpPos[1]-=x
                if jumpPos[1]>y:
                    self.jumping=2
            else:
                jumpPos[1]=self.high[1]
                self.count=0
                self.jumping=0
                self.finsihJump=1
            
            self.player.setPos(jumpPos)
        else:
            self.high=self.player.getPos()

    def shoot(self):
        """
        玉を打つための関数。
        """
        if self.remainingBullet<3:          #3発以上はスクリーン上に存在できない
            motion = LinearMotion([-300,0])
            bullet = Entity(None,[30,30], name="bullet", visual="bullet", algorithms=[motion, self.constraint])
            bulletFor = [0,0]
            bulletFor[0] = self.player.pos[0] + 10
            bulletFor[1] = self.player.pos[1] + 15
            bullet.setPos(bulletFor)
            self.entites.append(bullet)
            self.remainingBullet+=1
            self.finsihShot=1

    def finishCheck(self):
        """
        終了判定 ==の後を変更することで他のコースに変更可能
        """
        if self.entites[0].isDied():
            """
            プレイヤーが死亡
            """
            #print("died")
            self.moveMag=2              #アイテムの効果を消す
            self.jumpMag=5              #アイテムの効果を消す
            #self.enmCount=0             #倒した敵の数をリセット
            #sys.exit()
            self.finished = 1
        elif self.difficulty==3:
            if self.entites[1].isDied():
                """
                bossが死亡。difficultyを3に変更するとboss戦
                """
                #print("boss died")
                self.moveMag=2              #アイテムの効果を消す
                self.jumpMag=5              #アイテムの効果を消す
                #self.enmCount=0             #倒した敵の数をリセット
                #sys.exit()
                self.finished = 2
            elif abs(self.entites[1].pos[0]-self.entites[0].pos[0])>1000:
                """
                bossと自機の距離が離れすぎ。difficultyを3に変更するとboss戦
                """
                #print("boss")
                self.moveMag=2              #アイテムの効果を消す
                self.jumpMag=5              #アイテムの効果を消す
                #self.enmCount=0             #倒した敵の数をリセット
                #sys.exit()
                self.finished = 1
        elif self.difficulty==1:
            if self.moveDist>=COURSCLEAR:
                """
                2000進めば終了。difficultyを1に変更すると距離でのクリア判定。
                2000を変えることで距離を変更可能。移動速度は初期で2。
                """
                #print("clear")
                self.moveMag=2              #アイテムの効果を消す
                self.jumpMag=5              #アイテムの効果を消す
                #self.enmCount=0             #倒した敵の数をリセット
                #sys.exit()
                self.finished = 2
        elif self.difficulty==2:
            if self.time>=CLEARTIME:
                """
                180000つまり3分たてば終了。180000を変更することで耐久時間を変更可能。
                ただし、得られる数値はミリ秒単位。
                """
                #print("clear")
                self.moveMag=2              #アイテムの効果を消す
                self.jumpMag=5              #アイテムの効果を消す
                #self.enmCount=0             #倒した敵の数をリセット
                #sys.exit()
                self.finished = 2
    
    def getTime(self):
        if self.firstTime>0:
            self.time=pygame.time.get_ticks()-self.firstTime

    def drawSetting(self,entity):
        """
        複数あるモーションから最適なモーションを選択する関数
        """

        if entity.name=="user":
            if self.finsihShot>0:
                if self.jumping==1 or self.jumping==2:
                    entity.visual="player5-2"            #飛びながら射撃のモーション
                else:
                    entity.visual="player5-1"            #射撃後すぐのモーション
                self.finsihShot+=1
                if self.finsihShot>40:
                    self.finsihShot=0

            elif self.jumping==1:
                if self.playerFrame1>=0 and self.playerFrame1<15:
                    entity.visual="player3-1"
                    self.playerFrame1+=1

                elif self.playerFrame1>=15 and self.playerFrame1<30:
                    entity.visual="player3-2"
                    self.playerFrame1+=1
                else:
                    self.playerFrame1=0
                    entity.visual="player3-1"      #ジャンプしている時のモーション

            elif self.jumping==2:
                if self.playerFrame2>=0 and self.playerFrame2<15:
                    entity.visual="player4-1"
                    self.playerFrame1+=1

                elif self.playerFrame2>=15 and self.playerFrame2<30:
                    entity.visual="player4-2"
                    self.playerFrame2+=1
                else:
                    self.playerFrame2=0
                    entity.visual="player4-1"      #落ちている時のモーション

            elif self.movable_obj>0:
                self.walkCont=10
                if self.playerFrame3>=0 and self.playerFrame3<3:
                    entity.visual="player2-1"
                    self.playerFrame3+=1

                elif self.playerFrame3>=3 and self.playerFrame3<6:
                    entity.visual="player2-2"
                    self.playerFrame3+=1
                else:
                    self.playerFrame3=0
                    entity.visual="player2-1"      #前進している時のモーション

            elif self.movable_obj<0:
                self.walkCont=10
                if self.playerFrame4>=0 and self.playerFrame4<6:
                    entity.visual="player6-1"
                    self.playerFrame4+=1

                elif self.playerFrame4>=6 and self.playerFrame4<12:
                    entity.visual="player6-2"
                    self.playerFrame4+=1
                else:
                    self.playerFrame4=0
                    entity.visual="player6-1"      #後進している時のモーション
            elif self.movable_obj==0:
                if self.walkCont==0:
                    if self.playerFrame5>=0 and self.playerFrame5<15:
                        entity.visual="player1-1"
                        self.playerFrame5+=1

                    elif self.playerFrame5>=15 and self.playerFrame5<30:
                        entity.visual="player1-2"
                        self.playerFrame5+=1
                    else:
                        self.playerFrame5=0
                        entity.visual="player1-1"      #静止している時のモーション
                else:
                    self.walkCont-=1
        if entity.name=="enemy1":
            if self.frame1>=0 and self.frame1<15:
                entity.visual="enemy1-1"
                self.frame1+=1

            elif self.frame1>=15 and self.frame1<30:
                entity.visual="enemy1-2"
                self.frame1+=1
            else:
                self.frame1=0
                entity.visual="enemy1-2"
        elif entity.name=="enemy2":
            if self.frame2>=0 and self.frame2<15:
                entity.visual="enemy2-1"
                self.frame2+=1
            elif self.frame2>=15 and self.frame2<30:
                entity.visual="enemy2-2"
                self.frame2+=1
            else:
                self.frame2=0     
                entity.visual="enemy2-2"  
        elif entity.name=="boss":
            if self.frame3>=0 and self.frame3<30:
                entity.visual="enemy3-1"
                self.frame3+=1
            elif self.frame3>=30 and self.frame3<60:
                entity.visual="enemy3-2"
                self.frame3+=1
            else:
                self.frame3=0     
                entity.visual="enemy3-2"    
        self.view.draw(entity)               #動いたスクリーン上のentityなどをreloadする

    def touchObject(self,entity):
        """
        あたり判定が出た時、何と何がぶつかっているのかを判定する関数。
        また、ぶつかったものの種類で実行するプログラムを変更している。
        """
        for target in filter(lambda e:e.name=="enemy1" or e.name=="enemy2" or e.name=="enemy3", self.entites):#lambda式：無名関数     
            if entity.intersects(target):
                if entity.name=="user":
                    """
                    When player hit enemy, enemy disappear and player' life is decrease.
                    """
                    target.disapper()
                    self.player.decreaseHealth()

                elif entity.name=="bullet":
                    """
                    プレイヤーが敵を攻撃
                    """
                    target.disapper()   
                    entity.disapper()
                    self.enmCount+=1

        for target in filter(lambda e:e.name=="boss", self.entites):#lambda式：無名関数     
            if entity.intersects(target):
                if entity.name=="user":
                    """
                    When player hit boss, boss not disappear and player' life is decrease.
                    """
                    self.player.decreaseHealth()

                elif entity.name=="bullet":
                    """
                    プレイヤーがbossを攻撃
                    """
                    target.decreaseHealth() 
                    entity.disapper()
                    if target.health==0:
                        target.disapper()

        for target in filter(lambda e:e.name=="user", self.entites):#lambda式：無名関数     
            if entity.intersects(target):
                if entity.name=="item":
                    """
                    When player hit item, item disappear and player get item.
                    """
                    entity.disapper() 
                    entity.algorithms[0].haveItem=True

        for target in filter(lambda e:e.name=="block", self.entites):#lambda式：無名関数     
            if entity.intersects(target):
                if entity.name=="user":
                    """
                    When player hit block, player can't move on front.
                    """
                    userX=entity.center(0)
                    blockX=target.center(0)
                    if userX>=blockX:
                        self.move(1)
                    else:
                        self.move(-1)
                elif entity.name=="bullet":
                    """
                    弾が壁にぶつかった時
                    """
                    entity.disapper()
                    target.decreaseHealth()
                    if target.health==0:
                        target.disapper()
    
    def playMusic(self,path,volume,frequency):
        """
        音声ファイルを再生するためのプログラム
        path        ファイルのパス
        volume      音量   0.1~1　の範囲で指定
        frequency   繰り返す回数　-1で永遠に繰り返す
        """
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(frequency)
    def setTimer(self,screen,time,font,r,g,b,x,y):
        """
        タイマーを出力するプログラム
        screen      スクリーンサイズ
        time        経過時間
        font        出力する際のフォント
        r,g,b       RGBで色を指定する
        x,y         出力する座標　xはx座標　yはy座標
        """
        if time <= 1000:
            timeLimit = 0
        if time > 1000 and time < 10000:
            t = str(time)
            timeLimit = int(t[-4])
        if time >= 10000:
            t = str(time)
            timeLimit =int(t[-5])*10 + int(t[-4])
        screen.blit(font.render(str(timeLimit),True,(r,g,b)),(x,y))
        pygame.display.update()
    
    def setDistance(self,screen,distance,font,r,g,b,x,y):
        """
        必要な移動距離を出力するプログラム
        """
        distances = COURSCLEAR - distance
        screen.blit(font.render(str(distances),True,(r,g,b)),(x,y))
        pygame.display.update()

    def update(self):
        """
        ループ毎に実行される。実行位置はapp.pyのAppクラス。
        """
        self.getTime()
        if self.difficulty == 1:
            self.setDistance(self.screen,self.moveDist,self.font,255,255,255,380,5)
        if self.difficulty == 2:
            self.setTimer(self.screen,self.time,self.font,255,255,255,380,5)
        self.setPopUpSpeed()
        self.view.reloadBackground()
        self.timer+=1
        if self.timer>=self.popUpSpeed:                 #enemyの出現数を制御
            algo = []
            if self.difficulty==1 or self.difficulty==2:#距離、時間がクリア条件
                """
                雑魚敵の出現を制御
                """
                if random.random() > 0.5:
                    algo = [LinearMotion([70,0]),self.constraint]
                    enemy = Entity(1,[40,40],name="enemy1", visual="enemy1", algorithms=algo)
                    enemy.setPos([self.view.getScreenSize()[0],random.randint(350,450)])
                else:
                    algo = [LinearMotion([50,-(random.randint(20,60))]),self.constraint]
                    enemy = Entity(1,[40,40],name="enemy2", visual="enemy2", algorithms=algo)
                    enemy.setPos([self.view.getScreenSize()[0],random.randint(250,350)])   
                self.entites.append(enemy)
            elif self.difficulty==3:#boss戦
                """
                bossの出現を制御
                """
                if self.boss:
                    algo = [BossMotion()]
                    enemy = Entity(30,[40,40],name="boss", visual="enemy3", algorithms=algo)
                    enemy.setPos([400,400])
                    self.boss=False
                    self.entites.append(enemy)
                if random.random() < 0.3:
                    """
                    雑魚敵の出現を制御
                    """
                    algo = [LinearMotion([40,0]),self.constraint]
                    enemy = Entity(1,[40,40],name="enemy1", visual="enemy1", algorithms=algo)
                    enemy.setPos([self.view.getScreenSize()[0],random.randint(350,450)])
                    self.entites.append(enemy)

            if random.random()<0.5:
                """
                itemの出現を制御
                """
                if random.random()>=0.7:
                    algo = [Item(ItemFuncRecover(self.player)),self.constraint]
                    item = Entity(1,[40,40],name="item", visual="item1", algorithms=algo)
                    item.setPos([self.view.getScreenSize()[0],random.randint(300,450)])
                elif random.random()>=0.5:
                    algo = [Item(ItemFuncJumpUp(self)),self.constraint]
                    item = Entity(1,[40,40],name="item", visual="item2", algorithms=algo)
                    item.setPos([self.view.getScreenSize()[0],random.randint(300,450)])
                elif random.random()>=0.3: 
                    algo = [Item(ItemFuncSpeed(self)),self.constraint]
                    item = Entity(1,[40,40],name="item", visual="item3", algorithms=algo)
                    item.setPos([self.view.getScreenSize()[0],random.randint(300,450)])
                else: 
                    algo = [Item(ItemPoison(self.player)),self.constraint]
                    item = Entity(1,[40,40],name="item", visual="item4", algorithms=algo)
                    item.setPos([self.view.getScreenSize()[0],random.randint(300,450)])
                self.entites.append(item)

            if random.random()<0.3:
                """
                blockの出現を制御
                """
                algo = [Block()]
                block = Entity(3,[25,25],name="block", visual="block", algorithms=algo)
                block.setPos([self.view.getScreenSize()[0],random.randint(350,450)])
                self.entites.append(block)
            self.timer =0

        self.jump()                         #ジャンプボタンを押されているならばジャンプしに行く
        for m in self.entites[:]:           #mにentityに格納されたインスタンスを1つずつ取りだす。
            self.touchObject(m)             #当たり判定が出ている時の制御
            m.update(self.movable_obj)      #entity内のupdate関数を実行
            if m.name=="user" or m.name=="boss":
                self.view.setGauge(m)       #userとbossの体力ゲージを出力
            if m.disappeared():             #entityのwill_disappearがTrueになっているものは削除する。
                if m.name=="bullet":        #玉は消えていれば打てるようにする
                    self.remainingBullet-=1
                self.entites.remove(m)  
            self.drawSetting(m)             #動いたスクリーン上のentityなどをreloadする
        self.finishCheck()             #終了判定を問い合わせる
        if len(self.entites)>=25:           #entityが25以上になった場合bossとuser以外を消す
            del self.entites[2]             #ソフトウェアが重たくなることへの対処
        self.movable_obj=0                  #これを行わないとコントロールキー方向に加速し続ける