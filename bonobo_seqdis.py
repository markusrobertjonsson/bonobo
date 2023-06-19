import tkinter as tk
import random
import subprocess
import csv
import time
import os
from tkinter import PhotoImage
from sys import platform
from datetime import datetime

use_simpleaudio = True
try:
    import simpleaudio
except ModuleNotFoundError:
    use_simpleaudio = False

if platform == "win32":
    import winsound


def set_config():
    config = dict()

    # The experiment to run.
    config['SEQUENCE_DISCRIMINATION'] = "SeqDis"
    config['EXPERIMENT'] = config['SEQUENCE_DISCRIMINATION']

    # The subject exposed to the experiment. Used in the name of the result file and
    # as the "subject" column in the result file
    config['SUBJECT_TAG'] = "bonobo_name"


    ####################
    # General settings #
    ####################

    # Set to False or True
    config['HIDE_MOUSE_POINTER'] = False

    # The number of trials before the start screen appears automatically
    config['TRIALS_BEFORE_PAUSE'] = 60

    # The start screen
    config['START_SCREEN_COLOR_RGB'] = (255, 192, 203)

    # The background screen color in red, green, blue (each ranging from 0 to 255)
    config['BACKGROUND_COLOR_RGB'] = (0, 0, 0)

    # The color of the Next button
    config['NEXT_BUTTON_COLOR_RGB'] = (255, 255, 255)

    # The color of the "blackout" screen
    config['BLACKOUT_COLOR_RGB'] = (100, 100, 100)

    # Width (and height) of the Next button, as a fraction of H/3
    config['NEXT_BUTTON_WIDTH'] = 0.65

    # The time (in milliseconds) for the black screen after incorrect answer
    config['BLACKOUT_TIME'] = 3000

    # The delay (in milliseconds) after correct answer, before the next symbol is displayed
    config['DELAY_AFTER_REWARD'] = 1000

    # The name of the sound file to play if correct. File must be in the same directory as this file.
    config['SOUND_CORRECT'] = 'correct.wav'

    # The name of the sound file to play if incorrect. File must be in the same directory as this file.
    config['SOUND_INCORRECT'] = 'incorrect.wav'


    ###################################
    # General discrimination settings #
    ###################################

    # The time (in milliseconds) that the stimulus (each stimulus in sequences) is presented
    config['STIMULUS_TIME'] = 1500


    ####################################
    # Sequence discrimination settings #
    ####################################

    # The two colors in the sequence
    config['COLOR_A_RGB'] = (0, 0, 255)
    config['COLOR_B_RGB'] = (255, 255, 0)

    # The inter-stimulus time
    config['INTER_STIMULUS_TIME'] = 300

    # The symbol to the left to press after the sequence presentation, which is correct choice after
    # AB
    config['LEFT_OPTION'] = 'horizontal_lines.gif'

    # The symbol to the right to press after the sequence presentation, which is correct choice after
    # AA, BB and BA
    config['RIGHT_OPTION'] = 'vertical_lines.gif'

    return config

config = set_config()

random.seed()

hex_format = "#%02x%02x%02x"
START_SCREEN_COLOR = hex_format % config['START_SCREEN_COLOR_RGB']
BACKGROUND_COLOR = hex_format % config['BACKGROUND_COLOR_RGB']
NEXT_BUTTON_COLOR = hex_format % config['NEXT_BUTTON_COLOR_RGB']
BLACKOUT_COLOR = hex_format % config['BLACKOUT_COLOR_RGB']
COLOR_A = hex_format % config['COLOR_A_RGB']
COLOR_B = hex_format % config['COLOR_B_RGB']

frame_options = dict()  # For debugging frame positioning
# frame_options = {'highlightbackground': 'blue',
#                  'highlightcolor': 'blue',
#                  'highlightthickness': 1,
#                  'bd': 0}

canvas_options = {'bd': 0, 'highlightthickness': 0}
# canvas_options = {'bd': 3, 'highlightthickness': 3}

TOL = 0.99
TIMETOL = 3  # Round delay times to nearest millisecond


class Discrimination():
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
        self.image_files = {'horizontal_lines.gif': PhotoImage(file='horizontal_lines.gif'),
                            'vertical_lines.gif': PhotoImage(file='vertical_lines.gif')}
        self.root.update()
        for key, image_file in self.image_files.items():
            # scaling_factor = ceil(image_file.width() / self.left_canvas.winfo_width())
            scaling_factor = 1
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
        space_width = h / 3
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
        self.bottom_canvas_width = h * config['NEXT_BUTTON_WIDTH']
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

        if config['HIDE_MOUSE_POINTER']:
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
        L = self.canvas_width * config['GO_BUTTON_WIDTH']
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
        if self.finished_trial_cnt >= config['TRIALS_BEFORE_PAUSE']:
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
        subject = config['SUBJECT_TAG'].lower()
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
        job = self.root.after(config['DELAY_AFTER_REWARD'], self.get_ready_to_start_trial)
        self.current_after_jobs = [job]

    def incorrect_choice(self):
        # self.cancel_all_after_jobs()
        self.blackout()
        play_incorrect()
        job = self.root.after(config['BLACKOUT_TIME'], self.get_ready_to_start_trial)
        self.current_after_jobs = [job]


