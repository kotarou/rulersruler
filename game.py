from __future__ import division, print_function, unicode_literals

import random
import math
import os, sys

import pyglet
from pyglet.window import key
from pyglet.gl import *

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
            key.Q: 'p1larm',
            key.W: 'p1rarm',
            key.A: 'p1lleg',
            key.S: 'p1rleg',
            key.I: 'p2larm',
            key.O: 'p2rarm',
            key.K: 'p2lleg',
            key.L: 'p2rleg',
        }
}

character1 = character2 = "0"

space = pm.Space()
space.gravity = Vec2d(0.0, -900.0)
logo_img = pyglet.resource.image('pymunk_logo_googlecode.png')
batch = pyglet.graphics.Batch()
# world to view scales

# class Actor(cocos.sprite.Sprite):
#     palette = {}  # injected later

#     def __init__(self, cx, cy, radius, btype, img, vel=None):
#         super(Actor, self).__init__(img)
#         # the 1.05 so that visual radius a bit greater than collision radius
#         # self.scale = (radius * 1.05) * scale_x / (self.image.width / 2.0)
#         # self.btype = btype
#         # self.color = self.palette[btype]
#         # self.cshape = cm.CircleShape(eu.Vector2(cx, cy), radius)
#         self.update_center(self.cshape.center)
#         if vel is None:
#             vel = eu.Vector2(0.0, 0.0)
#         self.vel = vel
#         self.larm = eu.Line2(Point2(0,20),Point2(10,40))
#         self.rarm = eu.Line2(Point2(20,20),Point2(10,40))
#         self.lleg = eu.Line2(Point2(10,20), Point2(0,0))
#         self.rleg = eu.Line2(Point2(10,20), Point2(20,0))
#         self.body = eu.Line2(Point2(10,20), Point2(10,40))
#         self.head = Rect(0,0, 200, 100)



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
    def __init__(self):
        global character1
        # self.target = Sprite('Assets/crownrb.png')
        # self.larm = Sprite('Assets/00' + character1 + 'charrarm.png')
        # self.larm.position = (-15, -80)
        # self.larm.anchor = (0,20)
        # self.larm.rotation = (90)
        # self.rarm = Sprite('Assets/00' + character1 + 'charlarm.png')
        # self.rarm.position = (15, -80)
        # self.rarm.anchor = (0, 20)
        # self.rarm.rotation = (-90)
        # self.body = Sprite('Assets/00' + character1 + 'charbody.png')
        # self.body.position = (0, -80)
        # self.body.anchor = (0, 20)
        # self.lleg = Sprite('Assets/00' + character1 + 'charlleg.png')
        # self.lleg.position = (-15, -120)
        # self.lleg.anchor = (0, 20)
        # self.lleg.rotation = (90)
        # self.rleg = Sprite('Assets/00' + character1 + 'charrleg.png')
        # self.rleg.position = (15, -120)
        # self.rleg.anchor = (0, 20)
        # self.rleg.rotation = (-90)

        # self.target.add(self.head)
        # self.target.add(self.larm)
        # self.target.add(self.rarm)
        # self.target.add(self.body)
        # self.target.add(self.lleg)
        # self.target.add(self.rleg)

        # self.s = pm.Poly(self.b, [(0, -50), (50, 0), (30, 50),(-30, 50),(-50, 0)], (0,-100))
        # space.add(self.s)

        # The root node's location
        mass = 100

        self.body = pm.Body(100, pm.moment_for_box(mass, 40, 60))  # mass, moment
        self.body.position = 100, 200  #random.randint(20,400), 200
        self.body.angle = 0  # random.random() * math.pi

        # moment = pm.moment_for_box(mass, 20, 30)
        # self.body = pm.Body(mass, moment)
        #

        self.torso  = Sprite('Assets/00' + character1 + 'charbody.png')
        torso  = pm.Poly.create_box(self.body, size=(40, 60), offset=(0,0))
        torso.friction = 1

        self.head   = Sprite('Assets/00' + character1 + 'charhead.png')
        self.head_attach = pm.Body(mass, pm.moment_for_box(mass, 40, 40))
        head  = pm.Poly.create_box(self.head_attach, size=(40, 40), offset=(0,0))
        head.friction = 1
        self.head_attach.position = self.body.position + (0,65)

        self.larm   = Sprite('Assets/00' + character1 + 'charlarm.png')
        self.larm_attach = pm.Body(mass, pm.moment_for_box(mass, 20, 60))
        larm  = pm.Poly.create_box(self.larm_attach, size=(20, 60), offset=(0,0))
        larm.friction = 1
        self.larm_attach.position = self.body.position + (-20,40)

        self.rarm   = Sprite('Assets/00' + character1 + 'charrarm.png')
        self.rarm_attach = pm.Body(mass, pm.moment_for_box(mass, 20, 60))
        rarm  = pm.Poly.create_box(self.rarm_attach, size=(20, 60), offset=(0,0))
        rarm.friction = 1
        self.rarm_attach.position = self.body.position + (40,40)

        self.lleg   = Sprite('Assets/00' + character1 + 'charlleg.png')
        self.lleg_attach = pm.Body(mass, pm.moment_for_box(mass, 20, 60))
        lleg  = pm.Poly.create_box(self.lleg_attach, size=(20, 60), offset=(0,0))
        lleg.friction = 1
        self.lleg_attach.position = self.body.position + (-5,-65)

        self.rleg   = Sprite('Assets/00' + character1 + 'charrleg.png')
        self.rleg_attach = pm.Body(mass, pm.moment_for_box(mass, 20, 60))
        rleg  = pm.Poly.create_box(self.rleg_attach, size=(20, 60), offset=(0,0))
        rleg.friction = 1
        self.rleg_attach.position = self.body.position + (15,-65)


        body_head = pm.PinJoint(self.body, self.head_attach, (20,60), (20,0))
        body_head.distance = 5
        body_larm = pm.PinJoint(self.body, self.larm_attach, (0,60), (20,60))
        body_larm.distance = 5
        body_rarm = pm.PinJoint(self.body, self.rarm_attach, (40,60), (0,60))
        body_rarm.distance = 5
        body_lleg = pm.PinJoint(self.body, self.lleg_attach, (10,0), (20,60))
        body_lleg.distance = 5
        body_rleg = pm.PinJoint(self.body, self.rleg_attach, (30,0), (0,60))
        body_rleg.distance = 5

        space.add(self.body, self.head_attach, self.larm_attach, self.rarm_attach, self.lleg_attach, self.rleg_attach,
                  body_head, body_larm, body_rarm, body_lleg, body_rleg,
                  head, torso, larm, rarm, lleg, rleg)


    def alignPhys(self):
        self.head.set_position(*self.head_attach.position)
        self.torso.set_position(*self.body.position)
        self.larm.set_position(*self.larm_attach.position)
        self.rarm.set_position(*self.rarm_attach.position)
        self.lleg.set_position(*self.lleg_attach.position)
        self.rleg.set_position(*self.rleg_attach.position)

    def addComponents(self, layer):
        layer.add(self.lleg)
        layer.add(self.rleg)
        layer.add(self.larm)
        layer.add(self.rarm)
        layer.add(self.head)
        layer.add(self.torso)
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

    def __init__(self, scene, c1, c2):
        super(Worldview, self).__init__()

        global keyboard
        keyboard = key.KeyStateHandler()
        director.window.push_handlers(keyboard)

        # Setup the character sprites
        global character1
        character1 = c1
        character2 = c2

        palette = consts['view']['palette']
        #Actor.palette = palette
        #r, g, b = palette['bg']
        #scene.add(cocos.layer.ColorLayer(r, g, b, 255), z=-1)
        message_layer = MessageLayer()
        player_layer = Layer()
        scene.add(message_layer, z=1)
        scene.add(player_layer,z=2)
        self.fn_show_message = message_layer

        self.player = Me()
        self.player.addComponents(player_layer)

        self.bindings = world['bindings']
        buttons = {}
        for k in self.bindings:
            buttons[self.bindings[k]] = 0
        self.buttons = buttons

        self.schedule(self.update)

        # Physics stuff
        # The ground has lines ontop of it
        static_body = pm.Body()
        self.static_lines = [pm.Segment(static_body, (0.0, 50.0), (800.0, 50.0), 0.0),
                        pm.Segment(static_body, (0, 0), (0, 400), 0.0),
                        pm.Segment(static_body, (800, 0), (800, 400), 0.0)
                        ]
        for l in self.static_lines:
            l.friction = 0.5
        space.add(self.static_lines)

        # static_body = pm.Body()
        # static_lines = [pm.Segment(static_body, (111.0, 280.0), (407.0, 246.0), 0.0)
        #                 ,pm.Segment(static_body, (407.0, 246.0), (407.0, 343.0), 0.0)
        #                 ]
        # for line in static_lines:
        #     line.elasticity = 0.95
        # space.add(static_lines)

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

    def update(self, dt):

        self.player.alignPhys()
        #pymunk.pyglet_util.draw(space)
        # for line in self.static_lines:
        #     body = line.body

        #     pv1 = body.position + line.a.rotated(body.angle)
        #     pv2 = body.position + line.b.rotated(body.angle)
        #     pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
        #         ('v3f', (pv1.x,pv1.y,20,pv2.x,pv2.y,20)),
        #         ('c3f', (.8,.8,.8)*2)
        #         )

        #print(self.player.sprite.position)


        pdt = 1.0/60. #override dt to keep physics simulation stable
        space.step(pdt)


        # # interactions player - others
        # for other in self.collman.iter_colliding(me):
        #     print(other.btype)
            # typeball = other.btype
            # if typeball == 'food':
            #     self.toRemove.add(other)
            #     self.cnt_food -= 1
            #     if not self.cnt_food:
            #         self.open_gate()

            # elif (typeball == 'wall' or
            #       typeball == 'gate' and self.cnt_food > 0):
            #     self.level_losed()

            # elif typeball == 'gate':
            #     self.level_conquered()

        # update player
        buttons = self.buttons

        # Check key presses
        rot = buttons['p1larm']
        if rot != 0:
            self.player.larm.rotation = self.player.larm.rotation  + 10
        rot = buttons['p1rarm']
        if rot != 0:
            self.player.rarm.rotation = self.player.rarm.rotation  + 10
        rot = buttons['p1lleg']
        if rot != 0:
            self.player.lleg.rotation = self.player.lleg.rotation  + 10
        rot = buttons['p1rleg']
        if rot != 0:
            self.player.rleg.rotation = self.player.rleg.rotation  + 10



