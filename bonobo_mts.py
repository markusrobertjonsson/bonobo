import tkinter as tk
import random
import subprocess
import csv
import time
import os
import sys
from sys import platform
from datetime import datetime
from math import sqrt

use_simpleaudio = True
try:
    import simpleaudio
except ModuleNotFoundError:
    use_simpleaudio = False

if platform == "win32":
    import winsound


# These abbreviations are used in the name of the result file.
    MATCHING_TO_SAMPLE = "MTS"
    ZERO_DELAY_MATCHING_TO_SAMPLE = "ZDMTS"
    DELAYED_MATCHING_TO_SAMPLE = "DMTS"


def set_config():
    config = dict()

    #######################
    # Experiment settings #
    #######################

    # The symbols to use. Shapes to choose from:
    # 'redtriangle', 'bluecircle', 'greensquare', 'bluetriangle', 'greencircle', 'redsquare',
    # 'greentriangle', 'redcircle', 'bluesquare'
    config["SYMBOLS_MTS"] = ['bluesquare', 'yellowsquare']
    # The nonzero delay times (in milliseconds) to use. It is chosen randomly in every other trial (and every other is 0).
    config["DELAY_TIMES"] = [0, 2000, 5000, 10000]
    # The time (in milliseconds) that the symbol is displayed in DMTS and ZDMTS
    config["SYMBOL_SHOW_TIME"] = 2000
    # The time (in milliseconds) that the symbol is displayed by itself in MTS before the options appear
    config["SYMBOL_SHOW_TIME_MTS"] = 1000

    ####################
    # General settings #
    ####################

    # Set to False or True
    config["HIDE_MOUSE_POINTER"] = False
    # The number of trials before the start screen appears automatically
    config["TRIALS_BEFORE_PAUSE"] = 60
    # The start screen
    config["START_SCREEN_COLOR_RGB"] = (255, 192, 203)
    # The background screen color in red, green, blue (each ranging from 0 to 255)
    config["BACKGROUND_COLOR_RGB"] = (0, 0, 0)
    # The color of the separator
    config["SEPARATOR_COLOR_RGB"] = (255, 255, 255)
    # The color of the Next button
    config["NEXT_BUTTON_COLOR_RGB"] = (255, 255, 255)
    # The color of the "blackout" screen
    config["BLACKOUT_COLOR_RGB"] = (100, 100, 100)
    # Width (and height) of colored square, as a fraction of H/3
    config["SYMBOL_WIDTH"] = 0.75
    # Width (and height) of the Next button, as a fraction of H/3
    config["NEXT_BUTTON_WIDTH"] = 0.65
    # The time (in milliseconds) for the black screen after incorrect answer
    config["BLACKOUT_TIME"] = 5000
    # The delay (in milliseconds) after correct answer, before the next symbol is displayed
    config["DELAY_AFTER_REWARD"] = 1000
    # The name of the sound file to play if correct
    config["SOUND_CORRECT"] = 'correct.wav'
    # The name of the sound file to play if incorrect
    config["SOUND_INCORRECT"] = 'incorrect.wav'

    return config


config = set_config()

# The subject exposed to the experiment. Used in the name of the result file and as the "subject" column in the result file
SUBJECT_TAG = "subject_tag"

random.seed()

hex_format = "#%02x%02x%02x"
START_SCREEN_COLOR = hex_format % config["START_SCREEN_COLOR_RGB"]
BACKGROUND_COLOR = hex_format % config["BACKGROUND_COLOR_RGB"]
SEPARATOR_COLOR = hex_format % config["SEPARATOR_COLOR_RGB"]
NEXT_BUTTON_COLOR = hex_format % config["NEXT_BUTTON_COLOR_RGB"]
BLACKOUT_COLOR = hex_format % config["BLACKOUT_COLOR_RGB"]

frame_options = dict()  # For debugging frame positioning
# {'highlightbackground': 'blue',
#                  'highlightcolor': 'blue',
#                  'highlightthickness': 1,
#                  'bd': 0}

canvas_options = {'bd': 0, 'highlightthickness': 0}

