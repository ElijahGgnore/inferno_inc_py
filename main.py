from __future__ import annotations

import stage
from message_log import MessageLog, TextMessage, TextMessagePart

mp1 = TextMessagePart('Welcome', symbol_delay=1 / 10)
mp2 = TextMessagePart('\nNo time to explain', symbol_delay=1 / 100, auto_continue=True)
mp3 = TextMessagePart('\nThis one doesn\'t get typed', symbol_delay=0)

tm = TextMessage([mp1, mp2, mp3])

game = stage.Stage()
scene = MessageLog()
game.set_scene(scene)

scene.append_message(tm)

game.run()
