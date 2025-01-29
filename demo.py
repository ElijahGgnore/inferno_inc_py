import urwid

import stage
from message_log import MessageLog, TextMessage, TextMessagePart, ButtonMessage, ButtonMessageOption


class Demo(MessageLog):
    def setup(self, stage_):
        super().setup(stage_)
        
        def text_message():
            def greeting(tm: TextMessage, tmp: TextMessagePart):
                tmp.text = '\nHello ' + tm.message_log.stage.get_global_var('name')

            return TextMessage([
                TextMessagePart('Welcome', symbol_delay=1 / 10),
                TextMessagePart('\nNo time to explain', symbol_delay=1 / 100, auto_continue=True),
                TextMessagePart('\nThis one doesn\'t get typed', symbol_delay=0),
                TextMessagePart("\nWhat's your name?\n", store_input_at='name', store_input_globally=True),
                TextMessagePart('', preliminary_callback=greeting)],
                final_callback=choose_an_option)

        def choose_an_option(tm: TextMessage):
            tm.message_log.append_message(TextMessage([TextMessagePart('Select an option', auto_continue=True)],
                                                      final_callback=button_message))

        def button_message(tm: TextMessage):
            tm.message_log.append_message(ButtonMessage([
                ButtonMessageOption('1', show_selected_option),
                ButtonMessageOption('2', show_selected_option),
                ButtonMessageOption('3', show_selected_option)
            ]))

        def show_selected_option(bm: urwid.Button, b: ButtonMessage):
            bm.message_log.append_message(
                TextMessage([TextMessagePart(f'Selected option {b.label}')], final_callback=end_of_demo))

        def end_of_demo(tm: TextMessage):
            def goodbye(tm_: TextMessage, tmp: TextMessagePart):
                tmp.text = '\nGoodbye ' + tm_.message_log.stage.get_global_var('name')

            tm.message_log.append_message(TextMessage([
                TextMessagePart('End of demo', auto_continue=True),
                TextMessagePart('', auto_continue=True, symbol_delay=0, preliminary_callback=goodbye)
            ]))

        self.append_message(text_message())


def main():
    game = stage.Stage()
    game.set_scene(Demo())
    game.run()


if __name__ == '__main__':
    main()
