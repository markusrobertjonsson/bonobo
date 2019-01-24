import tkinter as tk
import random
import subprocess
import config
from sys import platform

if platform == "linux" or platform == "linux2":
    import simpleaudio


random.seed()

BACKGROUND_COLOR = "#%02x%02x%02x" % config.BACKGROUND_COLOR_RGB
SEPARATOR_COLOR = "#%02x%02x%02x" % config.SEPARATOR_COLOR_RGB
NEXT_BUTTON_COLOR = "#%02x%02x%02x" % config.NEXT_BUTTON_COLOR_RGB
GO_BUTTON_COLOR = "#%02x%02x%02x" % config.GO_BUTTON_COLOR_RGB
BLACKOUT_COLOR = "#%02x%02x%02x" % config.BLACKOUT_COLOR_RGB

frame_options = dict()  # For debugging frame positioning
# {'highlightbackground': 'blue',
#                  'highlightcolor': 'blue',
#                  'highlightthickness': 1,
#                  'bd': 0}

canvas_options = {'bd': 0, 'highlightthickness': 0}

TOL = 0.45


class Experiment():
    def __init__(self):
        self.root = tk.Tk()

        W = self.root.winfo_screenwidth() * TOL
        H = self.root.winfo_screenheight() * TOL
        h = H / 3

        # Width (and height) of stimulus symbol
        self.L = h * config.SYMBOL_WIDTH

        # self.root.attributes('-zoomed', True)  # Maximize window

        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)
        self.root.bind("<F5>", self.start)

        # TOP
        self.top_frame = tk.Frame(self.root, height=h, width=W, **frame_options)
        self.top_canvas = tk.Canvas(self.top_frame, height=self.L, width=self.L, **canvas_options)
        self.top_canvas.tag_bind("shape", "<Button-1>", self.top_image_clicked)
        self.top_canvas.pack(expand=True)

        self.top_frame.pack_propagate(False)
        self.top_frame.pack(expand=True, side=tk.TOP)

        # SEPARATOR1
        self.separator1 = tk.Frame(height=4, background=SEPARATOR_COLOR, bd=0,
                                   highlightthickness=0)
        self.separator1.pack(fill=tk.X, padx=0, pady=0)

        # MIDDLE
        self.middle_frame = tk.Frame(self.root, height=h, width=W, **frame_options)

        fw = (W - h) / 2

        # Left
        self.middle_lframe = tk.Frame(self.middle_frame, height=h, width=fw, **frame_options)
        self.middle_lcanvas = tk.Canvas(self.middle_lframe, height=self.L, width=self.L,
                                        **canvas_options)
        self.middle_lcanvas.tag_bind("shape", "<Button-1>", self.middle_limage_clicked)
        self.middle_lcanvas.pack(side=tk.RIGHT)
        self.middle_lframe.pack_propagate(False)
        self.middle_lframe.pack(side=tk.LEFT)

        # Middle
        self.go_frame = tk.Frame(self.middle_frame, height=h, width=h, **frame_options)
        self.go_canvas_width = config.GO_BUTTON_WIDTH * h
        self.go_canvas = tk.Canvas(self.go_frame, height=self.go_canvas_width,
                                   width=self.go_canvas_width, **canvas_options)
        self.go_canvas.bind("<Button-1>", self.go_clicked)
        self.go_canvas.pack(expand=True)
        self.go_frame.pack_propagate(False)
        self.go_frame.pack(side=tk.LEFT)

        # Right
        self.middle_rframe = tk.Frame(self.middle_frame, height=h, width=fw, **frame_options)
        self.middle_rcanvas = tk.Canvas(self.middle_rframe, height=self.L, width=self.L,
                                        **canvas_options)
        self.middle_rcanvas.tag_bind("shape", "<Button-1>", self.middle_rimage_clicked)
        self.middle_rcanvas.pack(side=tk.LEFT)
        self.middle_rframe.pack_propagate(False)
        self.middle_rframe.pack(side=tk.LEFT)

        self.middle_frame.pack_propagate(False)
        self.middle_frame.pack(expand=True, side=tk.TOP)

        # SEPARATOR2
        self.separator2 = tk.Frame(height=4, background=SEPARATOR_COLOR, bd=0,
                                   highlightthickness=0)
        self.separator2.pack(fill=tk.X, padx=0, pady=0)

        # BOTTOM
        self.next_frame = tk.Frame(self.root, height=h, width=W, **frame_options)
        self.next_canvas_width = h * config.NEXT_BUTTON_WIDTH
        self.next_canvas = tk.Canvas(self.next_frame, height=self.next_canvas_width,
                                     width=self.next_canvas_width, **canvas_options)
        self.next_canvas.bind("<Button-1>", self.next_clicked)
        self.next_canvas.pack(expand=True)

        w = self.next_canvas_width
        pw = w * 0.1
        d1 = w / 2 - pw / 2
        d2 = w / 2 + pw / 2
        self.next_symbol_args = [0, d1,
                                 d1, d1,
                                 d1, 0,
                                 d2, 0,
                                 d2, d1,
                                 w, d1,
                                 w, d2,
                                 d2, d2,
                                 d2, w,
                                 d1, w,
                                 d1, d2,
                                 0, d2]

        self.next_frame.pack_propagate(False)
        self.next_frame.pack(expand=True, side=tk.TOP)

        self.set_background_color(BACKGROUND_COLOR)
        self.next_displayed = False
        self.go_displayed = False
        self.display_next()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen  # Just toggling the boolean
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def end_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
        return "break"

    def top_frame_clicked(self, event=None):
        pass

    def top_image_clicked(self, event=None):
        pass

    def blackout(self):
        self.clear_canvases()
        self.set_background_color(BLACKOUT_COLOR)
        self.separator1.configure(background=BLACKOUT_COLOR)
        self.separator2.configure(background=BLACKOUT_COLOR)

    def set_background_color(self, color):
        # Root
        self.root.configure(background=color)
        # Frames
        self.top_frame.configure(background=color)
        self.middle_frame.configure(background=color)
        self.middle_lframe.configure(background=color)
        self.go_frame.configure(background=color)
        self.middle_rframe.configure(background=color)
        self.next_frame.configure(background=color)
        # Canvases
        self.top_canvas.configure(background=color)
        self.middle_lcanvas.configure(background=color)
        self.go_canvas.configure(background=color)
        self.middle_rcanvas.configure(background=color)
        self.next_canvas.configure(background=color)

    def clear(self):
        self.set_background_color(BACKGROUND_COLOR)
        self.separator1.configure(background=SEPARATOR_COLOR)
        self.separator2.configure(background=SEPARATOR_COLOR)
        self.clear_canvases()

    def clear_canvases(self):
        self.top_canvas.delete(tk.ALL)
        self.middle_lcanvas.delete(tk.ALL)
        self.go_canvas.delete(tk.ALL)
        self.middle_rcanvas.delete(tk.ALL)
        self.next_canvas.delete(tk.ALL)
        self.next_displayed = False
        self.go_displayed = False

    def show_only_next(self):
        self.clear()
        self.display_next()

    def display_next(self):
        self.next_canvas.create_polygon(*self.next_symbol_args, fill=NEXT_BUTTON_COLOR,
                                        outline=NEXT_BUTTON_COLOR)
        self.next_displayed = True

    def show_only_go(self):
        self.clear()
        self.display_go()

    def display_go(self):
        self.go_canvas.create_oval(0, 0, self.go_canvas_width, self.go_canvas_width,
                                   fill=GO_BUTTON_COLOR, outline=GO_BUTTON_COLOR)
        self.go_displayed = True

    def display_symbol(self, symbol, canvas):
        L = self.L  # self.top_frame.winfo_height() * config.SYMBOL_WIDTH
        if symbol == 'redtriangle':
            canvas.create_polygon(0, 0, L, L, L, 0, fill='red', tags="shape")
        elif symbol == 'bluecircle':
            canvas.create_oval(0, 0, L, L, fill='blue', tags="shape")
        elif symbol == 'greensquare':
            canvas.create_rectangle(0, 0, L, L, fill='green', tags="shape")
        elif symbol == 'bluetriangle':
            canvas.create_polygon(0, 0, L, L, L, 0, fill='blue', tags="shape")
        elif symbol == 'greencircle':
            canvas.create_oval(0, 0, L, L, fill='green', tags="shape")
        elif symbol == 'redsquare':
            canvas.create_rectangle(0, 0, L, L, fill='red', tags="shape")
        elif symbol == 'greentriangle':
            canvas.create_polygon(0, 0, L, L, L, 0, fill='green', tags="shape")
        elif symbol == 'redcircle':
            canvas.create_oval(0, 0, L, L, fill='red', tags="shape")
        elif symbol == 'bluesquare':
            canvas.create_rectangle(0, 0, L, L, fill='blue', tags="shape")

    def display_symbol_top(self, symbol):
        self.display_symbol(symbol, self.top_canvas)

    def middle_limage_clicked(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def middle_rimage_clicked(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def start(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def next_clicked(self, event=None):
        if self.next_displayed:
            self.start()

    def go_clicked(self, event=None):
        pass
        # assert(False)  # Must be overloaded


class NextButtonTraining(Experiment):
    def __init__(self):
        super().__init__()

    def start(self, event=None):
        self.clear()
        play_correct()
        self.root.after(config.DELAY_AFTER_REWARD, self.show_only_next)


class GoButtonTraining(Experiment):
    def __init__(self):
        super().__init__()
        self.show_only_go()

    def start(self, event=None):
        pass

    def go_clicked(self, event=None):
        self.clear()
        play_correct()
        self.root.after(config.DELAY_AFTER_REWARD, self.show_only_go)


class DelayedMatchedToSample(Experiment):
    def __init__(self):
        super().__init__()
        self.use_zero_delay = False

    def start(self, event=None):
        if self.use_zero_delay:
            delay_time = 0
        else:
            delay_time = random.choice(config.DELAY_TIMES)
        self.use_zero_delay = not self.use_zero_delay
        self.clear()
        symbol = self.display_random_symbol(config.SYMBOL_SHOW_TIME)
        self.root.after(config.SYMBOL_SHOW_TIME + delay_time, self.display_options, symbol)

    def display_random_symbol(self, display_time):
        symbol = random.choice(config.SYMBOLS)
        self.top_canvas.delete(tk.ALL)
        self.display_symbol(symbol, self.top_canvas)
        self.root.after(display_time, self.clear)
        return symbol

    def display_options(self, correct_symbol, do_clear=True):
        incorrect_symbol = None
        found = False
        while not found:
            incorrect_symbol = random.choice(config.SYMBOLS)
            found = (incorrect_symbol != correct_symbol)
        if do_clear:
            self.clear()

        r = random.random()
        if r < 0.5:
            self.left_is_correct = True
            self.display_symbol(correct_symbol, self.middle_lcanvas)
            self.display_symbol(incorrect_symbol, self.middle_rcanvas)
        else:
            self.left_is_correct = False
            self.display_symbol(incorrect_symbol, self.middle_lcanvas)
            self.display_symbol(correct_symbol, self.middle_rcanvas)

    def middle_limage_clicked(self, event=None):
        if self.left_is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()

    def middle_rimage_clicked(self, event=None):
        if self.left_is_correct:
            self.incorrect_choice()
        else:
            self.correct_choice()

    def correct_choice(self):
        self.clear()
        play_correct()
        self.root.after(config.DELAY_AFTER_REWARD, self.show_only_next)

    def incorrect_choice(self):
        self.blackout()
        play_incorrect()
        self.root.after(config.BLACKOUT_TIME, self.show_only_next)

    def go_clicked(self, event=None):
        pass  # Not used in DMS


class MatchedToSample(DelayedMatchedToSample):
    def __init__(self):
        super().__init__()

    def start(self, event=None):
        self.clear()
        symbol = self.display_random_symbol()
        self.display_options(symbol, do_clear=False)

    def display_random_symbol(self):
        symbol = random.choice(config.SYMBOLS)
        self.display_symbol(symbol, self.top_canvas)
        return symbol


class Discrimination(Experiment):
    def __init__(self):
        super().__init__()

    def go_clicked(self, event=None):
        if self.go_waiting is not None:  # Cancel the pending job to remove the go button
            self.root.after_cancel(self.go_waiting)
            self.go_waiting = None
        if self.go_displayed:
            if self.is_rewarding:
                self.clear()
                play_correct()
                self.root.after(config.DELAY_AFTER_REWARD, self.show_only_next)
            else:
                self.blackout()
                play_incorrect()
                self.root.after(config.BLACKOUT_TIME, self.show_only_next)


class SequenceDiscrimination(Discrimination):
    def __init__(self):
        super().__init__()
        self.go_waiting = None

    def start(self, event=None):
        self.clear()
        self.display_random_sequence()
        time_to_go = 2 * config.STIMULUS_TIME + config.INTER_STIMULUS_TIME + config.RETENTION_TIME
        self.root.after(time_to_go, self.show_only_go)
        time_to_go_away = time_to_go + config.GO_BUTTON_DURATION
        self.go_waiting = self.root.after(time_to_go_away, self.show_only_next)

    def display_random_sequence(self):
        r = random.random()
        if r < 0.25:
            symbol1, symbol2 = config.SYMBOL1, config.SYMBOL1
        elif r < 0.5:
            symbol1, symbol2 = config.SYMBOL1, config.SYMBOL2
        elif r < 0.75:
            symbol1, symbol2 = config.SYMBOL2, config.SYMBOL1
        else:
            symbol1, symbol2 = config.SYMBOL2, config.SYMBOL2
        self.top_canvas.delete(tk.ALL)
        self.display_symbol_top(symbol1)
        self.root.after(config.STIMULUS_TIME, self.clear)
        self.root.after(config.STIMULUS_TIME + config.INTER_STIMULUS_TIME,
                        self.display_symbol_top, symbol2)
        self.root.after(2 * config.STIMULUS_TIME + config.INTER_STIMULUS_TIME, self.clear)
        self.is_rewarding = ((symbol1, symbol2) == config.REWARDING_SEQUENCE)


class SingleStimulusDiscrimination(Discrimination):
    def __init__(self):
        super().__init__()
        self.go_waiting = None

    def start(self, event=None):
        self.clear()
        self.display_random_stimulus()
        time_to_go = config.STIMULUS_TIME + config.RETENTION_TIME
        self.root.after(time_to_go, self.show_only_go)
        time_to_go_away = time_to_go + config.GO_BUTTON_DURATION
        self.go_waiting = self.root.after(time_to_go_away, self.show_only_next)

    def display_random_stimulus(self):
        symbol = random.choice(config.SYMBOLS)
        self.top_canvas.delete(tk.ALL)
        self.display_symbol_top(symbol)
        self.root.after(config.STIMULUS_TIME, self.clear)
        self.is_rewarding = (symbol == config.REWARDING_STIMULUS)


def play_correct():
    _play(config.SOUND_CORRECT)


def play_incorrect():
    _play(config.SOUND_INCORRECT)


def _play(filename):
    if platform == "darwin":  # OSX
        subprocess.call(['afplay', filename])
    elif platform == "linux" or platform == "linux2":  # Linux
        wave_obj = simpleaudio.WaveObject.from_wave_file(filename)
        wave_obj.play()
        # play_obj = wave_obj.play()
        # play_obj.wait_done()
    elif platform == "win32":
        print('\a')  # beep
    else:
        print('\a')  # beep


if __name__ == '__main__':
    e = None
    if config.EXPERIMENT == "NextButtonTraining":
        e = NextButtonTraining()
    elif config.EXPERIMENT == "GoButtonTraining":
        e = GoButtonTraining()
    elif config.EXPERIMENT == "MatchedToSample":
        e = MatchedToSample()
    elif config.EXPERIMENT == "DelayedMatchedToSample":
        e = DelayedMatchedToSample()
    elif config.EXPERIMENT == "SequenceDiscrimination":
        e = SequenceDiscrimination()
    elif config.EXPERIMENT == "SingleStimulusDiscrimination":
        e = SingleStimulusDiscrimination()
    else:
        print("Error: Undefined experiment name '" + config.EXPERIMENT + "'.")
    if e:
        e.root.mainloop()


class File():
    def __init__(self, filename):
        self.filename = filename
