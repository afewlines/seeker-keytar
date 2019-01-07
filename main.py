from random import randint

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.effectwidget import EffectWidget
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager

# CLASSES


class BoardGenerator():
    def __init__(self):
        # init array of boards
        self.boards = []
        # start at board error
        self.current = -1

    def new_board(self, length, width):
        # init new board
        board = []
        # create 'length' rows, select random
        for row in range(length):
            temp_row = [0 for i in range(width)]
            temp_row[randint(0, width - 1)] = 1
            board.append(temp_row)

        # add padding
        for row in range(4):
            temp_row = [0 for i in range(width)]
            board.append(temp_row)

        # add to list of boards
        self.boards.append(board)
        # increment current board
        self.current += 1

    def get_board(self):
        # if there is a board
        if self.current >= 0:
            return self.boards[self.current]


# KIVY CLASSES

class Tile(ButtonBehavior, Label):
    def __init__(self, type, **kwargs):
        # get superclass properties
        super(Tile, self).__init__()
        # set id position
        self.moniker = kwargs['index']
        #
        self.type = type
        self.bcolor = Player.T_COLORS[self.type]

    def on_press(self):
        # if tile is on current row
        if self.moniker[0] == Player.SCREENS['game'].current_row:
            # if target, register correct
            # else, fail
            if self.type == 1:
                Player.SCREENS['game'].register(True)
            else:
                Player.SCREENS['game'].register(False)


# KIVY SCREENS

class TitleScreen(Screen):
    def __init__(self, **kwargs):
        super(TitleScreen, self).__init__(**kwargs)
        self.bcolor = Player.COLORS['offwhite']

    def _on_keypress(self, keyboard, keycode, text, modifiers):
        pass

    def on_touch_up(self, touch):
        Player.change_screen('game')


class WinScreen(Screen):
    def __init__(self, **kwargs):
        super(WinScreen, self).__init__(**kwargs)
        self.bcolor = Player.COLORS['offwhite']

    def _on_keypress(self, keyboard, keycode, text, modifiers):
        pass

    def on_touch_up(self, touch):
        Player.change_screen('game')


class LoseScreen(Screen):
    def __init__(self, **kwargs):
        super(LoseScreen, self).__init__(**kwargs)
        self.bcolor = Player.COLORS['offwhite']

    def _on_keypress(self, keyboard, keycode, text, modifiers):
        pass

    def on_touch_up(self, touch):
        Player.change_screen('game')


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.bcolor = Player.COLORS['charcoal']
        self.grid = self.ids.grid
        self.generator = BoardGenerator()
        self.active = False
        self.board = []
        self.board_length = 50
        self.board_width = 4
        self.current_row = 0
        self.start_timer = True
        self.ttime = 0

    def _on_keypress(self, keyboard, keycode, text, modifiers):
        pass

    def on_pre_enter(self):
        self.reset()
        self.generator.new_board(self.board_length, self.board_width)
        self.board = self.generator.get_board()
        self.update()

    def on_enter(self):
        # fix top bar widths
        section_width = self.ids.time.width * 0.9
        self.ids.time.text_size = [section_width, None]
        self.ids.level.text_size = [section_width, None]
        # activate
        self.active = True
        self.start_timer = True

    def on_leave(self):
        # put vars back to intial status
        self.reset()

    def reset(self):
        # put vars back to intial status
        self.active = False
        self.board = []
        self.current_row = 0
        self.ttime = 0
        self.start_timer = False
        self.ids.time.text = '{0:.3f}'.format(0)
        # clear grid
        self.grid.clear_widgets()

    def update(self):
        # update row text
        self.ids.level.text = "{}".format(self.current_row)
        # update grid
        self.grid.clear_widgets()
        self.grid.cols = self.board_width
        y_num = 3
        current = self.board[self.current_row:self.current_row + 3]
        current.reverse()
        for row in current:
            y_num -= 1
            x_num = -1
            for cell in row:
                x_num += 1
                self.grid.add_widget(
                    Tile(cell, index=(self.current_row + y_num, x_num)))

    def timer(self, dt):
        self.ttime += dt
        self.ids.time.text = '{0:.3f}'.format(self.ttime)
        return self.active

    def register(self, hit):
        # start timer
        if self.start_timer:
            Clock.schedule_interval(self.timer, 0.01)
            self.start_timer = False
        # check if successful
        if hit:
            self.current_row += 1
            self.update()
        else:
            self.lose()

        # process win
        if self.current_row >= self.board_length:
            self.win()
            return

    def win(self):
        Player.SCREENS['win'].ids.time.text = 'time: {0:.3f}'.format(
            self.ttime)
        Player.change_screen('win')

    def lose(self):
        Player.SCREENS['lose'].ids.time.text = 'time: {0:.3f}'.format(
            self.ttime)
        Player.SCREENS['lose'].ids.completed.text = 'rows: {:}'.format(
            self.current_row)
        Player.change_screen('lose')


# KIVY INNARDS

class Player:
    MANAGER = ScreenManager()
    SCREENS = None
    KEY = []
    ALPHA = [lt for lt in 'abcdefghijklmnopqrswxyz1234567890 ']
    COLORS = {'brown': [0.5, 0.43, 0.27, 1],
              'offwhite': [1.0, 1.0, 0.89, 1],
              'blue': [0.29, 0.46, 0.61, 1],
              'green': [0.47, 0.60, 0.45, 1],
              'white': [1, 1, 1, 1],
              'charcoal': [0.35, 0.4, 0.43, 1],
              'red': [0.81, 0.38, 0.45, 1]}
    T_COLORS = [COLORS['offwhite'],
                COLORS['charcoal']]

    def __init__(self):
        Player.SCREENS = {'title': TitleScreen(name='title'),
                          'win': WinScreen(name='win'),
                          'lose': LoseScreen(name='lose'),
                          'game': GameScreen(name='game')}
        for scr in Player.SCREENS:
            Player.MANAGER.add_widget(Player.SCREENS[scr])

        Player.change_screen('title')
        # self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        # self._keyboard.bind(on_key_down=self._on_keypress)

    def _on_keypress(self, keyboard, keycode, text, modifiers):
        if Player.MANAGER.current_screen.transition_progress % 1 == 0:
            Player.MANAGER.current_screen._on_keypress(
                keyboard, keycode, text, modifiers)

    def _keyboard_closed(self):
        try:
            self._keyboard.unbind(on_key_down=self._on_keypress)
            self._keyboard = None
        except:
            pass

    @staticmethod
    def change_screen(target, *args):
        try:
            Player.MANAGER.current = target
        except:
            print('[ E ] Screen {} does not exist'.format(target))


class KeytarApp(App):
    def build(self):
        sm = Player()
        return sm.MANAGER


if __name__ == '__main__':
    KeytarApp().run()
