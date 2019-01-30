import tkinter as tk
import random
import subprocess
import config
import csv
import time
import os
from sys import platform
from datetime import datetime
from math import sqrt

# if platform == "linux" or platform == "linux2":

use_simpleaudio = True
try:
    import simpleaudio
except ModuleNotFoundError:
    use_simpleaudio = False

random.seed()

START_SCREEN_COLOR = "#%02x%02x%02x" % config.START_SCREEN_COLOR_RGB
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

TOL = 0.99
TIMETOL = 3  # Round delay times to nearest millisecond


class Experiment():
    def __init__(self):
        filename = self.result_filename()
        self.result_file = ResultFile(filename)
        self.trial_cnt = 0

        # A list of the last 20 trials, 0 means unuccessful, 1 means successful
        self.success_list = []

        # The success frequency of the last 20 rounds
        self.success_frequency = 0

        self._make_widgets()

        self.set_background_color(BACKGROUND_COLOR)
        self.next_displayed = False
        self.go_displayed = False
        self.display_start_screen()

    def _make_widgets(self):
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

    def display_start_screen(self):
        self._set_entire_screen_color(START_SCREEN_COLOR)

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

    def show_only_go(self):
        self.clear()
        self.display_go()

    def display_go(self):
        L = self.go_canvas_width * 0.99
        self.go_canvas.create_oval(0, 0, L, L, fill=GO_BUTTON_COLOR, outline=GO_BUTTON_COLOR)
        self.go_displayed = True

    def display_symbol(self, symbol, canvas):
        L = self.L * 0.99  # self.top_frame.winfo_height() * config.SYMBOL_WIDTH
        if symbol == 'redtriangle':
            S = sqrt(3) / 2
            canvas.create_polygon(0, L * (S + 1) / 2, L, L * (S + 1) / 2, L / 2, L * (1 - S) / 2,
                                  fill='red', tags="shape")
        elif symbol == 'bluecircle':
            canvas.create_oval(0, 0, L, L, fill='blue', tags="shape")
        elif symbol == 'greensquare':
            canvas.create_rectangle(0, 0, L, L, fill='green', tags="shape")
        elif symbol == 'bluetriangle':
            S = sqrt(3) / 2
            canvas.create_polygon(0, L * (S + 1) / 2, L, L * (S + 1) / 2, L / 2, L * (1 - S) / 2,
                                  fill='blue', tags="shape")
        elif symbol == 'greencircle':
            canvas.create_oval(0, 0, L, L, fill='green', tags="shape")
        elif symbol == 'redsquare':
            canvas.create_rectangle(0, 0, L, L, fill='red', tags="shape")
        elif symbol == 'greentriangle':
            S = sqrt(3) / 2
            canvas.create_polygon(0, L * (S + 1) / 2, L, L * (S + 1) / 2, L / 2, L * (1 - S) / 2,
                                  fill='green', tags="shape")
        elif symbol == 'redcircle':
            canvas.create_oval(0, 0, L, L, fill='red', tags="shape")
        elif symbol == 'bluesquare':
            canvas.create_rectangle(0, 0, L, L, fill='blue', tags="shape")
        elif symbol == 'yellowcircle':
            canvas.create_oval(0, 0, L, L, fill='yellow', tags="shape")
        elif symbol == 'yellowsquare':
            canvas.create_rectangle(0, 0, L, L, fill='yellow', tags="shape")
        elif symbol == 'yellowtriangle':
            S = sqrt(3) / 2
            canvas.create_polygon(0, L * (S + 1) / 2, L, L * (S + 1) / 2, L / 2, L * (1 - S) / 2,
                                  fill='yellow', tags="shape")

    def display_symbol_top(self, symbol):
        self.display_symbol(symbol, self.top_canvas)

    def next_clicked(self, event=None):
        if self.next_displayed:
            self.trial_cnt += 1
            self.start_trial()

    def space_pressed(self, event=None):
        self.show_only_next()

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
        subject = config.SUBJECT_TAG.lower()
        date = datestamp()
        return subject + "_" + experiment + "_" + date + ".csv"

    def update_success_frequency(self, is_correct):
        if is_correct:
            self.success_list.append(1)
        else:
            self.success_list.append(0)
        if len(self.success_list) > 20:
            self.success_list.pop(0)
        self.success_frequency = sum(self.success_list) / len(self.success_list)

    def experiment_abbreviation(self):
        assert(False)  # Must be overloaded


