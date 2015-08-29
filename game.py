from __future__ import division, print_function, unicode_literals

import random
import math

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



    # def update_center(self, cshape_center):
    #     """cshape_center must be eu.Vector2"""
    #     self.position = world_to_view(cshape_center)
    #     self.cshape.center = cshape_center


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
        self.target = Sprite('Assets/crownrb.png')
        self.head = Sprite('Assets/charhead.png')
        self.head.position = (0, -35)
        self.head.anchor = (0, 20)
        self.larm = Sprite('Assets/charrarm.png')
        self.larm.position = (-15, -80)
        self.larm.anchor = (0,20)
        self.larm.rotation = (90)
        self.rarm = Sprite('Assets/charlarm.png')
        self.rarm.position = (15, -80)
        self.rarm.anchor = (0, 20)
        self.rarm.rotation = (-90)
        self.body = Sprite('Assets/charbody.png')
        self.body.position = (0, -80)
        self.body.anchor = (0, 20)
        self.lleg = Sprite('Assets/charlleg.png')
        self.lleg.position = (-15, -120)
        self.lleg.anchor = (0, 20)
        self.lleg.rotation = (90)
        self.rleg = Sprite('Assets/charrleg.png')
        self.rleg.position = (15, -120)
        self.rleg.anchor = (0, 20)
        self.rleg.rotation = (-90)

        self.target.add(self.head)
        self.target.add(self.larm)
        self.target.add(self.rarm)
        self.target.add(self.body)
        self.target.add(self.lleg)
        self.target.add(self.rleg)

        self.target.position = (100, 140)
        self.target.velocity = (0, 0)

    # def step(self, dt):
    #     super(Me, self).step(dt) # Run step function on the parent class.
    #     # Determine velocity based on keyboard inputs.
    #     # velocity_x = 100 * (keyboard[key.RIGHT] - keyboard[key.LEFT])
    #     # velocity_y = 100 * (keyboard[key.UP] - keyboard[key.DOWN])
    #     # # Set the object's velocity.
    #     self.larm.target.dr = 100 * keyboard[key.Q]

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

    def __init__(self, scene):
        super(Worldview, self).__init__()

        global keyboard
        keyboard = key.KeyStateHandler()
        director.window.push_handlers(keyboard)


        palette = consts['view']['palette']
        #Actor.palette = palette
        #r, g, b = palette['bg']
        #scene.add(cocos.layer.ColorLayer(r, g, b, 255), z=-1)
        message_layer = MessageLayer()
        player_layer = Layer()
        scene.add(message_layer, z=1)
        scene.add(player_layer,z=2)
        self.fn_show_message = message_layer

        global me
        me = Me()

        player_layer.add(me.target)

        self.bindings = world['bindings']
        buttons = {}
        for k in self.bindings:
            buttons[self.bindings[k]] = 0
        self.buttons = buttons

        self.schedule(self.update)



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

        # update player
        buttons = self.buttons

        rot = buttons['p1larm']
        if rot != 0:
            me.larm.rotation = me.larm.rotation  + 10
        rot = buttons['p1rarm']
        if rot != 0:
            me.rarm.rotation = me.rarm.rotation  + 10
        rot = buttons['p1lleg']
        if rot != 0:
            me.lleg.rotation = me.lleg.rotation  + 10
        rot = buttons['p1rleg']
        if rot != 0:
            me.rleg.rotation = me.rleg.rotation  + 10

