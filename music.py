#
# original file from http://www.partiallydisassembled.net/make_me/
# modified later for this game, 
# then modified for pxljam by Till
#

from __future__ import division, print_function, unicode_literals
import os
MUSIC = True
SOUND = True
import time
import pyglet
pyglet.lib.load_library('avbin')
pyglet.have_avbin=True
import pyglet.media.avbin
have_avbin = True
import random
#
# MUSIC
#

sound_vol = 0.7
volume = 0.4

def makeplayer():
    return pyglet.media.Player()


def set_music(name, mplayer):
    #print(mplayer.playing)
    #print(mplayer.source)
    #global current_music

    #if name == current_music:
    #    return

    current_music = name

    #if not MUSIC:
    #    return

    #music_player.next()
    mplayer.next()
    mplayer.queue(pyglet.resource.media(name, streaming=True))
    #mplayer.next()
    #print(mplayer.source)
    mplayer.play()
    # pyglet bug
    mplayer.volume = volume
    mplayer.eos_action = 'loop'

def music_volume(vol):
    music_player.volume=vol

def queue_music(name):
    global current_music
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.eos_action = 'next'


def play_music():
    if music_player.playing or not current_music:
        return
    name = current_music
    music_player.next()
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.play()
    music_player.eos_action = 'loop'

# @music_player.event
# def on_eos():
#     music_player.eos_action = 'loop'


# def stop_music():
#     print(music_player.playing)
#     music_player.pause()
#     print(music_player.playing)
# #
# # SOUND
# #
# sounds = {}

# def load(name, streaming=False):
#     if not SOUND:
#         return

#     if name not in sounds:
#         sounds[name] = pyglet.resource.media(name, streaming=streaming)

#     return sounds[name]

def play(name):
    if not SOUND:
        return
    load(name)
    a = sounds[name].play().volume = sound_vol

# def sound_volume( vol ):
#     global sound_vol
#     sound_vol = vol

# def play_whack():
#     play('whack.mp3')

# def testaud():
#     print("foo")
#     #play('tswin.mp3')
#     set_music('tswin.mp3')
#     queue_music('speech.wav')
#     #music_player.play()
#     #play_music()
#     print(music_player.playing)
#     print("done")
#     time.sleep(10)

def queue_random(mplayer):
    songs = ['citiesoftunnels.mp3',
    'demoscenessimp.mp3',
    'tearfulgardens.mp3',
    'birdsviking.mp3',]
    a = random.choice(songs)
    set_music(a, mplayer)

def queue_menu(mplayer):
    set_music('pearknight.mp3', mplayer)
