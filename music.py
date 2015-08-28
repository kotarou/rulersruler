#
# original file from http://www.partiallydisassembled.net/make_me/
# modified later for this game, 
# then modified for pxljam by Till
#

from __future__ import division, print_function, unicode_literals

MUSIC = True
SOUND = True
import time
import pyglet
import pyglet.media.avbin
have_avbin = True
MUSIC = True
SOUND = True

#
# MUSIC
#

music_player = pyglet.media.Player()
current_music = None

sound_vol = 0.7
music_player.volume = 0.4

def set_music(name):
    print('set music')
    global current_music

    if name == current_music:
        return

    current_music = name

    if not MUSIC:
        return

    music_player.next()
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.play()
    # pyglet bug
    music_player.volume = music_player.volume
    music_player.eos_action = 'loop'

def music_volume(vol):
    music_player.volume=vol

def queue_music(name):
    print('queue music')
    global current_music
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.eos_action = 'next'


def play_music():
    print('play music')
    print('play music2')
    if music_player.playing or not current_music:
        return
    print("play2")

    name = current_music
    music_player.next()
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.play()
    music_player.eos_action = 'loop'

@music_player.event
def on_eos():
    music_player.eos_action = 'loop'


def stop_music():
    music_player.pause()

#
# SOUND
#
sounds = {}

def load(name, streaming=False):
    if not SOUND:
        return

    if name not in sounds:
        sounds[name] = pyglet.resource.media(name, streaming=streaming)

    return sounds[name]

def play(name):
    if not SOUND:
        return
    load(name)
    a = sounds[name].play().volume = sound_vol

def sound_volume( vol ):
    global sound_vol
    sound_vol = vol

def play_whack():
    play('whack.mp3')

def testaud():
    print("foo")
    #play('tswin.mp3')
    set_music('tswin.mp3')
    queue_music('speech.wav')
    #music_player.play()
    #play_music()
    print(music_player.playing)
    print("done")
    time.sleep(10)
#play_whack()
#time.sleep(4)