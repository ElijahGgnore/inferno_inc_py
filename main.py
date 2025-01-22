from __future__ import annotations

import stage
from message_log import MessageLog, TextMessage, TextMessagePart

mp1 = TextMessagePart('Welcome', symbol_delay=1 / 10)
mp2 = TextMessagePart('\nNo time to explain', symbol_delay=1 / 100, auto_continue=True)
mp3 = TextMessagePart('\nThis one doesn\'t get typed', symbol_delay=0)
mp4 = TextMessagePart("\nWhat's your name?\n", store_input_at='name', store_input_globally=True)


def greeting(t: TextMessage, p: TextMessagePart):
    p.text = '\nHello ' + t.message_log.stage.get_global_var('name') + '\n'


mp5 = TextMessagePart('', preliminary_callback=greeting)

tm = TextMessage([mp1, mp2, mp3, mp4, mp5])

game = stage.Stage()
scene = MessageLog()
game.set_scene(scene)

scene.append_message(tm)

game.run()
