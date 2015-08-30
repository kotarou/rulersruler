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
import music
current_path = os.getcwd()
sys.path.insert(0, os.path.join(current_path, "pymunk-4.0.0"))
import random
import pymunk as pm
from pymunk import Vec2d

from pyglet.window import mouse
import time
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
        }
}

space = pm.Space()
#space.gravity = Vec2d(0.0, -900.0)

batch = pyglet.graphics.Batch()

# Controls movement
upForce = 10
upSpeed = 5
sideForce = 10
sideSpeed = 5
sideDirectionMult = 10
upDirectionMult = 10
wallImpactForce = 200 #4500
playerImpactForceMult = 300


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
    def __init__(self, cIn, start, angleIn, crowns, layer):
        self.layer = layer
        self.crowns = crowns
        self.crownObj = []
        self.c = cIn
        self.batch = cocos.batch.BatchNode()
        # The root node's location
        mass = 100
        self.start = start
        #self.controller = pm.Body()

        self.body = pm.Body(mass*10, pm.moment_for_box(mass**3, 40, 160))  # mass, moment
        # Somehow size is the other way around.... height width?
        self.body.position = self.start  # random.randint(20,400), 200
        #self.body.angle = 10  # random.random() * math.pi
        #self.bbody = pm.Poly(self.body, [[0,0],[40,0],[40,160],[0,160]], offset=(0,0), radius=int(cIn))
        self.bbody = pm.Poly(self.body, [[0,10],[35,10],[35,90],[0,90]], offset=(0,0), radius=int(cIn))
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

        print("as")
        self.updateCrowns()
        # body_rleg.distance = 0
        self.torso.rotation = self.body.angle
        self.head.rotation = self.body.angle
        self.torsor.rotation = self.body.angle
        self.headr.rotation = self.body.angle
        self.larm.rotation = self.body.angle
        self.rarm.rotation = self.body.angle
        self.lleg.rotation = self.body.angle
        self.rleg.rotation = self.body.angle

        self.torso.scale = 0.4
        self.head.scale = 0.7
        self.torsor.scale = 0.4
        self.headr.scale = 0.7
        self.larm.scale = 0.4
        self.rarm.scale = 0.4
        self.lleg.scale = 0.4
        self.rleg.scale = 0.4

        self.bbody.elasticity = 1
        #self.body.elasticity = 1
        #self.body.friction = 0.3
        self.body.group = 0

        self.larmrot = 0
        self.rarmrot = 0
        self.llegrot = 0
        self.rlegrot = 0


        space.add(self.bbody, self.body)

        # , #self.head_attach, self.larm_attach, self.rarm_attach, self.lleg_attach, self.rleg_attach,
                  #body_head, body_larm, body_rarm, body_lleg, body_rleg,
                  #head, torso, larm, rarm, lleg, rleg)

    def updateCrowns(self):
        i = 0
        for item in self.crownObj:
            self.layer.remove(item)

        self.crownObj = []
        for item in self.crowns:
            itspr = cocos.sprite.Sprite(item)
            itspr.scale_y = 2
            itspr.scale_x = 2
            itspr.position = self.body.position + (20,(120 + (25*i)))
            self.layer.add(itspr)
            self.crownObj.append(itspr)
            i += 1
        self.bbody.unsafe_set_vertices([[0,10],[35,10],[35,90+(i*25)],[0,90+(i*25)]])

        #print(self.crowns)
        #for item in self.crowns:
        #    self.spritem = Sprite(item)
        #    self.spritem.do( Place( (120, 330) ))
        #    print(item)
        #    print(self.spritem)
            #self.spritem.anchor(0,100)

    def alignPhys(self):
        self.torso.set_position(*self.body.position + (20,50))
        self.head.set_position(*self.body.position + (20,80))
        self.torsor.set_position(*self.body.position + (20,50))
        self.headr.set_position(*self.body.position + (20,80))
        self.larm.set_position(*self.body.position + (0,30))
        self.rarm.set_position(*self.body.position + (40,30))
        self.lleg.set_position(*self.body.position + (10,10))
        self.rleg.set_position(*self.body.position + (30,10))

        self.torso.rotation = self.body.angle
        self.head.rotation = self.body.angle
        self.torsor.rotation = self.body.angle
        self.headr.rotation = self.body.angle
        self.larm.rotation = self.body.angle + self.larmrot
        self.rarm.rotation = self.body.angle + self.rarmrot
        self.lleg.rotation = self.body.angle + self.llegrot
        self.rleg.rotation = self.body.angle + self.rlegrot

        i = 0
        for item in self.crownObj:
            item.position = self.body.position + (20,(120 + (25 * i)))
            i += 1

    def addComponents(self, layer):
        self.layer.add(self.lleg)
        self.layer.add(self.rleg)
        self.layer.add(self.larm)
        self.layer.add(self.rarm)
        self.layer.add(self.head)
        self.layer.add(self.torso)
        self.layer.add(self.headr)
        self.layer.add(self.torsor)
        self.layer.add(self.batch)
        pass


    def reset(self):
        #self.body.position = self.start
        #self.body.reset_forces()
        #self.bbody.reset_forces()
        self.updateCrowns()
        print("d")

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
        self.fn_show_message = message_layer.show_message
        # Setup the character sprites
        self.p1Object = player1
        self.p2Object = player2

        self.player1 = Me(self.p1Object.charSprite, (100, 350), 0, player1.crowns, self.player_layer)
        self.player2 = Me(self.p2Object.charSprite, (500, 350), 0, player2.crowns, self.player_layer)

        self.player1.addComponents(self.player_layer)
        self.player2.addComponents(self.player_layer)


        self.ruler = Ruler(side=0, spawnHeight=random.randint(50, 400), width=800, height=10, speed=random.randint(50, 400), layer=self.player_layer)


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
        self.static_lines = [pm.Segment(static_body, (0.0, 10.0), (600.0, 10.0), 0.0),
                        pm.Segment(static_body, (0, 0), (0, 500.0), 0.0),
                        pm.Segment(static_body, (600.0, 0), (600.0, 500.0), 0.0),
                        pm.Segment(static_body, (0, 500.0), (600.0, 500.0), 0.0)
                        ]
        for l in self.static_lines:
            #l.friction = 0.5
            l.elasticity = 0.7
        space.add(self.static_lines)


        space.add_collision_handler(0, 0,begin=self.collide, pre_solve=None, post_solve=None, separate=None)
        # static_body = pm.Body()
        # static_lines = [pm.Segment(static_body, (111.0, 280.0), (407.0, 246.0), 0.0)
        #                 ,pm.Segment(static_body, (407.0, 246.0), (407.0, 343.0), 0.0)
        #                 ]
        # for line in static_lines:
        #     line.elasticity = 0.95
        # space.add(static_lines)
        self.scene = scene

    def restart(self):
        self.ruler.replace()
        self.player1.reset()
        self.player2.reset()
        #time.sleep(3)


    def collide(self, a, arb):
        #print(arb.shapes)
        obj1 = arb.shapes[0]
        obj2 = arb.shapes[1]

        # Ruler against player collisions
        if 1 in [obj1.radius, obj2.radius] and 3 in [obj1.radius, obj2.radius]:
            self.fn_show_message("Player 1 died!")
            self.roundmanager.player_win(2)
            self.restart()
            music.play_whack()
            return False
        elif 2 in [obj1.radius, obj2.radius] and 3 in [obj1.radius, obj2.radius]:
            self.fn_show_message("Player 2 died!")
            self.roundmanager.player_win(1)
            self.restart()
            music.play_whack()
            return False

        # Player - Player collisions
        elif 1 in [obj1.radius, obj2.radius] and 2 in [obj1.radius, obj2.radius]:
            return True
            # for c in arb.contacts:
            #     print(obj1.body.position - obj2.body.position)
            #     obj1.body.apply_force(((obj1.body.position - obj2.body.position) * playerImpactForceMult), r=(0,0))
            #     obj2.body.apply_force(((obj2.body.position - obj1.body.position) * playerImpactForceMult), r=(0,0))
        # Player1 - Wall collisions
        elif 1 in [obj1.radius, obj2.radius]:
            return True
            # print("c1 impacts wall")
            # for c in arb.contacts:
            #     print((obj1.body.position,c.position,obj2.body.position))
            #     if c.position[1] > 490:
            #         print("top wall")
            #         # Top wall
            #         obj1.body.apply_force(f=(0,-wallImpactForce), r=(0,0))
            #         obj2.body.apply_force(f=(0,-wallImpactForce), r=(0,0))
            #     elif c.position[1] < 20:
            #         # Bottom wall
            #         obj1.body.apply_force(f=(0,wallImpactForce), r=(0,0))
            #         obj2.body.apply_force(f=(0,wallImpactForce), r=(0,0))
            #     elif c.position[0] < 20:
            #         # Left wall
            #         obj1.body.apply_force(f=(wallImpactForce,0), r=(0,0))
            #         obj2.body.apply_force(f=(wallImpactForce, 0), r=(0,0))
            #     elif c.position[0] > 450:
            #         # Right wall
            #         obj1.body.apply_force(f=(-wallImpactForce, 0), r=(0,0))
            #         obj2.body.apply_force(f=(-wallImpactForce, 0), r=(0,0))

                #obj1.body.velocity = -obj1.body.velocity
        # Player2 - Wall collisions
        elif 2 in [obj1.radius, obj2.radius]:
            return True
            # print("c2 impacts wall")
            # for c in arb.contacts:
            #     print((obj1.body.position,c.position,obj2.body.position))
            #     if c.position[1] > 490:
            #         print("top wall")
            #         # Top wall
            #         obj1.body.apply_force(f=(0,-wallImpactForce), r=(0,0))
            #         obj2.body.apply_force(f=(0,-wallImpactForce), r=(0,0))
            #     elif c.position[1] < 20:
            #         # Bottom wall
            #         obj1.body.apply_force(f=(0,wallImpactForce), r=(0,0))
            #         obj2.body.apply_force(f=(0,wallImpactForce), r=(0,0))
            #     elif c.position[0] < 20:
            #         # Left wall
            #         obj1.body.apply_force(f=(wallImpactForce,0), r=(0,0))
            #         obj2.body.apply_force(f=(wallImpactForce, 0), r=(0,0))
            #     elif c.position[0] > 450:
            #         # Right wall
            #         obj1.body.apply_force(f=(-wallImpactForce, 0), r=(0,0))
            #         obj2.body.apply_force(f=(-wallImpactForce, 0), r=(0,0))
        else:
            return False
        return True


    def notCollide(self, a, b):
        return False


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

        # a = self.ruler.bruler.cache_bb()
        # try:
        #     self.scene.remove("cc")
        # except:
        #     pass
        # bar = cocos.layer.ColorLayer(255, 0, 0, 255, width=int(a.right-a.left), height=int(a.top-a.bottom))
        # bar.position = (a.left,a.bottom)
        # self.scene.add(bar, 5, "cc")

        # print(self.player.head.position)
        # print(self.player.head_attach.position)


        #print(self.player.body.position)
        # update player
        buttons = self.buttons

        # Check key presses

        #print(self.player1.bbody.bb)

        #self.ruler.body.apply_impulse(j=(1000,0), r=(0, 0))
        rot = buttons['p1Up']
        #print(self.player1.body.velocity)
        if rot != 0:
            # if self.player1.body.velocity[1] < 0:
            #     self.player1.body.apply_force(f=(0,upForce*upDirectionMult), r=(0, 30))
            # else:
            #     self.player1.body.apply_force(f=(0,upForce), r=(0, 30))
            self.player1.body.velocity = self.player1.body.velocity + (0, upSpeed)
            self.player1.larmrot = self.player1.larmrot  + 10
            self.player1.rarmrot = self.player1.rarmrot  + 10
        else:
            self.p1Up = 0
        rot = buttons['p1Down']
        if rot != 0:
            # if self.player1.body.velocity[1] > 0:
            #     self.player1.body.apply_force(f=(0,-upForce*upDirectionMult), r=(0, 30))
            # else:
            #     self.player1.body.apply_force(f=(0,-upForce), r=(0, 30))
            self.player1.body.velocity = self.player1.body.velocity + (0, -upSpeed)
            self.player1.larmrot = self.player1.larmrot  - 10
            self.player1.rarmrot = self.player1.rarmrot  - 10
        rot = buttons['p1Left']
        if rot != 0:
            # if self.player1.body.velocity[0] > 0:
            #     self.player1.body.apply_force(f=(-sideForce*sideDirectionMult, 0), r=(30, 00))
            # else:
            #     self.player1.body.apply_force(f=(-sideForce, 0), r=(0, 30))
            self.player1.body.velocity = self.player1.body.velocity + (-sideSpeed, 0)
            self.player1.llegrot = self.player1.llegrot  - 10
            self.player1.rlegrot = self.player1.rlegrot  - 10
            self.player1.torsor.do(ac.Show())
            self.player1.torso.do(ac.Hide())
            self.player1.headr.do(ac.Show())
            self.player1.head.do(ac.Hide())
        rot = buttons['p1Right']
        if rot != 0:
            # if self.player1.body.velocity[0] < 0:
            #     self.player1.body.apply_force(f=(sideForce*sideDirectionMult, 0), r=(-30, 0))
            # else:
            #     self.player1.body.apply_force(f=(sideForce, 0), r=(0, 30))
            self.player1.body.velocity = self.player1.body.velocity + (sideSpeed, 0)
            self.player1.llegrot = self.player1.llegrot  + 10
            self.player1.rlegrot = self.player1.rlegrot  + 10
            self.player1.torso.do(ac.Show())
            self.player1.torsor.do(ac.Hide())
            self.player1.head.do(ac.Show())
            self.player1.headr.do(ac.Hide())

        rot = buttons['p2Up']
        #print(self.player1.body.velocity)
        if rot != 0:
            # if self.player2.body.velocity[1] < 0:
            #     self.player2.body.apply_force(f=(0,upForce*upDirectionMult), r=(0, 30))
            # else:
            #     self.player2.body.apply_force(f=(0,upForce), r=(0, 30))
            self.player2.body.velocity = self.player2.body.velocity + (0, upSpeed)
            self.player2.larmrot = self.player2.larmrot  + 10
            self.player2.rarmrot = self.player2.rarmrot  + 10
        else:
            self.p1Up = 0
        rot = buttons['p2Down']
        if rot != 0:
            # if self.player2.body.velocity[1] > 0:
            #     self.player2.body.apply_force(f=(0,-upForce*upDirectionMult), r=(0, 30))
            # else:
            #     self.player2.body.apply_force(f=(0,-upForce), r=(0, 30))
            self.player2.body.velocity = self.player2.body.velocity + (0, -upSpeed)
            self.player2.larmrot = self.player2.larmrot  - 10
            self.player2.rarmrot = self.player2.rarmrot  - 10
        rot = buttons['p2Left']
        if rot != 0:
            # if self.player2.body.velocity[0] > 0:
            #     self.player2.body.apply_force(f=(-sideForce*sideDirectionMult, 0), r=(30, 00))
            # else:
            #     self.player2.body.apply_force(f=(-sideForce, 0), r=(0, 30))
            self.player2.body.velocity = self.player2.body.velocity + (-sideSpeed, 0)
            self.player2.llegrot = self.player2.llegrot  - 10
            self.player2.rlegrot = self.player2.rlegrot  - 10
            self.player2.torsor.do(ac.Show())
            self.player2.torso.do(ac.Hide())
            self.player2.headr.do(ac.Show())
            self.player2.head.do(ac.Hide())
        rot = buttons['p2Right']
        if rot != 0:
            # if self.player2.body.velocity[0] < 0:
            #     self.player2.body.apply_force(f=(sideForce*sideDirectionMult, 0), r=(-30, 0))
            # else:
            #     self.player2.body.apply_force(f=(sideForce, 0), r=(0, 30))
            self.player2.body.velocity = self.player2.body.velocity + (sideSpeed, 0)
            self.player2.llegrot = self.player2.llegrot  + 10
            self.player2.rlegrot = self.player2.rlegrot  + 10
            self.player2.torso.do(ac.Show())
            self.player2.torsor.do(ac.Hide())
            self.player2.head.do(ac.Show())
            self.player2.headr.do(ac.Hide())

        prevKeys = buttons


        #self.ruler.rulerBody.apply_force((0.0, 90000.0), self.ruler.rulerBody.position)

