from __future__ import division, print_function, unicode_literals

import random
import math
import os, sys

import pyglet
from pyglet.window import key
from pyglet.gl import *
import cocos.actions.instant_actions as ic
import cocos
from cocos.director import director
import cocos.collision_model as cm
import cocos.euclid as eu
import cocos.actions as ac
from cocos.sprite import Sprite
from cocos.layer import *
import pymunk.pyglet_util

current_path = os.getcwd()
sys.path.insert(0, os.path.join(current_path, "pymunk-4.0.0"))

import pymunk as pm
from pymunk import Vec2d

from pyglet.window import mouse

from cocos.draw import Line

fe = 1.0e-4
consts = {
    "window": {
        "width": 800,
        "height": 600,
        "vsync": True,
        "resizable": True
    },
    "view": {
        # as the font file is not provided it will decay to the default font;
        # the setting is retained anyway to not downgrade the code
        "font_name": 'Axaxax',
        "palette": {
            #'bg': (0, 65, 133),
            'bg': (255, 65, 133),
            'player': (237, 27, 36),
            'wall': (247, 148, 29),
            'gate': (140, 198, 62),
            'food': (140, 198, 62)
        }
    }
}
world = {
        "width": 400,
        "height": 300,
        "rPlayer": 8.0,
        "wall_scale_min": 0.75,  # relative to player
        "wall_scale_max": 2.25,  # relative to player
        "topSpeed": 100.0,
        "angular_velocity": 240.0,  # degrees / s
        "accel": 85.0,
        "bindings": {
            key.W: 'p1Up',
            key.A: 'p1Left',
            key.S: 'p1Down',
            key.D: 'p1Right',
            key.LEFT: 'p2Left',
            key.RIGHT: 'p2Right',
            key.UP: 'p2Up',
            key.DOWN: 'p2Down',
            key.Z: 'p1die',
        }
}

space = pm.Space()
space.gravity = Vec2d(0.0, -900.0)
batch = pyglet.graphics.Batch()

class MessageLayer(cocos.layer.Layer):

    """Transitory messages over worldview

    Responsability:
    full display cycle for transitory messages, with effects and
    optional callback after hiding the message.
    """

    def show_message(self, msg, callback=None):
        w, h = director.get_window_size()

        self.msg = cocos.text.Label(msg,
                                    font_size=52,
                                    font_name=consts['view']['font_name'],
                                    anchor_y='center',
                                    anchor_x='center')
        self.msg.position = (w / 2.0, h)

        self.add(self.msg)

        actions = (
            ac.Show() + ac.Accelerate(ac.MoveBy((0, -h / 2.0), duration=0.5)) +
            ac.Delay(1) +
            ac.Accelerate(ac.MoveBy((0, -h / 2.0), duration=0.5)) +
            ac.Hide()
        )

        if callback:
            actions += ac.CallFunc(callback)

        self.msg.do(actions)


def reflection_y(a):
    assert isinstance(a, eu.Vector2)
    return eu.Vector2(a.x, -a.y)

