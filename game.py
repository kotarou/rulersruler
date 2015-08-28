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
    "world": {
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

# world to view scales
scale_x = consts["window"]["width"] / consts["world"]["width"]
scale_y = consts["window"]["height"] / consts["world"]["height"]


def world_to_view(v):
    """world coords to view coords; v an eu.Vector2, returns (float, float)"""
    return v.x * scale_x, v.y * scale_y


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
        palette = consts['view']['palette']
        #Actor.palette = palette
        r, g, b = palette['bg']
        scene.add(cocos.layer.ColorLayer(r, g, b, 255), z=-1)
        message_layer = MessageLayer()
        player_layer = Layer()
        scene.add(message_layer, z=1)
        scene.add(player_layer,z=2)
        self.fn_show_message = message_layer
        me = Sprite('Assets/crownrb.png')
        player_layer.add(me)
        me.position = (100, 100)
        me.velocity = (0, 0)
    #     # basic geometry
    #     world = consts['world']
    #     self.width = world['width']  # world virtual width
    #     self.height = world['height']  # world virtual height
    #     self.rPlayer = world['rPlayer']  # player radius in virtual space
    #     self.wall_scale_min = world['wall_scale_min']
    #     self.wall_scale_max = world['wall_scale_max']
    #     self.topSpeed = world['topSpeed']
    #     self.angular_velocity = world['angular_velocity']
    #     self.accel = world['accel']

    #     # load resources:
    #     pics = {}
    #     pics["player"] = pyglet.resource.image('player7.png')
    #     pics["food"] = pyglet.resource.image('circle6.png')
    #     pics["wall"] = pyglet.resource.image('circle6.png')
    #     self.pics = pics

    #     cell_size = self.rPlayer * self.wall_scale_max * 2.0 * 1.25
    #     self.collman = cm.CollisionManagerGrid(0.0, self.width,
    #                                            0.0, self.height,
    #                                            cell_size, cell_size)

    #     self.bindings = world['bindings']
    #     buttons = {}
    #     for k in self.bindings:
    #         buttons[self.bindings[k]] = 0
    #     self.buttons = buttons

    #     self.toRemove = set()
    #     self.schedule(self.update)
    #     self.ladder_begin()

    # def ladder_begin(self):
    #     self.level_num = 0
    #     self.empty_level()
    #     msg = 'balldrive'
    #     self.fn_show_message(msg, callback=self.level_launch)

    # def level_launch(self):
    #     self.generate_random_level()
    #     msg = 'level %d' % self.level_num
    #     self.fn_show_message(msg, callback=self.level_start)

    # def level_start(self):
    #     self.win_status = 'undecided'

    # def level_conquered(self):
    #     self.win_status = 'intermission'
    #     msg = 'level %d\nconquered !' % self.level_num
    #     self.fn_show_message(msg, callback=self.level_next)

    # def level_losed(self):
    #     self.win_status = 'losed'
    #     msg = 'ouchhh !!!'
    #     self.fn_show_message(msg, callback=self.ladder_begin)

    # def level_next(self):
    #     self.empty_level()
    #     self.level_num += 1
    #     self.level_launch()

    # def empty_level(self):
    #     # del old actors, if any
    #     for node in self.get_children():
    #         self.remove(node)
    #     assert len(self.children) == 0
    #     self.player = None
    #     self.gate = None
    #     self.food_cnt = 0
    #     self.toRemove.clear()

    #     self.win_status = 'intermission'  # | 'undecided' | 'conquered' | 'losed'

    #     # player phys params
    #     self.topSpeed = 75.0  # 50.
    #     self.impulse_dir = eu.Vector2(0.0, 1.0)
    #     self.impulseForce = 0.0

    # def generate_random_level(self):
    #     # Generate a random player location (x, y)
    #     # Choose a random background color
    #     # etc
    #     # build !
    #     width = self.width
    #     height = self.height

    #     # add player
    #     cx, cy = (0.5 * width, 0.5 * height)
    #     self.player = Actor(cx, cy, rPlayer, 'player', pics['player'])
    #     self.collman.add(self.player)


    #     self.add(self.player, z=z)
    #     z += 1

    # def update(self, dt):
    #     # if not playing dont update model
    #     if self.win_status != 'undecided':
    #         return

    #     # update collman
    #     self.collman.clear()
    #     for z, node in self.children:
    #         self.collman.add(node)

    #     # interactions player - others
    #     for other in self.collman.iter_colliding(self.player):
    #         typeball = other.btype
    #         if typeball == 'food':
    #             self.toRemove.add(other)
    #             self.cnt_food -= 1
    #             if not self.cnt_food:
    #                 self.open_gate()

    #         elif (typeball == 'wall' or
    #               typeball == 'gate' and self.cnt_food > 0):
    #             self.level_losed()

    #         elif typeball == 'gate':
    #             self.level_conquered()

    #     # update player
    #     buttons = self.buttons
    #     ma = buttons['right'] - buttons['left']
    #     if ma != 0:
    #         self.player.rotation += ma * dt * self.angular_velocity
    #         a = math.radians(self.player.rotation)
    #         self.impulse_dir = eu.Vector2(math.sin(a), math.cos(a))

    #     newVel = self.player.vel
    #     mv = buttons['up']
    #     if mv != 0:
    #         newVel += dt * mv * self.accel * self.impulse_dir
    #         nv = newVel.magnitude()
    #         if nv > self.topSpeed:
    #             newVel *= self.topSpeed / nv

    #     ppos = self.player.cshape.center
    #     newPos = ppos
    #     r = self.player.cshape.r
    #     while dt > 1.e-6:
    #         newPos = ppos + dt * newVel
    #         consumed_dt = dt
    #         # what about screen boundaries ? if colision bounce
    #         if newPos.x < r:
    #             consumed_dt = (r - ppos.x) / newVel.x
    #             newPos = ppos + consumed_dt * newVel
    #             newVel = -reflection_y(newVel)
    #         if newPos.x > (self.width - r):
    #             consumed_dt = (self.width - r - ppos.x) / newVel.x
    #             newPos = ppos + consumed_dt * newVel
    #             newVel = -reflection_y(newVel)
    #         if newPos.y < r:
    #             consumed_dt = (r - ppos.y) / newVel.y
    #             newPos = ppos + consumed_dt * newVel
    #             newVel = reflection_y(newVel)
    #         if newPos.y > (self.height - r):
    #             consumed_dt = (self.height - r - ppos.y) / newVel.y
    #             newPos = ppos + consumed_dt * newVel
    #             newVel = reflection_y(newVel)
    #         dt -= consumed_dt

    #     self.player.vel = newVel
    #     self.player.update_center(newPos)

    #     # at end of frame do removes; as collman is fully regenerated each frame
    #     # theres no need to update it here.
    #     for node in self.toRemove:
    #         self.remove(node)
    #     self.toRemove.clear()

    # def open_gate(self):
    #     self.gate.color = Actor.palette['gate']

    def on_key_press(self, k, m):
        binds = self.bindings
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
