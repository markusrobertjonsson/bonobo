import tkinter as tk
import random
import subprocess
import config_dis
import csv
import time
import os
from tkinter import PhotoImage
from sys import platform
from datetime import datetime
from math import ceil  # sqrt  # , sin, cos, pi

use_simpleaudio = True
try:
    import simpleaudio
except ModuleNotFoundError:
    use_simpleaudio = False

if platform == "win32":
    import winsound

random.seed()

hex_format = "#%02x%02x%02x"
START_SCREEN_COLOR = hex_format % config_dis.START_SCREEN_COLOR_RGB
BACKGROUND_COLOR = hex_format % config_dis.BACKGROUND_COLOR_RGB
NEXT_BUTTON_COLOR = hex_format % config_dis.NEXT_BUTTON_COLOR_RGB
GO_BUTTON_COLOR = hex_format % config_dis.GO_BUTTON_COLOR_RGB
BLACKOUT_COLOR = hex_format % config_dis.BLACKOUT_COLOR_RGB

frame_options = dict()  # For debugging frame positioning
# frame_options = {'highlightbackground': 'blue',
#                  'highlightcolor': 'blue',
#                  'highlightthickness': 1,
#                  'bd': 0}

canvas_options = {'bd': 0, 'highlightthickness': 0}
# canvas_options = {'bd': 3, 'highlightthickness': 3}

TOL = 0.99
TIMETOL = 3  # Round delay times to nearest millisecond