class Me(ac.Move):
    def __init__(self, cIn, start, angleIn):
        self.c = cIn
        # The root node's location
        mass = 100

        #self.controller = pm.Body()

        self.body = pm.Body(mass, pm.moment_for_box(mass**3, 40, 160))  # mass, moment
        # Somehow size is the other way around.... height width?
        self.body.position = start  # random.randint(20,400), 200
        #self.body.angle = 10  # random.random() * math.pi
        self.bbody = pm.Poly(self.body, [[0,0],[40,0],[40,160],[0,160]], offset=(0,0))
        #self.bbody = pm.Poly(self.controller, [[0,0],[40,0],[40,160],[0,160]], offset=(0,0))
        # moment = pm.moment_for_box(mass, 20, 30)
        # self.body = pm.Body(mass, moment)
        #

        self.torso  = Sprite('00' + cIn + 'charbody.png')
        self.torsor  = Sprite('00' + cIn + 'charbodyreversed.png')
        # torso  = pm.Poly.create_box(self.body, size=(40, 60), offset=(20,60))
        #torso.friction = 10

        self.head   = Sprite('00' + cIn + 'charhead.png')
        self.headr  = Sprite('00' + cIn + 'charheadreversed.png')
        # self.head_attach = pm.Body(mass, pm.moment_for_box(mass, 40, 40))
        # head  = pm.Poly.create_box(self.body, size=(40, 40), offset=(20,120))
        # head.friction = 10
        # self.head_attach.position = self.body.position + (0,60)

        self.larm   = Sprite('00' + cIn + 'charlarm.png')
        self.larm.anchor = (15, 30)
        #self.larm.anchor = (20, 60)
        # self.larm_attach = pm.Body(mass, pm.moment_for_box(mass, 20, 60))
        # larm  = pm.Poly.create_box(self.body, size=(20, 60), offset=(0,60))
        # larm.friction = 10
        # self.larm_attach.position = self.body.position + (-20,0)

        self.rarm   = Sprite('00' + cIn + 'charrarm.png')
        self.rarm.anchor = (-15, 30)
        # self.rarm_attach = pm.Body(mass, pm.moment_for_box(mass, 20, 60))
        # rarm  = pm.Poly.create_box(self.body, size=(20, 60), offset=(60,60))
        # rarm.friction = 10
        # self.rarm_attach.position = self.body.position + (40,0)

        self.lleg   = Sprite('00' + cIn + 'charlleg.png')
        self.lleg.anchor = (0, 30)
        # self.lleg_attach = pm.Body(mass, pm.moment_for_box(mass, 20, 60))
        # lleg  = pm.Poly.create_box(self.body, size=(20, 60), offset=(20,0))
        # lleg.friction = 10
        # self.lleg_attach.position = self.body.position + (0,-60)

        self.rleg   = Sprite('00' + cIn + 'charrleg.png')
        self.rleg.anchor = (0, 30)
        # self.rleg_attach = pm.Body(mass, pm.moment_for_box(mass, 20, 60))
        # rleg  = pm.Poly.create_box(self.body, size=(20, 60), offset=(40,0))
        # rleg.friction = 10
        # self.rleg_attach.position = self.body.position + (20,-60)

        # body_rleg.distance = 0
        self.torso.rotation = self.body.angle
        self.head.rotation = self.body.angle
        self.torsor.rotation = self.body.angle
        self.headr.rotation = self.body.angle
        self.larm.rotation = self.body.angle
        self.rarm.rotation = self.body.angle
        self.lleg.rotation = self.body.angle
        self.rleg.rotation = self.body.angle

        self.larmrot = 0
        self.rarmrot = 0
        self.llegrot = 0
        self.rlegrot = 0


        space.add(self.bbody, self.body)

        # , #self.head_attach, self.larm_attach, self.rarm_attach, self.lleg_attach, self.rleg_attach,
                  #body_head, body_larm, body_rarm, body_lleg, body_rleg,
                  #head, torso, larm, rarm, lleg, rleg)


    def alignPhys(self):
        self.torso.set_position(*self.body.position + (20,60))
        self.head.set_position(*self.body.position + (20,120))
        self.torsor.set_position(*self.body.position + (20,60))
        self.headr.set_position(*self.body.position + (20,120))
        self.larm.set_position(*self.body.position + (0,60))
        self.rarm.set_position(*self.body.position + (60,60))
        self.lleg.set_position(*self.body.position + (20,0))
        self.rleg.set_position(*self.body.position + (40,0))

        self.torso.rotation = self.body.angle
        self.head.rotation = self.body.angle
        self.torsor.rotation = self.body.angle
        self.headr.rotation = self.body.angle
        self.larm.rotation = self.body.angle + self.larmrot
        self.rarm.rotation = self.body.angle + self.rarmrot
        self.lleg.rotation = self.body.angle + self.llegrot
        self.rleg.rotation = self.body.angle + self.rlegrot

    def addComponents(self, layer):
        layer.add(self.lleg)
        layer.add(self.rleg)
        layer.add(self.larm)
        layer.add(self.rarm)
        layer.add(self.head)
        layer.add(self.torso)
        layer.add(self.headr)
        layer.add(self.torsor)
        pass

