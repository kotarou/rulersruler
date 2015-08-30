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

import music
import random

from game import *

rr = random.randrange

pyglet.resource.path = ['Assets']
pyglet.resource.reindex()
# Fix strange resource loading bug
slash_paths = filter(lambda x: x.startswith('/'), pyglet.resource._default_loader._index.keys())
for path in slash_paths:
    pyglet.resource._default_loader._index[path[1:]] = pyglet.resource._default_loader._index[path]


class MainMenu(Menu):

    def __init__(self):
        global player1, player2
        # call superclass with the title
        super(MainMenu, self).__init__("Ruler's Ruler")

        player1 = Player('0', [], 0)
        player2 = Player('0', [], 1)

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
        global player1, player1
        player1.select("1")
        player2.select("2")
        roundmanager = RoundManager()
        roundmanager.level_start('002background.png')

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

        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []
        items.append(ImageMenuItem('001backgroundPreview.png', self.levelSelect, 1))
        items.append(ImageMenuItem('002backgroundPreview.png', self.levelSelect, 1))
        items.append(MenuItem('BACK', self.on_quit))
        self.create_menu(items)

    def levelSelect(self, level):
        roundmanager = RoundManager()
        roundmanager.level_start('00' + str(level) + 'background.png')

    def on_quit(self):
        self.parent.switch_to(4)


class BackgroundLayer(cocos.layer.Layer):
    """Background layer for all the game."""

    def __init__(self, backgroundIn):
        super(BackgroundLayer, self).__init__()
        self.sp = Sprite(backgroundIn)  # creates a sprite from the imagefile in the pathname
        w, h = director.get_window_size()  # gets the size of the window
        self.sp.scale = h / self.sp.height  # scales the background image to the size of the window
        self.sp.position = w//2, h//2  # centers the scaled background iamge
        self.add(self.sp)  # adds the background image to be rendered

class CharacterMenu(Menu):

    def __init__(self, player):
        global player1, player2
        super(CharacterMenu, self).__init__("Characters")

        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        self.menu_valign = CENTER
        self.menu_halign = CENTER

        self.items = []
        self.player = player

        self.items.append(ImageMenuItem('001charhead.png', self.charSelect, 1))
        self.items.append(ImageMenuItem('002charhead.png', self.charSelect, 2))
        self.items.append(MenuItem('BACK', self.on_quit))
        self.create_menu(self.items)

    def charSelect(self, char):
        global player1, player2
        if self.player == 1:
            player1.select(str(char))
            self.parent.switch_to(5)
        if self.player == 2:
            if str(char) == player1.charSprite:
                self.parent.switch_to(5)
            else:
                player2.select(str(char))
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

class Player():
    def __init__(self, charSprite, crowns, side):
        self.charSprite = charSprite
        self.crowns = crowns
        self.wins = len(crowns)
        self.side = side

    def update(self):
        self.wins = len(self.crowns)

    def win(self):
        self.crowns.append('crownrb.png')
        self.update()

    def select(self, char):
        self.charSprite = char

class RoundManager():

    def __init__(self):
        self.gamestate = ""

        music.play('pearknight.mp3')


    def level_start(self, backgroundPathIn):
        global player1, player2
        self.gamestate = 'round start'
        self.backgroundPathIn = backgroundPathIn
        scene = cocos.scene.Scene()
        backgroundLayer = BackgroundLayer(backgroundPathIn)
        scene.add(backgroundLayer, z=1)
        self.playview = Worldview(scene, player1, player2, self)
        scene.add(self.playview, z=0)
        director.push(scene)

    def player_win(self, winner):
        if winner == 1:
            player1.win()
        self.genwinmessage(winner)
        self.gamestate = 'round end'
        self.reset_round()

    def genwinmessage(self, winner):
        print("player " + str(winner) + "has won")

    def crown(self, winner):
        pass
        # give winner a crown

    def reset_round(self):
        self.playview.restart()
        # any cleanup goes here, or ending the system
        director.push(director.pop())



def init():
    director.init(resizable=True, width=640, height=480)


def start():
    director.set_depth_test()

    menulayer = MultiplexLayer(MainMenu(), OptionMenu(), ScoreMenu(), LevelMenu(), CharacterMenu(1), CharacterMenu(2))

    scene = Scene(menulayer)
    return scene


def run(scene):

    director.run(scene)

if __name__ == "__main__":
    init()
    s = start()
    run(s)