class Discrimination2():
    def __init__(self):
        filename = self.result_filename()
        self.result_file = ResultFile(filename)
        self.started_trial_cnt = 0
        self.finished_trial_cnt = 0

        # Current self.root.after jobs. They are stored to be able to cancel them in space_pressed.
        self.current_after_jobs = []

        # A list of the last 20 trials, 0 means unuccessful, 1 means successful
        self.success_list = []

        # The success frequency of the last 20 rounds
        self.success_frequency = 0

        self._make_widgets()
        self._make_images()

        self.set_background_color(BACKGROUND_COLOR)
        self.next_displayed = False
        self.go_displayed = False
        self.stimulus_displayed = False
        self.blackout_displayed = False
        self.pause_screen_displayed = False
        self.display_pause_screen()

    def _make_images(self):
        self.image_files = {'circle.gif': PhotoImage(file='circle.gif'),
                            'diamond.gif': PhotoImage(file='diamond.gif'),
                            'star.gif': PhotoImage(file='star.gif'),
                            'balls.gif': PhotoImage(file='balls.gif')}
        self.root.update()
        for key, image_file in self.image_files.items():
            scaling_factor = ceil(image_file.width() / self.left_canvas.winfo_width())
            self.image_files[key] = image_file.subsample(scaling_factor)

    def _make_widgets(self):
        self.root = tk.Tk()

        W = self.root.winfo_screenwidth() * TOL
        H = self.root.winfo_screenheight() * TOL
        h = H / 3

        # self.root.attributes('-zoomed', True)  # Maximize window

        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)
        self.root.bind("<space>", self.space_pressed)

        # TOP
        self.top_frame = tk.Frame(self.root, width=W, height=h, **frame_options)
        self.top_frame.pack_propagate(False)
        self.top_frame.pack(expand=True, side=tk.TOP)

        # MIDDLE
        space_width = h / 10
        self.middle_frame = tk.Frame(self.root, width=W, height=h, **frame_options)

        self.middle_left_frame = tk.Frame(self.middle_frame, width=(W - space_width) / 2, height=h,
                                          **frame_options)
        self.middle_left_frame.pack_propagate(False)
        self.middle_left_frame.pack(side=tk.LEFT)

        self.middle_space_frame = tk.Frame(self.middle_frame, width=space_width, height=h,
                                           **frame_options)
        self.middle_space_frame.pack_propagate(False)
        self.middle_space_frame.pack(side=tk.LEFT)
        self.middle_right_frame = tk.Frame(self.middle_frame, width=(W - space_width) / 2,
                                           height=h, **frame_options)
        self.middle_right_frame.pack_propagate(False)
        self.middle_right_frame.pack(side=tk.LEFT)

        self.canvas_width = h
        self.left_canvas = tk.Canvas(self.middle_left_frame, width=self.canvas_width,
                                     height=self.canvas_width, **canvas_options)
        self.left_canvas.bind("<Button-1>", self.left_clicked)
        self.left_canvas.pack(side=tk.RIGHT)

        self.right_canvas = tk.Canvas(self.middle_right_frame, width=self.canvas_width,
                                      height=self.canvas_width, **canvas_options)
        self.right_canvas.bind("<Button-1>", self.right_clicked)
        self.right_canvas.pack(side=tk.LEFT)

        self.middle_frame.pack_propagate(False)
        self.middle_frame.pack(expand=True, side=tk.TOP)

        # BOTTOM
        self.bottom_frame = tk.Frame(self.root, width=W, height=h, **frame_options)
        self.bottom_canvas_width = h * config_dis.NEXT_BUTTON_WIDTH
        self.bottom_canvas = tk.Canvas(self.bottom_frame, width=self.bottom_canvas_width,
                                       height=self.bottom_canvas_width, **canvas_options)
        self.bottom_canvas.bind("<Button-1>", self.next_clicked)
        self.bottom_canvas.pack(expand=True)

        self.bottom_frame.pack_propagate(False)
        self.bottom_frame.pack(expand=True, side=tk.BOTTOM)

        self.root.update()
        w = self.bottom_canvas.winfo_width()
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

        if config_dis.HIDE_MOUSE_POINTER:
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

    def blackout(self):
        self._set_entire_screen_color(BLACKOUT_COLOR)
        self.blackout_displayed = True

    def display_pause_screen(self):
        self._set_entire_screen_color(START_SCREEN_COLOR)
        self.pause_screen_displayed = True
        self.blackout_displayed = False

    def _set_entire_screen_color(self, color):
        self.clear_canvases()
        self.set_background_color(color)

    def set_background_color(self, color):
        # Root
        self.root.configure(background=color)
        # Frames
        self.top_frame.configure(background=color)
        self.middle_frame.configure(background=color)
        self.middle_left_frame.configure(background=color)
        self.middle_space_frame.configure(background=color)
        self.middle_right_frame.configure(background=color)
        self.bottom_frame.configure(background=color)
        # Canvases
        self.left_canvas.configure(background=color)
        self.right_canvas.configure(background=color)
        self.bottom_canvas.configure(background=color)

    def clear(self):
        self.set_background_color(BACKGROUND_COLOR)
        self.clear_canvases()

    def clear_canvases(self):
        self.left_canvas.delete(tk.ALL)
        self.right_canvas.delete(tk.ALL)
        self.bottom_canvas.delete(tk.ALL)
        self.next_displayed = False
        self.go_displayed = False
        self.stimulus_displayed = False

    def show_only_next(self):
        self.clear()
        self.display_next()

    def display_next(self):
        self.bottom_canvas.create_polygon(*self.next_symbol_args, fill=NEXT_BUTTON_COLOR,
                                          outline='', width=0)
        self.next_displayed = True

    def show_only_go_button(self):
        self.clear()
        self.display_go_button()

    def display_go_button(self):
        L = self.canvas_width * config_dis.GO_BUTTON_WIDTH
        margin = (self.canvas_width - L) / 2
        self.right_canvas.create_polygon(margin, margin,
                                         self.canvas_width - margin, margin,
                                         self.canvas_width - margin, self.canvas_width - margin,
                                         margin, self.canvas_width - margin,
                                         fill=BACKGROUND_COLOR,
                                         outline=GO_BUTTON_COLOR,
                                         width=L / 5)
        self.go_displayed = True
        self.tic = time.time()

    def display_stimulus_symbol(self, symbol, canvas):
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        canvas.create_image(w / 2, h / 2, image=self.image_files[symbol], anchor=tk.CENTER)
        self.stimulus_displayed = True

    def next_clicked(self, event=None):
        if self.next_displayed:
            self.next_displayed = False
            self.started_trial_cnt += 1
            self.start_trial()

    def space_pressed(self, event=None):
        if self.pause_screen_displayed:
            self.get_ready_to_start_trial()
            self.pause_screen_displayed = False
        else:
            self.display_pause_screen()
            self.cancel_all_after_jobs()

    def get_ready_to_start_trial(self):
        self.blackout_displayed = False
        if self.finished_trial_cnt >= config_dis.TRIALS_BEFORE_PAUSE:
            self.display_pause_screen()
            self.finished_trial_cnt = 0
        else:
            self.clear()
            self.display_next()

    def cancel_all_after_jobs(self):
        for ind, job in enumerate(self.current_after_jobs):
            self.root.after_cancel(job)
            self.current_after_jobs[ind] = None
        self.current_after_jobs = []

    def start_trial(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def left_clicked(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def right_clicked(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def result_filename(self):
        """
        Return the file name of the result file.
        """
        experiment = self.experiment_abbreviation()
        subject = config_dis.SUBJECT_TAG.lower()
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
        job = self.root.after(config_dis.DELAY_AFTER_REWARD, self.get_ready_to_start_trial)
        self.current_after_jobs = [job]

    def incorrect_choice(self):
        # self.cancel_all_after_jobs()
        self.blackout()
        play_incorrect()
        job = self.root.after(config_dis.BLACKOUT_TIME, self.get_ready_to_start_trial)
        self.current_after_jobs = [job]


class SingleStimulusDiscrimination2(Discrimination2):
    def __init__(self):
        super().__init__()
        # If the currently shown stimulus should give reward for pressing go
        self.is_go_stimulus = False

    def start_trial(self, event=None):
        self.clear()
        self.display_random_stimulus()
        time_to_go_button = config_dis.STIMULUS_TIME
        job1 = self.root.after(time_to_go_button, self.show_only_go_button)
        self.current_after_jobs = [job1]

        time_go_button_displayed = config_dis.GO_BUTTON_DURATION_NOGO
        if self.is_go_stimulus:
            time_go_button_displayed = config_dis.GO_BUTTON_DURATION_GO

        job2 = self.root.after(time_to_go_button + time_go_button_displayed, self.show_only_next)
        self.current_after_jobs.append(job2)

    def display_random_stimulus(self):
        self.stimulus = random.choice([config_dis.SS_STIMULUS_A, config_dis.SS_STIMULUS_B])
        self.left_canvas.delete(tk.ALL)
        self.display_stimulus_symbol(self.stimulus, self.left_canvas)
        self.is_go_stimulus = (self.stimulus == config_dis.SS_STIMULUS_A)

    def left_clicked(self, event=None):
        if self.blackout_displayed:
            return
        if self.pause_screen_displayed:
            return
        if self.next_displayed:
            return
        if self.go_displayed:
            return
        self.cancel_all_after_jobs()
        self.incorrect_choice()

    def right_clicked(self, event=None):
        if self.blackout_displayed:
            return
        if self.pause_screen_displayed:
            return
        if self.next_displayed:
            return
        if self.go_displayed:
            if self.is_go_stimulus:
                self.correct_choice()
            else:
                self.incorrect_choice()
            self.write_to_file("go", self.is_go_stimulus)

    def show_only_next(self):
        if self.go_displayed:
            if self.is_go_stimulus:
                self.incorrect_choice()
            else:
                self.correct_choice()
            self.write_to_file("nogo", not self.is_go_stimulus)

    def write_to_file(self, go_or_nogo, is_correct):
        self.finished_trial_cnt += 1
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
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD",
                   "STIMULUS_TIME",
                   "GO_BUTTON_DURATION_GO",
                   "GO_BUTTON_DURATION_NOGO",
                   "GO_BUTTON_WIDTH",
                   "GO_BUTTON_COLOR",
                   "SS_STIMULUS_A"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config_dis.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.started_trial_cnt,
                  self.stimulus,
                  go_or_nogo,
                  is_correct,
                  response_time,
                  BACKGROUND_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config_dis.NEXT_BUTTON_WIDTH,
                  config_dis.BLACKOUT_TIME,
                  config_dis.DELAY_AFTER_REWARD,
                  config_dis.STIMULUS_TIME,
                  config_dis.GO_BUTTON_DURATION_GO,
                  config_dis.GO_BUTTON_DURATION_NOGO,
                  config_dis.GO_BUTTON_WIDTH,
                  GO_BUTTON_COLOR,
                  config_dis.SS_STIMULUS_A]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config_dis.SINGLE_STIMULUS_DISCRIMINATION


class SingleStimulusPretrainingA_Go(Discrimination2):
    def __init__(self):
        super().__init__()

    def start_trial(self, event=None):
        self.show_only_go_button()
        job = self.root.after(config_dis.GO_BUTTON_DURATION_GO, self.nogo)
        self.current_after_jobs = [job]

    def right_clicked(self, event=None):
        if self.go_displayed:
            self.cancel_all_after_jobs()
            self.correct_choice()
            self.write_to_file("go", True)

    def nogo(self):
        self.incorrect_choice()
        self.write_to_file("nogo", False)

    def write_to_file(self, go_or_nogo, is_correct):
        self.finished_trial_cnt += 1
        self.update_success_frequency(is_correct)
        headers = ["freq_correct",
                   "subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "response",
                   "is_correct",
                   "response_time",
                   "BACKGROUND_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD",
                   "GO_BUTTON_DURATION_GO",
                   "GO_BUTTON_WIDTH",
                   "GO_BUTTON_COLOR"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config_dis.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.started_trial_cnt,
                  go_or_nogo,
                  is_correct,
                  response_time,
                  BACKGROUND_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config_dis.NEXT_BUTTON_WIDTH,
                  config_dis.BLACKOUT_TIME,
                  config_dis.DELAY_AFTER_REWARD,
                  config_dis.GO_BUTTON_DURATION_GO,
                  config_dis.GO_BUTTON_WIDTH,
                  GO_BUTTON_COLOR]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config_dis.SSDIS_PRETRAININGA_GO


class SingleStimulusPretrainingA_AandGo(Discrimination2):
    def __init__(self):
        super().__init__()

    def start_trial(self, event=None):
        self.show_only_go_button()
        self.display_stimulus_symbol(config_dis.SS_STIMULUS_A, self.left_canvas)
        job = self.root.after(config_dis.GO_BUTTON_DURATION_GO, self.nogo)
        self.current_after_jobs = [job]

    def left_clicked(self, event=None):
        if self.go_displayed:
            self.incorrect_choice()

    def right_clicked(self, event=None):
        if self.go_displayed:
            self.cancel_all_after_jobs()
            self.correct_choice()
            self.write_to_file("go", True)

    def nogo(self):
        if self.go_displayed:
            self.incorrect_choice()
            self.write_to_file("nogo", False)

    def write_to_file(self, go_or_nogo, is_correct):
        self.finished_trial_cnt += 1
        self.update_success_frequency(is_correct)
        headers = ["freq_correct",
                   "subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "response",
                   "is_correct",
                   "response_time",
                   "SS_STIMULUS_A",
                   "BACKGROUND_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD",
                   "GO_BUTTON_DURATION_GO",
                   "GO_BUTTON_WIDTH",
                   "GO_BUTTON_COLOR"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config_dis.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.started_trial_cnt,
                  go_or_nogo,
                  is_correct,
                  response_time,
                  config_dis.SS_STIMULUS_A,
                  BACKGROUND_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config_dis.NEXT_BUTTON_WIDTH,
                  config_dis.BLACKOUT_TIME,
                  config_dis.DELAY_AFTER_REWARD,
                  config_dis.GO_BUTTON_DURATION_GO,
                  config_dis.GO_BUTTON_WIDTH,
                  GO_BUTTON_COLOR]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config_dis.SSDIS_PRETRAININGA_A_AND_GO


class SingleStimulusPretrainingA_AThenGo(Discrimination2):
    def __init__(self):
        super().__init__()

    def start_trial(self, event=None):
        self.clear()
        self.display_stimulus_symbol(config_dis.SS_STIMULUS_A, self.left_canvas)
        job1 = self.root.after(config_dis.STIMULUS_TIME, self.show_only_go_button)
        self.current_after_jobs = [job1]
        job2 = self.root.after(config_dis.STIMULUS_TIME + config_dis.GO_BUTTON_DURATION_GO,
                               self.nogo)
        self.current_after_jobs.append(job2)

    def left_clicked(self, event=None):
        if self.stimulus_displayed:
            self.cancel_all_after_jobs()
            self.incorrect_choice()

    def right_clicked(self, event=None):
        if self.go_displayed:
            self.cancel_all_after_jobs()
            self.correct_choice()
            self.write_to_file("go", True)

    def nogo(self):
        if self.go_displayed:
            self.incorrect_choice()
            self.write_to_file("nogo", False)

    def write_to_file(self, go_or_nogo, is_correct):
        self.finished_trial_cnt += 1
        self.update_success_frequency(is_correct)
        headers = ["freq_correct",
                   "subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "response",
                   "is_correct",
                   "response_time",
                   "SS_STIMULUS_A",
                   "BACKGROUND_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD",
                   "GO_BUTTON_DURATION_GO",
                   "GO_BUTTON_WIDTH",
                   "GO_BUTTON_COLOR"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config_dis.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.started_trial_cnt,
                  go_or_nogo,
                  is_correct,
                  response_time,
                  config_dis.SS_STIMULUS_A,
                  BACKGROUND_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config_dis.NEXT_BUTTON_WIDTH,
                  config_dis.BLACKOUT_TIME,
                  config_dis.DELAY_AFTER_REWARD,
                  config_dis.GO_BUTTON_DURATION_GO,
                  config_dis.GO_BUTTON_WIDTH,
                  GO_BUTTON_COLOR]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config_dis.SSDIS_PRETRAININGA_A_THEN_GO


class SingleStimulusPretrainingB(Discrimination2):
    def __init__(self):
        super().__init__()

    def start_trial(self, event=None):
        self.clear()
        self.display_stimulus_symbol(config_dis.SS_STIMULUS_B, self.left_canvas)
        self.tic = time.time()
        job = self.root.after(config_dis.GO_BUTTON_DURATION_NOGO, self.nogo)
        self.current_after_jobs = [job]

    def left_clicked(self, event=None):
        if self.stimulus_displayed:
            self.cancel_all_after_jobs()
            self.incorrect_choice()

    def nogo(self):
        self.correct_choice()
        self.write_to_file("nogo", True)

    def write_to_file(self, go_or_nogo, is_correct):
        self.finished_trial_cnt += 1
        self.update_success_frequency(is_correct)
        headers = ["freq_correct",
                   "subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "response",
                   "is_correct",
                   "response_time",
                   "SS_STIMULUS_B",
                   "BACKGROUND_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD",
                   "GO_BUTTON_DURATION_GO",
                   "GO_BUTTON_WIDTH",
                   "GO_BUTTON_COLOR"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config_dis.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.started_trial_cnt,
                  go_or_nogo,
                  is_correct,
                  response_time,
                  config_dis.SS_STIMULUS_B,
                  BACKGROUND_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config_dis.NEXT_BUTTON_WIDTH,
                  config_dis.BLACKOUT_TIME,
                  config_dis.DELAY_AFTER_REWARD,
                  config_dis.GO_BUTTON_DURATION_GO,
                  config_dis.GO_BUTTON_WIDTH,
                  GO_BUTTON_COLOR]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config_dis.SSDIS_PRETRAININGB


class SingleStimulusPretrainingB_BandGo(Discrimination2):
    def __init__(self):
        super().__init__()

    def start_trial(self, event=None):
        self.show_only_go_button()
        self.display_stimulus_symbol(config_dis.SS_STIMULUS_B, self.left_canvas)
        job = self.root.after(config_dis.GO_BUTTON_DURATION_NOGO, self.nogo)
        self.current_after_jobs = [job]

    def left_clicked(self, event=None):
        if self.go_displayed:
            self.incorrect_choice()

    def right_clicked(self, event=None):
        if self.go_displayed:
            self.cancel_all_after_jobs()
            self.incorrect_choice()
            self.write_to_file("go", True)

    def nogo(self):
        if self.go_displayed:
            self.correct_choice()
            self.write_to_file("nogo", False)

    def write_to_file(self, go_or_nogo, is_correct):
        self.finished_trial_cnt += 1
        self.update_success_frequency(is_correct)
        headers = ["freq_correct",
                   "subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "response",
                   "is_correct",
                   "response_time",
                   "SS_STIMULUS_B",
                   "BACKGROUND_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD",
                   "GO_BUTTON_DURATION_GO",
                   "GO_BUTTON_WIDTH",
                   "GO_BUTTON_COLOR"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config_dis.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.started_trial_cnt,
                  go_or_nogo,
                  is_correct,
                  response_time,
                  config_dis.SS_STIMULUS_B,
                  BACKGROUND_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config_dis.NEXT_BUTTON_WIDTH,
                  config_dis.BLACKOUT_TIME,
                  config_dis.DELAY_AFTER_REWARD,
                  config_dis.GO_BUTTON_DURATION_GO,
                  config_dis.GO_BUTTON_WIDTH,
                  GO_BUTTON_COLOR]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config_dis.SSDIS_PRETRAININGB_B_AND_GO


class SingleStimulusPretrainingB_BThenGo(Discrimination2):
    def __init__(self):
        super().__init__()

    def start_trial(self, event=None):
        self.clear()
        self.display_stimulus_symbol(config_dis.SS_STIMULUS_B, self.left_canvas)
        job1 = self.root.after(config_dis.STIMULUS_TIME, self.show_only_go_button)
        self.current_after_jobs = [job1]
        job2 = self.root.after(config_dis.STIMULUS_TIME + config_dis.GO_BUTTON_DURATION_NOGO,
                               self.nogo)
        self.current_after_jobs.append(job2)

    def left_clicked(self, event=None):
        if self.stimulus_displayed:
            self.cancel_all_after_jobs()
            self.incorrect_choice()

    def right_clicked(self, event=None):
        if self.go_displayed:
            self.cancel_all_after_jobs()
            self.incorrect_choice()
            self.write_to_file("go", False)

    def nogo(self):
        if self.go_displayed:
            self.correct_choice()
            self.write_to_file("nogo", True)

    def write_to_file(self, go_or_nogo, is_correct):
        self.finished_trial_cnt += 1
        self.update_success_frequency(is_correct)
        headers = ["freq_correct",
                   "subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "response",
                   "is_correct",
                   "response_time",
                   "SS_STIMULUS_B",
                   "BACKGROUND_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD",
                   "GO_BUTTON_DURATION_GO",
                   "GO_BUTTON_WIDTH",
                   "GO_BUTTON_COLOR"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config_dis.SUBJECT_TAG,
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.started_trial_cnt,
                  go_or_nogo,
                  is_correct,
                  response_time,
                  config_dis.SS_STIMULUS_B,
                  BACKGROUND_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config_dis.NEXT_BUTTON_WIDTH,
                  config_dis.BLACKOUT_TIME,
                  config_dis.DELAY_AFTER_REWARD,
                  config_dis.GO_BUTTON_DURATION_GO,
                  config_dis.GO_BUTTON_WIDTH,
                  GO_BUTTON_COLOR]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config_dis.SSDIS_PRETRAININGB_B_THEN_GO


class SequenceDiscrimination2(Discrimination2):
    def __init__(self):
        super().__init__()
        # If the currently shown stimulus should give reward for pressing go
        self.is_go_sequence = False

    def experiment_abbreviation(self):
        return config_dis.SEQUENCE_DISCRIMINATION


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


def play_correct():
    _play(config_dis.SOUND_CORRECT)


def play_incorrect():
    _play(config_dis.SOUND_INCORRECT)


def _play(filename):
    if use_simpleaudio:
        wave_obj = simpleaudio.WaveObject.from_wave_file(filename)
        wave_obj.play()
        # play_obj = wave_obj.play()
        # play_obj.wait_done()
    else:
        if platform == "darwin":  # OSX
            subprocess.call(['afplay', filename])
        elif platform == "win32":  # Windows
            winsound.PlaySound(filename, winsound.SND_FILENAME)
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


if __name__ == '__main__':
    e = None
    if config_dis.EXPERIMENT == config_dis.SEQUENCE_DISCRIMINATION:
        e = SequenceDiscrimination2()
    elif config_dis.EXPERIMENT == config_dis.SINGLE_STIMULUS_DISCRIMINATION:
        e = SingleStimulusDiscrimination2()
    elif config_dis.EXPERIMENT == config_dis.SSDIS_PRETRAININGA_GO:
        e = SingleStimulusPretrainingA_Go()
    elif config_dis.EXPERIMENT == config_dis.SSDIS_PRETRAININGA_A_AND_GO:
        e = SingleStimulusPretrainingA_AandGo()
    elif config_dis.EXPERIMENT == config_dis.SSDIS_PRETRAININGA_A_THEN_GO:
        e = SingleStimulusPretrainingA_AThenGo()
    elif config_dis.EXPERIMENT == config_dis.SSDIS_PRETRAININGB:
        e = SingleStimulusPretrainingB()
    elif config_dis.EXPERIMENT == config_dis.SSDIS_PRETRAININGB_B_AND_GO:
        e = SingleStimulusPretrainingB_BandGo()
    elif config_dis.EXPERIMENT == config_dis.SSDIS_PRETRAININGB_B_THEN_GO:
        e = SingleStimulusPretrainingB_BThenGo()
    else:
        print("Error: Undefined experiment name '" + config_dis.EXPERIMENT + "'.")
    if e:
        e.root.mainloop()