class SequenceDiscrimination(Discrimination):
    def __init__(self):
        super().__init__()
        self.options_displayed = False
        self.is_correct = True  # Initialize to False so that first sequence is taken from pot

        self.AA = (COLOR_A, COLOR_A)
        self.AB = (COLOR_A, COLOR_B)
        self.BA = (COLOR_B, COLOR_A)
        self.BB = (COLOR_B, COLOR_B)
        self.pot18 = []
        for s in [self.AA, self.AB, self.BA, self.BB]:
            if s == self.AB:
                self.pot18.extend([s] * 9)
            else:
                self.pot18.extend([s] * 3)
        self._create_new_sequences()

    def _create_new_sequences(self):
        random.shuffle(self.pot18)
        self.sequences = list(self.pot18)

    def start_trial(self, event=None):
        self.clear()
        job1, job2, job3 = self.display_random_sequence()
        self.current_after_jobs = [job1, job2, job3]
        time_to_options = 2 * config['STIMULUS_TIME'] + config['INTER_STIMULUS_TIME']
        job4 = self.root.after(time_to_options, self.display_options)
        self.current_after_jobs.append(job4)

    def display_random_sequence(self):
        if self.is_correct:
            self.stimulus1, self.stimulus2 = self.sequences.pop()
            if len(self.sequences) == 0:
                self._create_new_sequences()
        else:
            pass  # Repeat the previous sequence (i.e. keep self.stimulus{1,2}))

        # self.display_symbol_top(self.stimulus1)
        self._set_entire_screen_color(self.stimulus1)
        job1 = self.root.after(config['STIMULUS_TIME'], self.clear)
        job2 = self.root.after(config['STIMULUS_TIME'] + config['INTER_STIMULUS_TIME'],
                               self._set_entire_screen_color, self.stimulus2)
        job3 = self.root.after(2 * config['STIMULUS_TIME'] + config['INTER_STIMULUS_TIME'],
                               self.clear)
        self.current_after_jobs = [job1, job2, job3]
        self.is_AB = ((self.stimulus1, self.stimulus2) == self.AB)
        return job1, job2, job3

    def display_options(self):
        self.clear()
        self._display_symbol(config['LEFT_OPTION'], self.left_canvas)
        self._display_symbol(config['RIGHT_OPTION'], self.right_canvas)
        self.options_displayed = True
        self.tic = time.time()

    def _display_symbol(self, symbol, canvas, scale=1):
        w = canvas.winfo_width() / scale
        h = canvas.winfo_height() / scale
        canvas.create_image(w / 2, h / 2, image=self.image_files[symbol], anchor=tk.CENTER)

    def left_clicked(self, event=None):
        if self.options_displayed:
            self.is_correct = self.is_AB
            self._option_chosen("left")

    def right_clicked(self, event=None):
        if self.options_displayed:
            self.is_correct = not self.is_AB
            self._option_chosen("right")

    def _option_chosen(self, left_or_right):
        if self.is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.write_to_file(left_or_right)
        self.options_displayed = False

    def write_to_file(self, left_or_right):
        self.finished_trial_cnt += 1
        self.update_success_frequency(self.is_correct)
        presented = (self.stimulus1, self.stimulus2)
        sequence = None
        if presented == self.AA:
            sequence = "AA"
        elif presented == self.AB:
            sequence = "AB"
        elif presented == self.BA:
            sequence = "BA"
        else:
            sequence = "BB"

        headers = ["freq_correct",
                   "subject",
                   "experiment",
                   "date",
                   "timestamp",
                   "trial",
                   "sequence",
                   "stimulus1",
                   "stimulus2",
                   "response",
                   "is_correct",
                   "response_time",
                   "COLOR_A",
                   "COLOR_B",
                   "STIMULUS_TIME",
                   "INTER_STIMULUS_TIME",
                   "LEFT_OPTION",
                   "RIGHT_OPTION",
                   "BACKGROUND_COLOR",
                   "NEXT_BUTTON_COLOR",
                   "BLACKOUT_COLOR",
                   "NEXT_BUTTON_WIDTH",
                   "BLACKOUT_TIME",
                   "DELAY_AFTER_REWARD"]

        toc = time.time()
        response_time = round(toc - self.tic, TIMETOL)
        values = [self.success_frequency,
                  config['SUBJECT_TAG'],
                  self.experiment_abbreviation(),
                  datestamp(),
                  timestamp(),
                  self.started_trial_cnt,
                  sequence,
                  self.stimulus1,
                  self.stimulus2,
                  left_or_right,
                  self.is_correct,
                  response_time,
                  COLOR_A,
                  COLOR_B,
                  config['STIMULUS_TIME'],
                  config['INTER_STIMULUS_TIME'],
                  config['LEFT_OPTION'],
                  config['RIGHT_OPTION'],
                  BACKGROUND_COLOR,
                  NEXT_BUTTON_COLOR,
                  BLACKOUT_COLOR,
                  config['NEXT_BUTTON_WIDTH'],
                  config['BLACKOUT_TIME'],
                  config['DELAY_AFTER_REWARD']]

        self.result_file.write(headers, values)

    def experiment_abbreviation(self):
        return config['SEQUENCE_DISCRIMINATION']


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
    _play(config['SOUND_CORRECT'])


def play_incorrect():
    _play(config['SOUND_INCORRECT'])


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
    e = SequenceDiscrimination()
    e.root.mainloop()