class Ruler(ac.Move):
    def __init__(self, side, spawnHeight, width, height, speed, layer):
        self.layer = layer
        # self.xsize = 16
        # self.ysize = 141
        self.ruler = Sprite("ruler1p.png")
        # self.currx = 300
        # self.curry = 113
        # self.wsprite = Sprite(self.spritefile)
        # self.wsprite.position = self.currx, self.curry

        self.rulerBody = pm.Body(100, pm.moment_for_box(1000**5, 800, height))  # mass, moment
        self.bruler = pm.Poly.create_box(self.rulerBody, size=(width, height), radius=3)
        #self.ruler.scale_x = width / 800
        self.ruler.scale_y = height / 16.
        self.rulerBody.position = -400 if side == 0 else 1200, spawnHeight  # random.randint(20,400), 200
        self.ruler.position = self.rulerBody.position
       # self.rulerBody.angle = 90
        self.rulerBody.group = 2
        space.add(self.rulerBody, self.bruler)
        self.rulerBody.velocity = (speed if side ==0 else -speed, 0)
    # def updatepos(xchange, ychange):
    #     pass
        #self.rulerBody.apply_force((0.0, 90000000.0), self.rulerBody.position)
    def addComponents(self, layer):
         layer.add(self.ruler)



    def alignPhys(self):
        self.ruler.set_position(*self.rulerBody.position)
        self.ruler.rotation = self.rulerBody.angle
        if self.rulerBody.position[0] > 1200 or self.rulerBody.position[0] < -400:
            self.replace()

    def replace(self):
        #self.rulerBody = pm.Body(100, pm.moment_for_box(100**3, 800, height))  # mass, moment
        #self.bruler = pm.Poly.create_box(self.rulerBody, size=(800, height), radius=3)
        space.remove(self.rulerBody)
        space.remove(self.bruler)
        height = random.randint(10, 50)
        width = random.randint(400, 800)
        vdir = random.randint(0, 1)

        self.rulerBody = pm.Body(100, pm.moment_for_box(1000**5, 800, height))  # mass, moment
        side = random.randint(0, 1)

        # if vdir > 0:
        #     a = width
        #     width = height
        #     height = a
        #     self.layer.remove(self.ruler)
        #     self.ruler = Sprite("ruler.png")
        #     self.layer.add(self.ruler)
        #     spawnWidth = random.randint(50, 400)
        #     speed = random.randint(100, 250)
        #     self.rulerBody.position = spawnWidth, -399 if side == 0 else 1199  #random.randint(20,400), 200
        #     self.ruler.position = self.rulerBody.position
        #     self.rulerBody.velocity = (0, speed if side == 0 else -speed)
        # else:
        #self.layer.remove(self.ruler)
        #self.ruler = Sprite("ruler1p.png")
        #self.layer.add(self.ruler)
        spawnHeight = random.randint(50, 400)
        speed = random.randint(100, 250)
        self.rulerBody.position = -399 if side == 0 else 1199, spawnHeight  #random.randint(20,400), 200
        self.ruler.position = self.rulerBody.position
        self.rulerBody.velocity = (speed if side == 0 else -speed, 0)


        self.bruler = pm.Poly.create_box(self.rulerBody, size=(width, height), radius=3)
        space.add(self.rulerBody, self.bruler)


        self.ruler.scale_x = width / 800
        self.ruler.scale_y = height / 16.

