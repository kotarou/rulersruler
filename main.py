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

mplayer = music.makeplayer()

class MainMenu(Menu):

    def __init__(self):
        global player1, player2, player3, player4
        # call superclass with the title
        super(MainMenu, self).__init__("Ruler's Ruler")

        player1 = Player('0', [], 0)
        player2 = Player('0', [], 1)
        player3 = Player('0', [], 2)
        player4 = Player('0', [], 3)
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

        music.queue_menu(mplayer)
        #music.play('pearknight.mp3')

    # Callbacks

    def on_quick_start(self):
        global player1, player2, player3, player4
        player1.select("1")
        player2.select("2")
        player3.select("3")
        player4.select("4")
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
        items.append(ImageMenuItem('002backgroundPreview.png', self.levelSelect, 2))
        items.append(ImageMenuItem('003backgroundPreview.png', self.levelSelect, 3))
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
        global player1, player2, player3, player4
        super(CharacterMenu, self).__init__("Player " + str(player))

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
        self.items.append(ImageMenuItem('003charhead.png', self.charSelect, 3))
        self.items.append(ImageMenuItem('004charhead.png', self.charSelect, 4))
        self.items.append(MenuItem('BACK', self.on_quit))
        self.create_menu(self.items)

    def charSelect(self, char):
        global player1, player2, player3, player4
        if self.player == 1:
            player1.select(str(char))
            self.parent.switch_to(5)
        if self.player == 2:
            if str(char) == player1.charSprite:
                self.parent.switch_to(5)
            else:
                player2.select(str(char))
                self.parent.switch_to(6)
        if self.player == 3:
            if str(char) == player1.charSprite or str(char) == player2.charSprite:
                self.parent.switch_to(5)
            else:
                player3.select(str(char))
                self.parent.switch_to(7)
        if self.player == 4:
            if str(char) == player1.charSprite or str(char) == player2.charSprite or str(char) == player3.charSprite:
                self.parent.switch_to(5)
            else:
                player4.select(str(char))
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
        self.crowns.append(self.random_crown())
        self.update()

    def lose(self):
        try:
            self.crowns.pop()
        except Exception:
            pass
        self.update()

    def random_crown(self):
        opt_crowns = [
        "001crown.png",
        "002crown.png",
        "003crown.png",
        "004crown.png",
        "005crown.png",
        "006crown.png",
        "007crown.png",
        "008crown.png",
        "009crown.png",
        "010crown.png",
        "011crown.png",
        "012crown.png",
        "013crown.png",
        ]
        return random.choice(opt_crowns)

    def select(self, char):
        self.charSprite = char

class RoundManager():

    def __init__(self):
        self.gamestate = ""
        #music.play('pearknight.mp3')


    def level_start(self, backgroundPathIn):
        global player1, player2, player3, player4
        self.gamestate = 'round start'

        self.backgroundPathIn = backgroundPathIn
        music.queue_random(mplayer)

        scene = cocos.scene.Scene()
        backgroundLayer = BackgroundLayer(backgroundPathIn)
        scene.add(backgroundLayer, z=1)
        self.playview = Worldview(scene, player1, player2, player3, player4, self)
        scene.add(self.playview, z=0)
        director.push(scene)

    def player_win(self, winner):
        if winner == 1:
            player1.win()
            player2.lose()
            player3.lose()
            player4.lose()
        if winner == 2:
            player2.win()
            player1.lose()
            player3.lose()
            player4.lose()
        if winner == 3:
            player3.win()
            player1.lose()
            player2.lose()
            player4.lose()
        if winner == 4:
            player4.win()
            player1.lose()
            player2.lose()
            player3.lose()
        self.genwinmessage(winner)
        self.gamestate = 'round end'
        music.queue_random(mplayer)
        print(player1.crowns)
        if (len(player1.crowns) > 5):
            director.scene.end()
        if (len(player2.crowns) > 5):
            director.scene.end()
        if (len(player3.crowns) > 5):
            director.scene.end()
        if (len(player4.crowns) > 5):
            director.scene.end()

    def genwinmessage(self, winner):
        pass

    def reset_round(self):
        self.playview.restart()
        # any cleanup goes here, or ending the system
        director.push(director.pop())



def init():
    director.init(resizable=True, width=640, height=480)


def start():
    director.set_depth_test()

    menulayer = MultiplexLayer(MainMenu(), OptionMenu(), ScoreMenu(), LevelMenu(), CharacterMenu(1), CharacterMenu(2), CharacterMenu(3), CharacterMenu(4))

    scene = Scene(menulayer)
    return scene


def run(scene):

    director.run(scene)

if __name__ == "__main__":
    init()
    s = start()
    run(s)
