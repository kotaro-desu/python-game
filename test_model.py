import unittest
from model import *
import pygame

class AlgoTest(unittest.TestCase):
    def test_linear(self):
        """
        0.005ずつ進んでいることを確認
        """
        l = LinearMotion([1,0])
        e = Entity(1,[30,72],algorithms=[l])
        e.update(0)
        self.assertEqual(e.pos, [-0.005,0])

        e.update(0)
        self.assertEqual(e.pos, [-0.01,0])
    def test_boss(self):
        """
        ボスの動きを確認
        """
        b= BossMotion()
        b.num=0
        e= Entity(30,[40,40], algorithms=[b])
        e.update(0)
        self.assertEqual(e.pos, [0.3,0.3])
        b.high=False
        e.update(0)
        self.assertEqual(e.pos, [0.6,0])
    def test_item(self):
        """
        アイテムの動きを確認
        """
        pygame.init()
        e = Entity(3,[30,72],algorithms=[])
        a= Item(ItemPoison(e))
        i = Entity(1,[40,40],name="item", algorithms=[a])
        a.haveItem=True
        i.update(0)
        self.assertEqual(e.health, 2)

        a= Item(ItemFuncRecover(e))
        i = Entity(1,[40,40],name="item", algorithms=[a])
        a.haveItem=True
        i.update(0)
        self.assertEqual(e.health, 3)

        m = Model(View())
        self.assertEqual(m.jumpMag, 5)
        a= Item(ItemFuncJumpUp(m))
        i = Entity(1,[40,40],name="item", algorithms=[a])
        a.haveItem=True
        i.update(0)
        self.assertEqual(m.jumpMag, 6)

        self.assertEqual(m.moveMag, 2)
        a= Item(ItemFuncSpeed(m))
        i = Entity(1,[40,40],name="item", algorithms=[a])
        a.haveItem=True
        i.update(0)
        self.assertEqual(m.moveMag, 3)

class View:
    def getScreenSize(self):
        return [600, 500]

    def draw(self, movable_obj):
        pass

class ModelTest(unittest.TestCase):
    def _shoot(self):
        m = Model(View())
        m.shoot()
        self.assertEqual(m.remainingBullet,1)
        self.assertEqual(m.entites[2].name,"bullet")

    def _finishCheck(self):
        m = Model(View())
        m.entites[0].health=0
        m.finishCheck()
        self.assertEqual(m.finished,1)

    def _drawSetting(self):
        m = Model(View())
        algo = []
        m.entites.append(Entity(1,[40,40],name="enemy1", visual="enemy1", algorithms=algo))
        m.entites[2].setPos([300,426])
        m.touchObject(m.entites[0])
        self.assertEqual(m.entites[2].visual,"enemy1-1")




if __name__ == '__main__':
    unittest.main()