# class Ruler(ac.Move):
#     def __init__(self):
#         # self.xsize = 16
#         # self.ysize = 141
#         self.ruler = Sprite("ruler1p.png")
#         # self.currx = 300
#         # self.curry = 113
#         # self.wsprite = Sprite(self.spritefile)
#         # self.wsprite.position = self.currx, self.curry

#         self.rulerBody = pm.Body(16*3, pm.moment_for_box(16, 16, 141))  # mass, moment
#         self.bruler = pm.Poly.create_box(self.rulerBody, size=(141, 16), radius=3)
#         self.rulerBody.position = 325, 151  #random.randint(20,400), 200
#         self.ruler.position = 325, 151
#        # self.rulerBody.angle = 90
#         self.rulerBody.group = 2
#         space.add(self.rulerBody, self.bruler)

#     # def updatepos(xchange, ychange):
#     #     pass

#     def addComponents(self, layer):
#          layer.add(self.ruler)


#     def alignPhys(self):
#         self.ruler.set_position(*self.rulerBody.position)
#         self.ruler.rotation = self.rulerBody.angle




    # def hitPlayer(self, player):
    #     pass

    #self.head
    #self.head_attach = pm.Body(mass, pm.moment_for_box(mass, 40, 40))
    #head  = pm.Poly(self.head_attach, [[0,0],[40,0],[40,40],[0,40]])
    #head.friction = 1
    #self.head_attach.position = self.body.position + (0,50)

# Useful example code