class NextButtonTraining(Experiment):
    def __init__(self):
        super().__init__()
        self.tic = time.time()

    def start_trial(self, event=None):
        self.write_to_file()
        self.clear()
        play_correct()
        self.root.after(config.DELAY_AFTER_REWARD, self.show_only_next)

    def show_only_next(self):
        super().show_only_next()
        self.tic = time.time()

    def write_to_file(self):
        headers = ["subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "response_time",
                   "BACKGROUND_COLOR",
                   "SEPARATOR_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "NEXT_BUTTON_WIDTH",
                   "SOUND_CORRECT"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [config.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.trial_cnt,
                  response_time,
                  BACKGROUND_COLOR,
                  SEPARATOR_COLOR,
                  NEXT_BUTTON_COLOR,
                  config.NEXT_BUTTON_WIDTH,
                  config.SOUND_CORRECT]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config.NEXT_BUTTON_TRAINING


class GoButtonTraining(Experiment):
    def __init__(self):
        super().__init__()
        self.show_only_go()

    def show_only_go(self):
        super().show_only_go()
        self.tic = time.time()

    def start_trial(self, event=None):
        pass

    def go_clicked(self, event=None):
        if self.go_displayed:
            self.trial_cnt += 1
            self.write_to_file()
            self.clear()
            play_correct()
            self.root.after(config.DELAY_AFTER_REWARD, self.show_only_go)

    def write_to_file(self):
        headers = ["subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "response_time",
                   "BACKGROUND_COLOR",
                   "SEPARATOR_COLOR",
                   "GO_BUTTON_COLOR",
                   "GO_BUTTON_WIDTH",
                   "SOUND_CORRECT"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [config.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.trial_cnt,
                  response_time,
                  BACKGROUND_COLOR,
                  SEPARATOR_COLOR,
                  GO_BUTTON_COLOR,
                  config.GO_BUTTON_WIDTH,
                  config.SOUND_CORRECT]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config.GO_BUTTON_TRAINING


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

    def start_trial(self, event=None):
        if self.use_zero_delay:
            self.delay_time = 0
        else:
            self.delay_time = random.choice(config.DELAY_TIMES)
        self.use_zero_delay = not self.use_zero_delay
        self.clear()
        self.display_random_symbol(config.SYMBOL_SHOW_TIME)
        self.root.after(config.SYMBOL_SHOW_TIME + self.delay_time, self.display_options,
                        self.sample)

    def display_random_symbol(self, display_time):
        self.sample = random.choice(config.SYMBOLS_MTS)
        self.top_canvas.delete(tk.ALL)
        self.display_symbol(self.sample, self.top_canvas)
        self.root.after(display_time, self.clear)
        # return symbol

    def display_options(self, correct_symbol, do_clear=True):
        incorrect_symbol = None
        found = False
        while not found:
            incorrect_symbol = random.choice(config.SYMBOLS_MTS)
            found = (incorrect_symbol != correct_symbol)
        if do_clear:
            self.clear()

        r = random.random()
        if r < 0.5:
            self.left_is_correct = True
            self.display_symbol(correct_symbol, self.middle_lcanvas)
            self.display_symbol(incorrect_symbol, self.middle_rcanvas)
            self.left_symbol = correct_symbol
            self.right_symbol = incorrect_symbol
        else:
            self.left_is_correct = False
            self.display_symbol(incorrect_symbol, self.middle_lcanvas)
            self.display_symbol(correct_symbol, self.middle_rcanvas)
            self.left_symbol = incorrect_symbol
            self.right_symbol = correct_symbol
        self.tic = time.time()

    def middle_limage_clicked(self, event=None):
        is_correct = self.left_is_correct
        if self.left_is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.write_to_file(self.left_symbol, is_correct)

    def middle_rimage_clicked(self, event=None):
        is_correct = not self.left_is_correct
        if self.left_is_correct:
            self.incorrect_choice()
        else:
            self.correct_choice()
        self.write_to_file(self.right_symbol, is_correct)

    def write_to_file(self, symbol_clicked, is_correct):
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
                   "is_correct",
                   "response_time",
                   "BACKGROUND_COLOR",
                   "SEPARATOR_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "SYMBOL_WIDTH",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD",
                   "SOUND_CORRECT",
                   "SOUND_INCORRECT",
                   "DELAY_TIMES",
                   "SYMBOL_SHOW_TIME"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.trial_cnt,
                  self.delay_time,
                  self.sample,
                  self.left_symbol,
                  self.right_symbol,
                  symbol_clicked,
                  is_correct,
                  response_time,
                  BACKGROUND_COLOR,
                  SEPARATOR_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config.SYMBOL_WIDTH,
                  config.NEXT_BUTTON_WIDTH,
                  config.BLACKOUT_TIME,
                  config.DELAY_AFTER_REWARD,
                  config.SOUND_CORRECT,
                  config.SOUND_INCORRECT,
                  config.DELAY_TIMES,
                  config.SYMBOL_SHOW_TIME]

        self.result_file.write(headers, values)

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

    def experiment_abbreviation(self):
        return config.DELAYED_MATCHING_TO_SAMPLE


class ZeroDelayMatchingToSample(DelayedMatchingToSample):
    def __init__(self):
        super().__init__()
        self.delay_time = 0

    def start_trial(self, event=None):
        self.clear()
        self.display_random_symbol(config.SYMBOL_SHOW_TIME)
        self.root.after(config.SYMBOL_SHOW_TIME, self.display_options, self.sample)

    def experiment_abbreviation(self):
        return config.ZERO_DELAY_MATCHING_TO_SAMPLE


class MatchingToSample(DelayedMatchingToSample):
    def __init__(self):
        super().__init__()
        self.delay_time = "na"

    def start_trial(self, event=None):
        self.clear()
        self.display_random_symbol()
        self.display_options(self.sample, do_clear=False)

    def display_random_symbol(self):
        self.sample = random.choice(config.SYMBOLS_MTS)
        self.display_symbol(self.sample, self.top_canvas)

    def experiment_abbreviation(self):
        return config.MATCHING_TO_SAMPLE


class Discrimination(Experiment):
    def __init__(self):
        super().__init__()
        self.go_waiting = None

    def show_only_go(self):
        super().show_only_go()
        self.tic = time.time()

    def show_only_next(self):
        super().show_only_next()
        if self.go_waiting is not None:
            self.write_to_file("nogo", not self.is_rewarding)

    def go_clicked(self, event=None):
        if self.go_waiting is not None:  # Cancel the pending job to remove the go button
            self.root.after_cancel(self.go_waiting)
            self.go_waiting = None
        if self.go_displayed:
            self.write_to_file("go", self.is_rewarding)
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
        all_sequences = [(config.SYMBOL1, config.SYMBOL1),
                         (config.SYMBOL1, config.SYMBOL2),
                         (config.SYMBOL2, config.SYMBOL1),
                         (config.SYMBOL2, config.SYMBOL2)]
        self.nonrewarding_sequences = [s for s in all_sequences if s != config.REWARDING_SEQUENCE]

    def start_trial(self, event=None):
        self.clear()
        self.display_random_sequence()
        time_to_go = 2 * config.STIMULUS_TIME + config.INTER_STIMULUS_TIME + config.RETENTION_TIME
        self.root.after(time_to_go, self.show_only_go)
        time_to_go_away = time_to_go + config.GO_BUTTON_DURATION
        self.go_waiting = self.root.after(time_to_go_away, self.show_only_next)

    def display_random_sequence(self):
        r = random.random()
        if r < 0.5:
            self.stimulus1, self.stimulus2 = config.REWARDING_SEQUENCE
        else:
            self.stimulus1, self.stimulus2 = random.choice(self.nonrewarding_sequences)
        self.top_canvas.delete(tk.ALL)
        self.display_symbol_top(self.stimulus1)
        self.root.after(config.STIMULUS_TIME, self.clear)
        self.root.after(config.STIMULUS_TIME + config.INTER_STIMULUS_TIME,
                        self.display_symbol_top, self.stimulus2)
        self.root.after(2 * config.STIMULUS_TIME + config.INTER_STIMULUS_TIME, self.clear)
        self.is_rewarding = ((self.stimulus1, self.stimulus2) == config.REWARDING_SEQUENCE)

    def write_to_file(self, go_or_nogo, is_correct):
        self.update_success_frequency(is_correct)
        headers = ["freq_correct",
                   "subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "stimulus1",
                   "stimulus2",
                   "response",
                   "is_correct",
                   "response_time",
                   "BACKGROUND_COLOR",
                   "SEPARATOR_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "SYMBOL_WIDTH",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD",
                   "SOUND_CORRECT",
                   "SOUND_INCORRECT",
                   "STIMULUS_TIME",
                   "GO_BUTTON_DURATION",
                   "RETENTION_TIME",
                   "GO_BUTTON_WIDTH",
                   "GO_BUTTON_COLOR",
                   "REWARDING_SEQUENCE",
                   "INTER_STIMULUS_TIME"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.trial_cnt,
                  self.stimulus1,
                  self.stimulus2,
                  go_or_nogo,
                  is_correct,
                  response_time,
                  BACKGROUND_COLOR,
                  SEPARATOR_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config.SYMBOL_WIDTH,
                  config.NEXT_BUTTON_WIDTH,
                  config.BLACKOUT_TIME,
                  config.DELAY_AFTER_REWARD,
                  config.SOUND_CORRECT,
                  config.SOUND_INCORRECT,
                  config.STIMULUS_TIME,
                  config.GO_BUTTON_DURATION,
                  config.RETENTION_TIME,
                  config.GO_BUTTON_WIDTH,
                  GO_BUTTON_COLOR,
                  config.REWARDING_SEQUENCE[0] + "_" + config.REWARDING_SEQUENCE[1],
                  config.INTER_STIMULUS_TIME]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config.SEQUENCE_DISCRIMINATION


class SingleStimulusDiscrimination(Discrimination):
    def __init__(self):
        super().__init__()

    def start_trial(self, event=None):
        self.clear()
        self.display_random_stimulus()
        time_to_go = config.STIMULUS_TIME + config.RETENTION_TIME
        self.root.after(time_to_go, self.show_only_go)
        time_to_go_away = time_to_go + config.GO_BUTTON_DURATION
        self.go_waiting = self.root.after(time_to_go_away, self.show_only_next)

    def display_random_stimulus(self):
        self.stimulus = random.choice(config.SYMBOLS_SS)
        self.top_canvas.delete(tk.ALL)
        self.display_symbol_top(self.stimulus)
        self.root.after(config.STIMULUS_TIME, self.clear)
        self.is_rewarding = (self.stimulus == config.REWARDING_STIMULUS)

    def write_to_file(self, go_or_nogo, is_correct):
        self.update_success_frequency(is_correct)
        headers = ["freq_correct",
                   "subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "stimulus",
                   "response",
                   "is_correct",
                   "response_time",
                   "BACKGROUND_COLOR",
                   "SEPARATOR_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "SYMBOL_WIDTH",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD",
                   "SOUND_CORRECT",
                   "SOUND_INCORRECT",
                   "STIMULUS_TIME",
                   "GO_BUTTON_DURATION",
                   "RETENTION_TIME",
                   "GO_BUTTON_WIDTH",
                   "GO_BUTTON_COLOR",
                   "REWARDING_STIMULUS"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.trial_cnt,
                  self.stimulus,
                  go_or_nogo,
                  is_correct,
                  response_time,
                  BACKGROUND_COLOR,
                  SEPARATOR_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config.SYMBOL_WIDTH,
                  config.NEXT_BUTTON_WIDTH,
                  config.BLACKOUT_TIME,
                  config.DELAY_AFTER_REWARD,
                  config.SOUND_CORRECT,
                  config.SOUND_INCORRECT,
                  config.STIMULUS_TIME,
                  config.GO_BUTTON_DURATION,
                  config.RETENTION_TIME,
                  config.GO_BUTTON_WIDTH,
                  GO_BUTTON_COLOR,
                  config.REWARDING_STIMULUS]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config.SINGLE_STIMULUS_DISCRIMINATION


def play_correct():
    _play(config.SOUND_CORRECT)


def play_incorrect():
    _play(config.SOUND_INCORRECT)


def _play(filename):
    if use_simpleaudio:
        wave_obj = simpleaudio.WaveObject.from_wave_file(filename)
        wave_obj.play()
        # play_obj = wave_obj.play()
        # play_obj.wait_done()
    else:
        if platform == "darwin":  # OSX
            subprocess.call(['afplay', filename])
        else:  # platform == "win32":
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
    unow = datetime.utcnow()
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


if __name__ == '__main__':
    e = None
    if config.EXPERIMENT == config.NEXT_BUTTON_TRAINING:
        e = NextButtonTraining()
    elif config.EXPERIMENT == config.GO_BUTTON_TRAINING:
        e = GoButtonTraining()
    elif config.EXPERIMENT == config.MATCHING_TO_SAMPLE:
        e = MatchingToSample()
    elif config.EXPERIMENT == config.ZERO_DELAY_MATCHING_TO_SAMPLE:
        e = ZeroDelayMatchingToSample()
    elif config.EXPERIMENT == config.DELAYED_MATCHING_TO_SAMPLE:
        e = DelayedMatchingToSample()
    elif config.EXPERIMENT == config.SEQUENCE_DISCRIMINATION:
        e = SequenceDiscrimination()
    elif config.EXPERIMENT == config.SINGLE_STIMULUS_DISCRIMINATION:
        e = SingleStimulusDiscrimination()
    else:
        print("Error: Undefined experiment name '" + config.EXPERIMENT + "'.")
    if e:
        e.root.mainloop()
