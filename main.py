#
# cocos2d
# http://python.cocos2d.org
#
# Particle Engine done by Phil Hassey
# http://www.imitationpickles.org
#

from __future__ import division, print_function, unicode_literals

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
character1 = "0"
character2 = "0"

pyglet.resource.path = ['Assets']
pyglet.resource.reindex()
# Fix strange resource loading bug
slash_paths = filter(lambda x: x.startswith('/'), pyglet.resource._default_loader._index.keys())
for path in slash_paths:
    pyglet.resource._default_loader._index[path[1:]] = pyglet.resource._default_loader._index[path]


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

        items.append(MenuItem('QuickStart', self.on_quick_start))
        items.append(MenuItem('New Game', self.on_new_game))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('Scores', self.on_scores))
        items.append(MenuItem('Quit', self.on_quit))

        self.create_menu(items)

    # Callbacks

    def on_quick_start(self):
        global character1, character2
        character1 = "1"
        character2 = "2"
        scene = cocos.scene.Scene()
        backgroundLayer = BackgroundLayer('001background.png')
        scene.add(backgroundLayer, z=1)
        print("asdf", character1)
        playview = Worldview(scene, character1, character2)
        scene.add(playview, z=0)
        director.push(scene)
        print("on_new_game()")

    def on_new_game(self):
        self.parent.switch_to(4)

    def on_scores(self):
        self.parent.switch_to(2)

    def on_options(self):
        self.parent.switch_to(1)

    def on_quit(self):
        director.pop()

class LevelMenu(Menu):

    def __init__(self):
        super(LevelMenu, self).__init__("Levels")

        print("hjhjhj", character1)

        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []
        items.append(ImageMenuItem('001backgroundPreview.png', self.on_level_select_1))
        items.append(ImageMenuItem('002backgroundPreview.png', self.on_level_select_2))
        items.append(MenuItem('BACK', self.on_quit))
        self.create_menu(items)

    def on_level_select_1(self):
        global character1
        scene = cocos.scene.Scene()
        backgroundLayer = BackgroundLayer('001background.png')
        scene.add(backgroundLayer, z=1)
        print("asdf", character1)
        playview = Worldview(scene, character1, character2)
        scene.add(playview, z=0)
        director.push(scene)
        print("on_new_game()")

    def on_level_select_2(self):
        global character1
        print("asdf", character1)
        scene = cocos.scene.Scene()
        backgroundLayer = BackgroundLayer('002background.png')
        scene.add(backgroundLayer, z=1)
        playview = Worldview(scene, character1, character2)
        scene.add(playview, z=0)
        director.push(scene)
        print("on_new_game()")

    def on_quit(self):
        self.parent.switch_to(4)


class BackgroundLayer(cocos.layer.Layer):
    """Background layer for all the game."""

    def __init__(self, backgroundIn):
        super(BackgroundLayer, self).__init__()
        self.sp = Sprite(backgroundIn) #creates a sprite from the imagefile in the pathname
        w, h = director.get_window_size() #gets the size of the window
        self.sp.scale = h / self.sp.height #scales the background image to the size of the window
        self.sp.position = w//2, h//2 #centers the scaled background iamge
        self.add(self.sp) #adds the background image to be rendered

class CharacterMenu(Menu):

    def __init__(self):
        super(CharacterMenu, self).__init__("Characters")

        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []

        items.append(ImageMenuItem('001charhead.png', self.on_001char_select))
        items.append(ImageMenuItem('002charhead.png', self.on_002char_select))
        items.append(MenuItem('BACK', self.on_quit))
        self.create_menu(items)

    def on_001char_select(self):
        global character1, character2
        character1 = "1"
        character2 = "2"
        self.parent.switch_to(3)

    def on_002char_select(self):
        global character1, character2
        character2 = "1"
        character1 = "2"
        self.parent.switch_to(3)

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

    menulayer = MultiplexLayer(MainMenu(), OptionMenu(), ScoreMenu(), LevelMenu(), CharacterMenu())

    scene = Scene(menulayer)
    return scene


def run(scene):
    director.run(scene)

if __name__ == "__main__":
    init()
    s = start()
    run(s)
