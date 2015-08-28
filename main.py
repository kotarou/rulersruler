#
# cocos2d
# http://python.cocos2d.org
#
# Particle Engine done by Phil Hassey
# http://www.imitationpickles.org
#

from __future__ import division, print_function, unicode_literals
import six

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
from pyglet.gl import *

from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *
from cocos.actions import *
from cocos.sprite import Sprite

import random

from game import *

rr = random.randrange

class MainMenu(Menu):

    def __init__(self):

        # call superclass with the title
        super(MainMenu, self).__init__("Ruler's Ruler")

        pyglet.font.add_directory('.')

        # you can override the font that will be used for the title and the items
        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        # you can also override the font size and the colors. see menu.py for
        # more info

        # example: menus can be vertical aligned and horizontal aligned
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []

        items.append(MenuItem('New Game', self.on_new_game))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('Scores', self.on_scores))
        items.append(MenuItem('Quit', self.on_quit))

        self.create_menu(items)

    # Callbacks

    def on_new_game(self):
        self.parent.switch_to(3)

    def on_scores(self):
        self.parent.switch_to(2)

    def on_options(self):
        self.parent.switch_to(1)

    def on_quit(self):
        director.pop()

class LevelMenu(Menu):

    def __init__(self):
        super(LevelMenu, self).__init__("Levels")

        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []
        items.append(ImageMenuItem('Assets/backgroundPreview.png', self.on_new_game))
        items.append(MenuItem('BACK', self.on_quit))
        self.create_menu(items)

    def on_new_game(self):
        scene = cocos.scene.Scene()
        playview = Worldview(scene)
        scene.add(playview, z=0)
        director.push(scene)
        print("on_new_game()")

    def on_quit(self):
        self.parent.switch_to(0)

class OptionMenu(Menu):

    def __init__(self):
        super(OptionMenu, self).__init__("Options")

        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        self.menu_valign = BOTTOM
        self.menu_halign = RIGHT

        items = []
        items.append(MenuItem('Fullscreen', self.on_fullscreen))
        items.append(ToggleMenuItem('Show FPS: ', self.on_show_fps, True))
        items.append(MenuItem('OK', self.on_quit))
        self.create_menu(items)

    # Callbacks
    def on_fullscreen(self):
        director.window.set_fullscreen(not director.window.fullscreen)

    def on_quit(self):
        self.parent.switch_to(0)

    def on_show_fps(self, value):
        director.show_FPS = value


class ScoreMenu(Menu):

    def __init__(self):
        super(ScoreMenu, self).__init__("Scores")

        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72
        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        self.menu_valign = BOTTOM
        self.menu_halign = LEFT

        self.create_menu([MenuItem('Go Back', self.on_quit)])

    def on_quit(self):
        self.parent.switch_to(0)


def init():
    director.init(resizable=True, width=640, height=480)


def start():
    director.set_depth_test()

    menulayer = MultiplexLayer(MainMenu(), OptionMenu(), ScoreMenu(), LevelMenu())

    scene = Scene(menulayer)
    return scene


def run(scene):
    director.run(scene)

if __name__ == "__main__":
    init()
    s = start()
    run(s)