class Worldview(cocos.layer.Layer):

    """
    Responsabilities:
        Generation: random generates a level
        Initial State: Set initial playststate
        Play: updates level state, by time and user input. Detection of
        end-of-level conditions.
        Level progression.
    """
    is_event_handler = True

    def __init__(self, scene, player1, player2, roundmanager):
        self.roundmanager = roundmanager
        global prevKeys
        prevKeys = []
        super(Worldview, self).__init__()

        global keyboard
        keyboard = key.KeyStateHandler()
        director.window.push_handlers(keyboard)

        palette = consts['view']['palette']
        #Actor.palette = palette
        #r, g, b = palette['bg']
        #scene.add(cocos.layer.ColorLayer(r, g, b, 255), z=-1)
        message_layer = MessageLayer()
        self.player_layer = Layer()
        scene.add(message_layer, z=2)
        scene.add(self.player_layer,z=3)
        self.fn_show_message = message_layer

        # Setup the character sprites
        self.p1Object = player1
        self.p2Object = player2

        self.player1 = Me(self.p1Object.charSprite, (100, 150), 0)
        self.player2 = Me(self.p2Object.charSprite, (500, 150), 0)

        self.player1.addComponents(self.player_layer)
        self.player2.addComponents(self.player_layer)


        self.ruler = Ruler()
        self.ruler.addComponents(self.player_layer)

        self.bindings = world['bindings']
        buttons = {}
        for k in self.bindings:
            buttons[self.bindings[k]] = 0
        self.buttons = buttons

        self.schedule(self.update)

        # Physics stuff
        # The ground has lines ontop of it
        static_body = pm.Body()
        self.static_lines = [pm.Segment(static_body, (0.0, 50.0), (600.0, 50.0), 0.0),
                        pm.Segment(static_body, (0, 0), (0, 500.0), 0.0),
                        pm.Segment(static_body, (600.0, 0), (600.0, 500.0), 0.0),
                        pm.Segment(static_body, (0, 500.0), (600.0, 500.0), 0.0)
                        ]
        for l in self.static_lines:
            l.friction = 30
        space.add(self.static_lines)

        # static_body = pm.Body()
        # static_lines = [pm.Segment(static_body, (111.0, 280.0), (407.0, 246.0), 0.0)
        #                 ,pm.Segment(static_body, (407.0, 246.0), (407.0, 343.0), 0.0)
        #                 ]
        # for line in static_lines:
        #     line.elasticity = 0.95
        # space.add(static_lines)
        self.scene = scene

    def on_key_press(self, k, m):
        binds = self.bindings
        #print(k)
        if k in binds:
            self.buttons[binds[k]] = 1
            return True
        return False

    def on_key_release(self, k, m):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 0
            return True
        return False

    def on_mouse_press(self, x, y, button, modifiers):
        if self.player1.bbody.point_query((x, y)):
            print("Intersect: p1")
        if self.player2.bbody.point_query((x, y)):
            print("Intersect: p2")

    def update(self, dt):
        global prevKeys
        pdt = 1.0/60.  # override dt to keep physics simulation stable
        space.step(pdt)

        self.player1.alignPhys()
        self.player2.alignPhys()
        self.ruler.alignPhys()

        # a = self.player1.bbody.cache_bb()
        # try:
        #     self.scene.remove("aa")
        # except:
        #     pass
        # bar = cocos.layer.ColorLayer(255, 0, 0, 255, width=int(a.right-a.left), height=int(a.top-a.bottom))
        # bar.position = (a.left,a.bottom)
        # self.scene.add(bar, 5, "aa")

        # a = self.player2.bbody.cache_bb()
        # try:
        #     self.scene.remove("bb")
        # except:
        #     pass
        # bar = cocos.layer.ColorLayer(255, 0, 0, 255, width=int(a.right-a.left), height=int(a.top-a.bottom))
        # bar.position = (a.left,a.bottom)
        # self.scene.add(bar, 5, "bb")

        a = self.ruler.bruler.cache_bb()
        # try:
        #     self.scene.remove("bb")
        # except:
        #     pass
        # bar = cocos.layer.ColorLayer(255, 0, 0, 255, width=int(a.right-a.left), height=int(a.top-a.bottom))
        # bar.position = (a.left,a.bottom)
        # self.scene.add(bar, 5, "bb")

        # cheeky fast assumption
        if self.player1.bbody.point_query((a.left, a.bottom)) or self.player1.bbody.point_query((a.left, a.top)) or self.player1.bbody.point_query((a.right, a.bottom)) or self.player1.bbody.point_query((a.right, a.top)):
            self.roundmanager.player_win("p1","p2")
        if self.player2.bbody.point_query((a.left, a.bottom)) or self.player2.bbody.point_query((a.left, a.top)) or self.player2.bbody.point_query((a.right, a.bottom)) or self.player2.bbody.point_query((a.right, a.top)):
            self.roundmanager.player_win("p2","p1")


        # print(self.player.head.position)
        # print(self.player.head_attach.position)


        #print(self.player.body.position)
        # update player
        buttons = self.buttons

        # Check key presses

        #print(self.player1.bbody.bb)

        #self.ruler.body.apply_impulse(j=(1000,0), r=(0, 0))
        rot = buttons['p1Up']
        if rot != 0:
            self.p1Up += 1
            if self.p1Up < 15:
                self.player1.body.apply_impulse(j=(0,self.p1Up*600), r=(0, 0))
            self.ruler.rulerBody.apply_impulse(j=(0,2500), r=(0, 0))
            self.player1.larmrot = self.player1.larmrot  + 10
            self.player1.rarmrot = self.player1.rarmrot  + 10
        else:
            self.p1Up = 0
        rot = buttons['p1Down']
        if rot != 0:
            self.player1.body.apply_impulse(j=(0,-5000), r=(0, 0))
            self.ruler.rulerBody.apply_impulse(j=(0,-25000), r=(0, 0))
            self.player1.larmrot = self.player1.larmrot  - 10
            self.player1.rarmrot = self.player1.rarmrot  - 10
        rot = buttons['p1Left']
        if rot != 0:
            self.player1.body.apply_impulse(j=(-200,0), r=(0, 0))
            self.ruler.rulerBody.apply_impulse(j=(-1000,0), r=(0, 0))
            self.player1.llegrot = self.player1.llegrot  - 10
            self.player1.rlegrot = self.player1.rlegrot  - 10
            self.player1.torsor.do(ac.Show())
            self.player1.torso.do(ac.Hide())
            self.player1.headr.do(ac.Show())
            self.player1.head.do(ac.Hide())
        rot = buttons['p1Right']
        if rot != 0:
            self.player1.body.apply_impulse(j=(200,0), r=(0, 0))
            self.ruler.rulerBody.apply_impulse(j=(1000,0), r=(0, 0))
            self.player1.llegrot = self.player1.llegrot  + 10
            self.player1.rlegrot = self.player1.rlegrot  + 10
            self.player1.torso.do(ac.Show())
            self.player1.torsor.do(ac.Hide())
            self.player1.head.do(ac.Show())
            self.player1.headr.do(ac.Hide())

        rot = buttons['p2Up']
        if rot != 0:
            self.p2Up += 1
            if self.p2Up < 15:
                self.player2.body.apply_impulse(j=(0,self.p2Up*600), r=(0, 0))
            self.ruler.rulerBody.apply_impulse(j=(0,25000), r=(0, 0))
            self.player2.larmrot = self.player2.larmrot  + 10
            self.player2.rarmrot = self.player2.rarmrot  + 10
        else:
            self.p2Up = 0
        rot = buttons['p2Down']
        if rot != 0:
            self.player2.body.apply_impulse(j=(0,-5000), r=(0, 0))
            self.ruler.rulerBody.apply_impulse(j=(0,-25000), r=(0, 0))
            self.player2.larmrot = self.player2.larmrot  - 10
            self.player2.rarmrot = self.player2.rarmrot  - 10
        rot = buttons['p2Left']
        if rot != 0:
            self.player2.body.apply_impulse(j=(-200,0), r=(0, 0))
            self.ruler.rulerBody.apply_impulse(j=(-1000,0), r=(0, 0))
            self.player2.llegrot = self.player2.llegrot  - 10
            self.player2.rlegrot = self.player2.rlegrot  - 10
            self.player2.torsor.do(ac.Show())
            self.player2.torso.do(ac.Hide())
            self.player2.headr.do(ac.Show())
            self.player2.head.do(ac.Hide())
        rot = buttons['p2Right']
        if rot != 0:
            self.player2.body.apply_impulse(j=(200,0), r=(0, 0))
            self.ruler.rulerBody.apply_impulse(j=(1000,0), r=(0, 0))
            self.player2.llegrot = self.player2.llegrot  + 10
            self.player2.rlegrot = self.player2.rlegrot  + 10
            self.player2.torsor.do(ac.Show())
            self.player2.torso.do(ac.Hide())
            self.player2.headr.do(ac.Show())
            self.player2.head.do(ac.Hide())

        prevKeys = buttons
        rot = buttons['p1die']
        if rot != 0:
            print(self.roundmanager.gamestate)
            self.roundmanager.player_win("p1","p2")