TOL = 0.99
TIMETOL = 3  # Round delay times to nearest millisecond


class Experiment():
    def __init__(self):
        filename = self.result_filename()
        self.result_file = ResultFile(filename)
        self.trial_cnt = 0

        # Current self.root.after jobs. They are stored to be able to cancel them in space_pressed.
        self.current_after_jobs = []

        # A list of the last 20 trials, 0 means unuccessful, 1 means successful
        self.success_list = []

        # The success frequency of the last 20 rounds
        self.success_frequency = 0

        self._make_widgets()

        self.set_background_color(BACKGROUND_COLOR)
        self.next_displayed = False
        self.go_displayed = False
        self.pause_screen_displayed = False
        self.display_pause_screen()

    def _make_widgets(self):
        self.root = tk.Tk()

        W = self.root.winfo_screenwidth() * TOL
        H = self.root.winfo_screenheight() * TOL
        h = H / 3

        # Width (and height) of stimulus symbol
        self.L = h * config["SYMBOL_WIDTH"]

        # self.root.attributes('-zoomed', True)  # Maximize window

        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)
        self.root.bind("<F5>", self.start_trial)
        self.root.bind("<space>", self.space_pressed)

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
        # self.middle_lcanvas.tag_bind("shape", "<Button-1>", self.middle_limage_clicked)
        self.middle_lcanvas.bind("<Button-1>", self.middle_limage_clicked)
        self.middle_lcanvas.pack(side=tk.RIGHT)
        self.middle_lframe.pack_propagate(False)
        self.middle_lframe.pack(side=tk.LEFT)

        # Middle
        self.go_frame = tk.Frame(self.middle_frame, height=h, width=h, **frame_options)
        self.go_canvas_width = config["NEXT_BUTTON_WIDTH"] * h
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
        # self.middle_rcanvas.tag_bind("shape", "<Button-1>", self.middle_rimage_clicked)
        self.middle_rcanvas.bind("<Button-1>", self.middle_rimage_clicked)
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
        self.next_canvas_width = h * config["NEXT_BUTTON_WIDTH"]
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

        if config["HIDE_MOUSE_POINTER"]:
            # Hide mouse pointer
            self.root.config(cursor="none")

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
        self._set_entire_screen_color(BLACKOUT_COLOR)

    def display_pause_screen(self):
        self._set_entire_screen_color(START_SCREEN_COLOR)
        self.pause_screen_displayed = True

    def _set_entire_screen_color(self, color):
        self.clear_canvases()
        self.set_background_color(color)
        self.separator1.configure(background=color)
        self.separator2.configure(background=color)

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

    def display_symbol(self, symbol, canvas):
        L = self.L * 0.99  # self.top_frame.winfo_height() * config["SYMBOL_WIDTH
        if symbol == 'redtriangle':
            S = sqrt(3) / 2
            canvas.create_polygon(0, L * (S + 1) / 2, L, L * (S + 1) / 2, L / 2, L * (1 - S) / 2,
                                  fill='red', outline="", tags="shape")
        elif symbol == 'bluecircle':
            canvas.create_oval(0, 0, L, L, fill='blue', outline="", tags="shape")
        elif symbol == 'greensquare':
            canvas.create_rectangle(0, 0, L, L, fill='green', outline="", tags="shape")
        elif symbol == 'bluetriangle':
            S = sqrt(3) / 2
            canvas.create_polygon(0, L * (S + 1) / 2, L, L * (S + 1) / 2, L / 2, L * (1 - S) / 2,
                                  fill='blue', outline="", tags="shape")
        elif symbol == 'greencircle':
            canvas.create_oval(0, 0, L, L, fill='green', outline="", tags="shape")
        elif symbol == 'redsquare':
            canvas.create_rectangle(0, 0, L, L, fill='red', outline="", tags="shape")
        elif symbol == 'greentriangle':
            S = sqrt(3) / 2
            canvas.create_polygon(0, L * (S + 1) / 2, L, L * (S + 1) / 2, L / 2, L * (1 - S) / 2,
                                  fill='green', outline="", tags="shape")
        elif symbol == 'redcircle':
            canvas.create_oval(0, 0, L, L, fill='red', outline="", tags="shape")
        elif symbol == 'bluesquare':
            canvas.create_rectangle(0, 0, L, L, fill='blue', outline="", tags="shape")
        elif symbol == 'yellowcircle':
            canvas.create_oval(0, 0, L, L, fill='yellow', outline="", tags="shape")
        elif symbol == 'yellowsquare':
            canvas.create_rectangle(0, 0, L, L, fill='yellow', outline="", tags="shape")
        elif symbol == 'yellowtriangle':
            S = sqrt(3) / 2
            canvas.create_polygon(0, L * (S + 1) / 2, L, L * (S + 1) / 2, L / 2, L * (1 - S) / 2,
                                  fill='yellow', outline="", tags="shape")

        elif symbol == 'lightbluesquare':
            canvas.create_rectangle(0, 0, L, L, fill=hex_format % (51, 153, 255), outline="",
                                    tags="shape")
        elif symbol == 'orangesquare':
            canvas.create_rectangle(0, 0, L, L, fill=hex_format % (255, 128, 0), outline="",
                                    tags="shape")
        else:
            raise Exception("Unknown symbol {}".format(symbol))

    def display_symbol_top(self, symbol):
        self.display_symbol(symbol, self.top_canvas)

    def next_clicked(self, event=None):
        if self.next_displayed:
            self.trial_cnt += 1
            self.start_trial()

    def space_pressed(self, event=None):
        _play('space_bar_sound.wav')
        if self.pause_screen_displayed:
            self.get_ready_to_start_trial()
            self.pause_screen_displayed = False
        else:
            self.display_pause_screen()
            self.cancel_all_after_jobs()

    def get_ready_to_start_trial(self):
        if self.trial_cnt >= config["TRIALS_BEFORE_PAUSE"]:
            self.display_pause_screen()
            self.trial_cnt = 0
        else:
            self.clear()
            self.display_next()

    def cancel_all_after_jobs(self):
        for j in self.current_after_jobs:
            self.root.after_cancel(j)
        self.current_after_jobs = []

    def middle_limage_clicked(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def middle_rimage_clicked(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def start_trial(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def go_clicked(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def result_filename(self):
        """
        Return the file name of the result file.
        """
        experiment = self.experiment_abbreviation()
        subject = SUBJECT_TAG.lower()
        date = datestamp()
        return subject + "_" + experiment + "_" + date + ".csv"

    def update_success_frequency(self, is_correct):
        self.success_list.append(int(is_correct))
        if len(self.success_list) > 20:
            self.success_list.pop(0)
        self.success_frequency = round(sum(self.success_list) / len(self.success_list), 3)

    def experiment_abbreviation(self):
        assert(False)  # Must be overloaded

    def correct_choice(self):
        self.clear()
        play_correct()
        job = self.root.after(config["DELAY_AFTER_REWARD"], self.get_ready_to_start_trial)
        self.current_after_jobs = [job]

    def incorrect_choice(self):
        self.blackout()
        play_incorrect()
        job = self.root.after(config["BLACKOUT_TIME"], self.get_ready_to_start_trial)
        self.current_after_jobs = [job]


class DelayedMatchingToSample(Experiment):
    def __init__(self):
        super().__init__()
        self.use_zero_delay = True

        # The last delay time used
        self.delay_time = None

        # The last sample displayed
        self.sample = None

        # The last displayed left option
        self.left_symbol = None

        # The last displayed right option
        self.right_symbol = None

        # Only used in MatchingToSample
        self.is_practice_trial = None

        self.left_option_displayed = False
        self.right_option_displayed = False

        # Overridden from Experiment, since here we want one success_list per delay time
        self.success_frequency = dict()
        self.success_list = dict()
        for dt in set(config["DELAY_TIMES"]).union({0}):
            self.success_frequency[dt] = 0
            self.success_list[dt] = []

    def start_trial(self, event=None):
        if self.use_zero_delay:
            self.delay_time = 0
        else:
            self.delay_time = random.choice(config["DELAY_TIMES"])
        self.use_zero_delay = not self.use_zero_delay
        self.clear()
        job1 = self.display_random_symbol(config["SYMBOL_SHOW_TIME"])
        self.current_after_jobs = [job1]
        job2 = self.root.after(config["SYMBOL_SHOW_TIME"] + self.delay_time, self.display_options,
                               self.sample)
        self.current_after_jobs.append(job2)

    def display_random_symbol(self, display_time):
        self.sample = random.choice(config["SYMBOLS_MTS"])
        self.top_canvas.delete(tk.ALL)
        self.display_symbol(self.sample, self.top_canvas)
        job = self.root.after(display_time, self.clear)
        return job

    def display_options(self, correct_symbol, do_clear=True, show_only_correct=False):
        incorrect_symbol = None
        if not show_only_correct:
            found = False
            while not found:
                incorrect_symbol = random.choice(config["SYMBOLS_MTS"])
                found = (incorrect_symbol != correct_symbol)
        if do_clear:
            self.clear()

        r = random.random()
        if r < 0.5:
            self.left_is_correct = True
            self.display_symbol(correct_symbol, self.middle_lcanvas)
            self.left_option_displayed = True
            self.left_symbol = correct_symbol
            self.right_symbol = incorrect_symbol
            if not show_only_correct:
                self.display_symbol(incorrect_symbol, self.middle_rcanvas)
                self.right_option_displayed = True
        else:
            self.left_is_correct = False
            self.display_symbol(correct_symbol, self.middle_rcanvas)
            self.right_option_displayed = True
            self.right_symbol = correct_symbol
            self.left_symbol = incorrect_symbol
            if not show_only_correct:
                self.display_symbol(incorrect_symbol, self.middle_lcanvas)
                self.left_option_displayed = True
        self.tic = time.time()

    def middle_limage_clicked(self, event=None):
        if self.left_option_displayed:
            is_correct = self.left_is_correct
            if self.left_is_correct:
                self.correct_choice()
            else:
                self.incorrect_choice()
            self.left_option_displayed = False
            self.right_option_displayed = False
            self.write_to_file(self.left_symbol, is_correct)

    def middle_rimage_clicked(self, event=None):
        if self.right_option_displayed:
            is_correct = not self.left_is_correct
            if self.left_is_correct:
                self.incorrect_choice()
            else:
                self.correct_choice()
            self.left_option_displayed = False
            self.right_option_displayed = False
            self.write_to_file(self.right_symbol, is_correct)

    def write_to_file(self, symbol_clicked, is_correct):
        if self.is_practice_trial:
            return
        self.update_success_frequency(is_correct)
        headers = ["freq_correct",
                   "subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "delay",
                   "sample",
                   "left_item",
                   "right_item",
                   "response",
                   "is_correct"]

        ls = self.left_symbol if self.left_symbol is not None else "None"
        rs = self.right_symbol if self.right_symbol is not None else "None"
        values = [self.success_frequency[self.delay_time],
                  SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.trial_cnt,
                  self.delay_time,
                  self.sample,
                  ls,
                  rs,
                  symbol_clicked,
                  is_correct]

        self.result_file.write(headers, values)

    def update_success_frequency(self, is_correct):
        sl = self.success_list[self.delay_time]
        if is_correct:
            sl.append(1)
        else:
            sl.append(0)
        if len(self.success_list) > 20:
            sl.pop(0)
        self.success_frequency[self.delay_time] = round(sum(sl) / len(sl), 3)

    def go_clicked(self, event=None):
        pass  # Not used in DMS

    def experiment_abbreviation(self):
        return DELAYED_MATCHING_TO_SAMPLE


class ZeroDelayMatchingToSample(DelayedMatchingToSample):
    def __init__(self):
        super().__init__()
        self.delay_time = 0
        self.success_frequency = {self.delay_time: 0}
        self.success_list = {self.delay_time: []}

    def start_trial(self, event=None):
        self.clear()
        job1 = self.display_random_symbol(config["SYMBOL_SHOW_TIME"])
        self.current_after_jobs = [job1]
        job2 = self.root.after(config["SYMBOL_SHOW_TIME"], self.display_options, self.sample)
        self.current_after_jobs.append(job2)

    def experiment_abbreviation(self):
        return ZERO_DELAY_MATCHING_TO_SAMPLE


class MatchingToSample(DelayedMatchingToSample):
    def __init__(self):
        super().__init__()
        self.delay_time = "na"
        self.is_practice_trial = False  # If True, show only the correct option

        self.success_frequency = {self.delay_time: 0}
        self.success_list = {self.delay_time: []}

    def start_trial(self, event=None):
        self.is_practice_trial = self.trial_cnt % 3 == 0
        self.clear()
        self.display_random_symbol()
        job = self.root.after(config["SYMBOL_SHOW_TIME_MTS"], self.display_options,
                              self.sample, False, self.is_practice_trial)
        self.current_after_jobs = [job]

    def display_random_symbol(self):
        self.sample = random.choice(config["SYMBOLS_MTS"])
        self.display_symbol(self.sample, self.top_canvas)

    def experiment_abbreviation(self):
        return MATCHING_TO_SAMPLE


def play_correct():
    _play(config["SOUND_CORRECT"])


def play_incorrect():
    _play(config["SOUND_INCORRECT"])


def _play(filename):
    full_filename = "./sounds/" + filename
    if use_simpleaudio:
        wave_obj = simpleaudio.WaveObject.from_wave_file(full_filename)
        wave_obj.play()
        # play_obj = wave_obj.play()
        # play_obj.wait_done()
    else:
        if platform == "darwin":  # OSX
            subprocess.call(['afplay', full_filename])
        elif platform == "win32":  # Windows
            winsound.PlaySound(full_filename, winsound.SND_FILENAME)
        else:
            print('\a')  # beep


def datestamp():
    now = datetime.now()
    year = str(now.year)
    month = str(now.month)
    if now.month < 10:
        month = "0" + month
    day = str(now.day)
    if now.day < 10:
        day = "0" + day
    return year + "-" + month + "-" + day


def timestamp():
    unow = datetime.now()
    hour = str(unow.hour)
    if unow.hour < 10:
        hour = "0" + hour
    minute = str(unow.minute)
    if unow.minute < 10:
        minute = "0" + minute
    second = str(unow.second)
    if unow.second < 10:
        second = "0" + second
    microsecond = unow.microsecond
    millisecond = str(round(microsecond / 1000))
    return hour + ":" + minute + ":" + second + ":" + millisecond


class ResultFile():
    def __init__(self, filename):
        self.filename = filename
        self.path_and_file = "./result_files/" + self.filename

        if not os.path.exists('./result_files'):
            os.makedirs('./result_files')

    def write(self, headers, values):
        if os.path.exists(self.path_and_file):
            write_headers = (os.path.getsize(self.path_and_file) == 0)
        else:
            write_headers = True

        file = open(self.path_and_file, 'a', newline='')
        with file as csvfile:
            w = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_MINIMAL, escapechar=None)
            if write_headers:
                w.writerow(headers)
            w.writerow(values)


def print_help():
    print("Usage: python bonobo_mts.py <experiment_type>")
    print("Where <experiment_type> is one of the following:")
    print("  - MTS (for simultaneous matching-to-sample)")
    print("  - ZDMTS (for zero-delay matching-to-sample)")
    print("  - DMTS (for delayed matching-to-sample)")


if __name__ == '__main__':
    # Check if the exp_type argument is provided
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    # Get the experiment type from the command line argument
    experiment_type = sys.argv[1].upper()

    # Validate input
    valid_exp_types = {"MTS", "ZDMTS", "DMTS"}
    if experiment_type not in valid_exp_types:
        print_help()
        sys.exit(1)    

    e = None
    if experiment_type == "MTS":
        e = MatchingToSample()
    elif experiment_type == "ZDMTS":
        e = ZeroDelayMatchingToSample()
    elif experiment_type == "DMTS":
        e = DelayedMatchingToSample()
    if e:
        e.root.mainloop()