class Ruler(ac.Move):
    def __init__(self):
        # self.xsize = 16
        # self.ysize = 141
        self.ruler = Sprite("ruler1p.png")
        # self.currx = 300
        # self.curry = 113
        # self.wsprite = Sprite(self.spritefile)
        # self.wsprite.position = self.currx, self.curry

        self.rulerBody = pm.Body(16*3, pm.moment_for_box(16, 16, 141))  # mass, moment
        self.bruler = pm.Poly.create_box(self.rulerBody, size=(16, 141))
        self.rulerBody.position = 325, 151  #random.randint(20,400), 200
        self.ruler.position = 325, 151
        self.rulerBody.angle = 90
        space.add(self.rulerBody, self.bruler)

    # def updatepos(xchange, ychange):
    #     pass

    def addComponents(self, layer):
         layer.add(self.ruler)


    def alignPhys(self):
        self.ruler.set_position(*self.rulerBody.position)
        self.ruler.rotation = self.rulerBody.angle




    # def hitPlayer(self, player):
    #     pass

    #self.head
    #self.head_attach = pm.Body(mass, pm.moment_for_box(mass, 40, 40))
    #head  = pm.Poly(self.head_attach, [[0,0],[40,0],[40,40],[0,40]])
    #head.friction = 1
    #self.head_attach.position = self.body.position + (0,50)

# Useful example code
