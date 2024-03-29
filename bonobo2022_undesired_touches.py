import tkinter as tk
import random
import subprocess
import config2022 as config
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
START_SCREEN_COLOR = hex_format % config.START_SCREEN_COLOR_RGB
BACKGROUND_COLOR = hex_format % config.BACKGROUND_COLOR_RGB
NEXT_BUTTON_COLOR = hex_format % config.NEXT_BUTTON_COLOR_RGB
BLACKOUT_COLOR = hex_format % config.BLACKOUT_COLOR_RGB

frame_options = dict()  # For debugging frame positioning
# frame_options = {'highlightbackground': 'blue',
#                  'highlightcolor': 'blue',
#                  'highlightthickness': 1,
#                  'bd': 0}

canvas_options = {'bd': 0, 'highlightthickness': 0}
# canvas_options = {'bd': 1, 'highlightthickness': 1}

TOL = 0.33  # 0.99
TIMETOL = 3  # Round delay times to nearest millisecond


class Gui():
    def __init__(self, use_screen2=False):
        self.use_screen2 = use_screen2
        self._make_widgets()
        self._make_images()
 
        # PhotoImage() (used in _make_images()) can only be called after creation of Tk() (used in _make_widgets)
        self.stimulus_window = None
        if self.use_screen2:
            self.stimulus_window = StimulusWindow(self)

        self.next_displayed = False
        self.stimulus_displayed = False
        self.options_displayed = False
        self.blackout_displayed = False
        self.pause_screen_displayed = False
        self.snack_time = False

    def _make_images(self):
        self.image_files = {'blue_star.gif': PhotoImage(file='blue_star.gif'),
                            'yellow_circle.gif': PhotoImage(file='yellow_circle.gif'),
                            'white_star.gif': PhotoImage(file='white_star.gif'),
                            'white_circle.gif': PhotoImage(file='white_circle.gif'),
                            'circle.gif': PhotoImage(file='circle.gif'),
                            'diamond.gif': PhotoImage(file='diamond.gif'),
                            'star.gif': PhotoImage(file='star.gif'),
                            'balls.gif': PhotoImage(file='balls.gif'),
                            'blue_circles.gif': PhotoImage(file='blue_circles.gif'),
                            'yellow_diamond.gif': PhotoImage(file='yellow_diamond.gif'),
                            'green_circles.gif': PhotoImage(file='green_circles.gif'),
                            'red_circles.gif': PhotoImage(file='red_circles.gif'),
                            'red_diamond.gif': PhotoImage(file='red_diamond.gif'),
                            'horizontal_lines.gif': PhotoImage(file='horizontal_lines.gif'),
                            'vertical_lines.gif': PhotoImage(file='vertical_lines.gif'),
                            'horizontal_button.gif': PhotoImage(file='horizontal_button.gif'),
                            'vertical_button.gif': PhotoImage(file='vertical_button.gif'),
                            'pink_circle.gif': PhotoImage(file='pink_circle.gif'),
                            'happy_face.gif': PhotoImage(file='happy_face.gif'),
                            'sad_face.gif': PhotoImage(file='sad_face.gif')}
        
        # Just to make sure there are 20 after meddling with the dict above
        assert(len(self.image_files) == 20)

        self.root.update()
        for key, image_file in self.image_files.items():
            scaling_factor = ceil(image_file.width() / self.canvas['11'].winfo_width())
            self.image_files[key] = image_file.subsample(scaling_factor)

    def _make_widgets(self):

        # For dual screen setup, self.root.winfo_screenwidth() returns the sum of the two screen
        # widths. The below is to get only one screen (the screen where the window is launched)
        t = tk.Tk()  # Create a temporary window
        # t.attributes("-alpha", 00)  # Set max transparency (min opacity)
        t.attributes('-fullscreen', True)  # Maximize window
        t.update()
        self.screen_width = t.winfo_width()
        self.screen_height = t.winfo_height()
        t.destroy()  # Delete the temporary window

        self.root = tk.Tk()

        W = self.screen_width * TOL
        H = self.screen_height * TOL
        h = H / 4
        w = W / 3

        # print(f"self.root.winfo_screenwidth()={self.root.winfo_screenwidth()}")
        # print(f"self.root.winfo_screenheight()={self.root.winfo_screenheight()}")

        self.canvas_width = h

        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

        self.is_pointer_visible = True
        self.root.bind("<F10>", self.toggle_pointer_visibility)

        self.frame = dict()
        self.canvas = dict()
        for i in ['1', '2', '3', '4']:
            self.frame[i] = tk.Frame(self.root, width=W, height=h, **frame_options)
            self.frame[i].pack(side=tk.TOP, anchor=tk.N)
            for j in ['1', '2', '3']:
                self.frame[i + j] = tk.Frame(self.frame[i], width=w, height=h, **frame_options )
                self.frame[i + j].pack_propagate(False)
                self.frame[i + j].pack(side=tk.LEFT)
                self.canvas[i + j] = tk.Canvas(self.frame[i + j], width=h, height=h, **canvas_options)
                self.canvas[i + j].place(relx=.5, rely=.5, anchor="center")
                # self.canvas[i + j].pack(side=tk.BOTTOM)
                # self.canvas[i + j].pack(anchor=tk.S)

        self.root.update()
        w = self.canvas['32'].winfo_width()
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

        if config.HIDE_MOUSE_POINTER:
            # Hide mouse pointer
            self.toggle_pointer_visibility()

        self.root.title("Main Window")
        self.root.protocol("WM_DELETE_WINDOW", self.delete_window)

    def set_background_color(self, color):
        # Root
        self.root.configure(background=color)
        # Frames
        for frame in self.frame.values():            
            frame.configure(background=color)
        # Canvases
        for canvas in self.canvas.values():
            canvas.configure(background=color)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen  # Just toggling the boolean
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def toggle_pointer_visibility(self, event=None):
        if self.is_pointer_visible:
            # Hide mouse pointer
            self.root.config(cursor='none')
        else:
            self.root.config(cursor='')
        self.is_pointer_visible = not self.is_pointer_visible

    def end_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
        return "break"

    def _set_entire_screen_color(self, color):
        self.clear_canvases()
        self.set_background_color(color)

    def clear(self):
        self.set_background_color(BACKGROUND_COLOR)
        self.clear_canvases()
        if self.stimulus_window:
            self.stimulus_window.clear()

    def clear_canvases(self):
        for canvas in self.canvas.values():
            canvas.delete(tk.ALL)
        self.next_displayed = False
        self.stimulus_displayed = False
        self.options_displayed = False

    def delete_window(self):
        exit(0)

    def blackout(self, color=BLACKOUT_COLOR):
        self._set_entire_screen_color(color)
        self.blackout_displayed = True
        if self.stimulus_window:
            self.stimulus_window.blackout()

    def show_only_next(self):
        self.clear()
        self.display_next()

    def display_next(self):
        self.canvas['42'].create_polygon(*self.next_symbol_args, fill=NEXT_BUTTON_COLOR,
                                          outline='', width=0)
        self.next_displayed = True

    def display_stimulus(self, stimulus, shape_scale, fraction=1, force_mid=False):
        _display_shape(stimulus, self.canvas['12'], shape_scale, fraction)
        self.stimulus_displayed = True

    def _display_image(self, symbol, canvas):
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        canvas.create_image(w / 2, h / 2, image=self.image_files[symbol], anchor=tk.CENTER)

    def display_pause_screen(self):
        if self.stimulus_window:
            self.stimulus_window.display_pause_screen()
        self._set_entire_screen_color(START_SCREEN_COLOR)
        self.pause_screen_displayed = True
        self.blackout_displayed = False
        self.snack_time = False

    # def _screen_touched(self):
    #     if self.pause_screen_displayed:
    #         return "PS"  # Pause/Pink screen
    #     elif self.next_displayed:
    #         return "NBS"  # Next button screen
    #     elif self.blackout_displayed:
    #         return "BS"  # Blackout screen
    #     elif self.options_displayed:
    #         return "RS"  # Response screen
    #     elif self.snack_time:
    #         return "ST"  # Snack time
    #     elif self.stimulus_displayed:
    #         return "SS"  # Stimulus screen
    #     else:
    #         return "None"

    # def _cell_touched(self, x, y):
    #     w = self.screen_width
    #     h = self.screen_height
    #     if x <= w / 3:
    #         horiz = 'L'
    #     elif x <= 2 * w / 3:
    #         horiz = 'M'
    #     else:
    #         horiz = 'R'

    #     if y <= h / 3:
    #         vert = 'T'
    #     elif y <= 2 * h / 3:
    #         vert = 'M'
    #     else:
    #         vert = 'B'
    #     return horiz + vert


class Experiment():
    def __init__(self, gui, is_combination=False):
        self.gui = gui

        for key, canvas in self.gui.canvas.items():
            canvas.bind("<Button-1>", lambda e=None, k=key: self.canvas_clicked(e, k))
        self.gui.root.bind("<space>", self.space_pressed)
        if gui.use_screen2:
            self.gui.stimulus_window.root.bind("<space>", self.space_pressed)

        self.is_combination = is_combination
        self.sub_experiment_index = None
        filename = self.result_filename()
        self.result_file = ResultFile(filename)
        self.started_trial_cnt = 0
        self.finished_trial_cnt = 0
        self.clicked_option = None

        # Current self.gui.root.after jobs. Stored here to be able to cancel them in space_pressed.
        self.current_after_jobs = []

        # A list of the last 20 trials, 0 means unuccessful, 1 means successful
        self.success_list = []

        # The success frequency of the last 20 rounds
        self.success_frequency = None

        self.gui.set_background_color(BACKGROUND_COLOR)
        self.gui.display_pause_screen()

    def add_current_after_jobs(self, jobs):
        if type(jobs) is list:
            self.current_after_jobs.extend(jobs)
        else:
            self.current_after_jobs.extend([jobs])

    def cancel_all_after_jobs(self):
        for ind, job in enumerate(self.current_after_jobs):
            if job is not None:
                self.gui.root.after_cancel(job)
                self.current_after_jobs[ind] = None
        self.current_after_jobs = []

    def canvas_clicked(self, event, canvas_key):
        if canvas_key == '42':
            return self.next_clicked(event)
        else:
            return self._canvas_clicked(event, canvas_key)

    def next_clicked(self, event=None):
        if self.gui.next_displayed:
            self.gui.next_displayed = False
            self.started_trial_cnt += 1
            self.start_trial()

    def space_pressed(self, event=None):
        _play('space_bar_sound.wav')
        if self.gui.pause_screen_displayed:
            self.get_ready_to_start_trial()
            self.gui.pause_screen_displayed = False
        else:
            self.cancel_all_after_jobs()
            self.gui.display_pause_screen()

    def get_ready_to_start_trial(self):
        self.gui.blackout_displayed = False
        self.gui.snack_time = False
        if self.finished_trial_cnt >= config.TRIALS_BEFORE_PAUSE:
            self.gui.display_pause_screen()
            _play('space_bar_sound.wav')
            self.finished_trial_cnt = 0
        else:
            self.gui.clear()
            self.gui.display_next()

    def start_trial(self, event=None):
        pass
        # assert(False)  # Must be overridden

    def is_sub_experiment_done(self):
        return False

    def left_clicked(self, event=None):
        self.clicked_option = "left"
        return self._left_clicked(event)

    def right_clicked(self, event=None):
        self.clicked_option = "right"
        return self._right_clicked(event)

    def _left_clicked(self, event):
        assert(False)  # Must be overridden

    def _right_clicked(self, event):
        assert(False)  # Must be overridden

    def result_filename(self):
        """
        Return the file name of the result file.
        """
        experiment = self.exp_abbrev
        assert(experiment is not None)
        subject = config.SUBJECT_TAG.lower()
        date = datestamp()
        return subject + "_" + experiment + "_" + date + ".csv"

    def update_success_frequency(self, is_correct):
        if is_correct is None:  # For example for probe trials
            return
        self.success_list.append(int(is_correct))
        # if len(self.success_list) > 5:  # XXX
        if len(self.success_list) > 20:
            self.success_list.pop(0)
        # if len(self.success_list) >= 5:  # XXX
        if len(self.success_list) >= 20:
            first10 = self.success_list[0: 10]
            last10 = self.success_list[10: 20]
            success_first10 = sum(first10) / len(first10)
            success_last10 = sum(last10) / len(last10)
            min_success = min(success_first10, success_last10)
            self.success_frequency = round(min_success, 3)
            # self.success_frequency = round(sum(self.success_list) / len(self.success_list), 3)

    def correct_choice(self):
        self.gui.clear()
        play_correct()
        self.gui.snack_time = True
        job = self.gui.root.after(config.DELAY_AFTER_REWARD, self.get_ready_to_start_trial)
        self.add_current_after_jobs(job)

    def incorrect_choice(self):
        # self.cancel_all_after_jobs()
        self.gui.blackout()
        play_incorrect()
        job = self.gui.root.after(config.BLACKOUT_TIME, self.get_ready_to_start_trial)
        self.add_current_after_jobs(job)

    def write_to_file(self, event):
        self.finished_trial_cnt += 1

        toc = time.time()
        response_time = None
        if hasattr(self, "tic") and self.tic is not None:
            response_time = round(toc - self.tic, TIMETOL)

        file_data = list()
        if self.success_frequency is not None:
            self.update_success_frequency(self.is_correct)
            file_data.extend([("freq_correct", self.success_frequency)])
        else:
            file_data.extend([("freq_correct", "None")])

        if self.is_combination:
            file_data.extend([("sub_experiment_index", self.sub_experiment_index)])

        file_data.extend([("subject", config.SUBJECT_TAG),
                          ("experiment", self.exp_abbrev),
                          ("date", datestamp()),
                          ("timestamp", timestamp()),
                          ("trial", self.started_trial_cnt),
                          ("response", self.clicked_option)])

        if self.is_correct is not None:
            file_data.extend([("is_correct", self.is_correct)])
        else:
            file_data.extend([("is_correct", "None")])

        file_data.extend([("response_time", response_time)])

        # Add experiment specific data
        file_data.extend(self.get_file_data())

        file_data.extend([("BACKGROUND_COLOR", BACKGROUND_COLOR),
                          ("NEXT_BUTTON_COLOR", NEXT_BUTTON_COLOR),
                          ("BLACKOUT_COLOR", BLACKOUT_COLOR),
                          ("BLACKOUT_TIME", config.BLACKOUT_TIME),
                          ("DELAY_AFTER_REWARD", config.DELAY_AFTER_REWARD)])

        # # The coordinate of the click
        # x = y = "None"
        # if event is not None:
        #     x = event.x_root
        #     y = event.y_root
        # file_data.extend([("x", x), ("y", y)])

        # # The "undesired click" related data
        # file_data.extend([("undesired_touch", is_undesired)])

        # screen_touched = self.gui._screen_touched()
        # file_data.extend([("screen_touched", screen_touched)])

        # cell_touched = self.gui._cell_touched(x, y)
        # file_data.extend([("cell_touched", cell_touched)])

        # button_touched = self.gui.last_clicked_button_canvas
        # file_data.extend([("button_touched", button_touched)])
        # self.gui.last_clicked_button_canvas = "None"  # Reset for next click

        headers = list()
        values = list()
        for data in file_data:
            header, value = data
            if data is None:
                data = "None"
            headers.append(header)
            values.append(value)
        self.result_file.write(headers, values)


class StimulusWindow():
    def __init__(self, gui):
        self.gui = gui
        self.root = tk.Toplevel(gui.root)
        self.is_fullscreen = False
        self.is_pointer_visible = True
        self.image_files = gui.image_files
        self._make_widgets()

        self.set_background_color(BACKGROUND_COLOR)
        self.stimulus_displayed = False
        self.display_pause_screen()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen  # Just toggling the boolean
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def toggle_pointer_visibility(self, event=None):
        if self.is_pointer_visible:
            # Hide mouse pointer
            self.root.config(cursor='none')
        else:
            self.root.config(cursor='')
        self.is_pointer_visible = not self.is_pointer_visible

    def end_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
        return "break"

    def blackout(self, color=BLACKOUT_COLOR):
        self._set_entire_screen_color(color)

    def display_pause_screen(self):
        self._set_entire_screen_color(START_SCREEN_COLOR)
        self.pause_screen_displayed = True
        self.snack_time = False

    def set_background_color(self, color):
        # Root
        self.root.configure(background=color)
        # Frames
        self.bottom_frame.configure(background=color)
        # Canvases
        self.bottom_canvas.configure(background=color)

    def _set_entire_screen_color(self, color):
        self.clear_canvases()
        self.set_background_color(color)

    def display_stimulus(self, stimulus, shape_scale):
        pass
        # _display_shape(stimulus, self.bottom_canvas, shape_scale)
        # self.stimulus_displayed = True

    # def _display_image(self, symbol):
    #     canvas = self.bottom_canvas
    #     w = canvas.winfo_width()
    #     h = canvas.winfo_height()
    #     canvas.create_image(w / 2, h / 2, image=self.image_files[symbol], anchor=tk.CENTER)

    def _display_image(self, symbol, canvas):
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        canvas.create_image(w / 2, h / 2, image=self.image_files[symbol], anchor=tk.CENTER)

    def clear(self):
        self.set_background_color(BACKGROUND_COLOR)
        self.clear_canvases()

    def clear_canvases(self):
        self.bottom_canvas.delete(tk.ALL)
        self.stimulus_displayed = False

    def _make_widgets(self):
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

        self.root.bind("<F10>", self.toggle_pointer_visibility)

        H = self.root.winfo_screenheight() * TOL
        h = H * config.SCREEN2_STIMULUS_WIDTH
        self.bottom_frame = tk.Frame(self.root, width=h, height=h, **frame_options)
        self.bottom_canvas = tk.Canvas(self.bottom_frame, width=h, height=h * 0.99,
                                       **canvas_options)
        self.bottom_canvas.pack(expand=False, side=tk.BOTTOM)

        self.bottom_frame.pack_propagate(False)
        self.bottom_frame.pack(expand=False, side=tk.BOTTOM)

        if config.HIDE_MOUSE_POINTER:
            # Hide mouse pointer
            self.toggle_pointer_visibility()

        self.root.title("Stimulus Window")
        self.root.protocol("WM_DELETE_WINDOW", self.delete_window)

    def delete_window(self):
        exit(0)


BLUESQUARE = 'bluesquare'
YELLOWSQUARE = 'yellowsquare'
YELLOWCIRCLE = 'yellowcircle'
WHITECIRCLE = 'whitecircle'
BLUESTAR = 'bluestar'
WHITESTAR = 'whitestar'


class MatchingToSample(Experiment):
    def __init__(self, gui, is_combination=False, exp_abbrev=None):

        # super().__init__(gui, is_combination=is_combination)

        # Experiment abbreviation
        self.exp_abbrev = exp_abbrev

        super().__init__(gui, is_combination=is_combination)

        # The key for the canvas containing the correct option
        self.correct_canvas_key = None

        self.is_correct = None

        # The last displayed sample
        self.sample = None

        # To make sure that within 100 trials, each sample occurs five times
        self.SAMPLE_POT = list(self.gui.image_files.keys()) * 5

        self._create_new_samples()

        self.current_option_canvases = None

    def start_trial(self, event=None):
        self.gui.clear()
        self.display_sample()
        job = self.gui.root.after(config.SYMBOL_SHOW_TIME_MTS, self.display_options)
        self.add_current_after_jobs(job)

    def display_sample(self):
        self.sample = self.sample_pot.pop()
        if len(self.sample_pot) == 0:
            self._create_new_samples()
        self.gui._display_image(self.sample, self.gui.canvas['12'])
        if self.gui.use_screen2:
            # self.gui.stimulus_window.display_stimulus(self.sample, shape_scale=1)
            self.gui.stimulus_window._display_image(self.sample, self.gui.stimulus_window.bottom_canvas)
        self.stimulus_displayed = True

    def _create_new_samples(self):
        self.sample_pot = list(self.SAMPLE_POT)  # Make a copy
        random.shuffle(self.sample_pot)

    def display_options(self):
        self.gui.clear()
        pool = list(self.gui.image_files.keys())
        pool = [s for s in pool if s != self.sample]  # Exclude the correct sample
        options = [self.sample]  # The shown sample
        options.extend(list(random.sample(pool, 3)))  # Three other random symbols
        random.shuffle(options)

        # Pick four random canvases out of the six cells
        self.current_option_canvases = random.sample(['21', '22', '23', '31', '32', '33'], 4)

        self.canvas_option_dict = {key: option for key, option in zip(self.current_option_canvases, options)}
        found_sample = False
        for key, option in self.canvas_option_dict.items():
            self.gui._display_image(option, self.gui.canvas[key])
            if option == self.sample:
                assert(not found_sample)
                self.correct_canvas_key = key
                found_sample = True

        self.gui.options_displayed = True
        self.tic = time.time()

    def _canvas_clicked(self, event, canvas_key):
        if self.gui.options_displayed and (canvas_key in self.current_option_canvases):
            self.clicked_option = self.canvas_option_dict[canvas_key]
            self.is_correct = (canvas_key == self.correct_canvas_key)
            if self.is_correct:
                self.correct_choice()    
            else:
                self.incorrect_choice()
            self.gui.options_displayed = False
            self.write_to_file(event)
            return "break"

    def get_file_data(self):
        return [("SYMBOL_SHOW_TIME_MTS", config.SYMBOL_SHOW_TIME_MTS)]

    def is_sub_experiment_done(self):
        if self.success_frequency is None:
            return False
        else:
            return (self.success_frequency >= 0.8)


class MatchingToSampleWithProbes(MatchingToSample):
    PROBE_TYPE1 = [
        (("A", 500), ("B", 1000)),
        (("A", 1500), ("B", 1000)),
        (("A", 4500), ("B", 1000))
    ]
    PROBE_TYPE2 = [
        (("B", 500), ("A", 1000)),
        (("B", 1500), ("A", 1000)),
        (("B", 4500), ("A", 1000))
    ]
    PROBE_TYPE3 = [
        (("A", 500), ("B", 500)),
        (("A", 1000), ("B", 500)),
        (("A", 2000), ("B", 500))
    ]
    PROBE_TYPE4 = [
        (("B", 500), ("A", 500)),
        (("B", 1000), ("A", 500)),
        (("B", 2000), ("A", 500))
    ]
    PROBE_TYPES = PROBE_TYPE1 + PROBE_TYPE2 + PROBE_TYPE3 + PROBE_TYPE4

    def __init__(self, gui, is_combination=False, exp_abbrev=None):
        super().__init__(gui, is_combination)
        self.PROBE_TRIAL_INTERVAL = 2  # XXX Should be 10
        self.INTER_STIMULUS_TIME = 300
        self.sample_cnt = 0

        self.PROBE_POT = MatchingToSampleWithProbes.PROBE_TYPES

        self._create_new_probes()

        self.probe = None
        self.probe_stimulus1 = None
        self.probe_stimulus2 = None

    def start_trial(self, event=None):
        self.gui.clear()
        time_to_options = self.display_sample()
        job = self.gui.root.after(time_to_options, self.display_options)
        self.add_current_after_jobs(job)

    def _display_probe(self, probe):
        self.gui.clear()
        canvas1 = self.gui.canvas['12']
        canvas2 = None
        if self.gui.use_screen2:
            canvas2 = self.gui.stimulus_window.bottom_canvas
        stimulus1, time1 = probe[0]
        stimulus2, time2 = probe[1]

        self.probe_stimulus1, self.probe_stimulus2 = random.sample(list(self.gui.image_files.keys()), 2)
        self.gui._display_image(self.probe_stimulus1, canvas1)
        if self.gui.use_screen2:
            self.gui.stimulus_window._display_image(self.probe_stimulus1, canvas2)

        job1 = self.gui.root.after(time1, self.gui.clear)
        job2 = self.gui.root.after(time1 + self.INTER_STIMULUS_TIME, self.gui._display_image, self.probe_stimulus2, canvas1)
        job2_2 = None
        if self.gui.use_screen2:
            job2_2 = self.gui.root.after(time1 + self.INTER_STIMULUS_TIME, self.gui._display_image, self.probe_stimulus2, canvas2)
        job3 = self.gui.root.after(time1 + self.INTER_STIMULUS_TIME + time2, self.gui.clear)
        self.add_current_after_jobs([job1, job2, job2_2, job3])
        return time1 + self.INTER_STIMULUS_TIME + time2

    def display_sample(self):
        self.sample_cnt += 1
        is_probe_trial = (self.sample_cnt % self.PROBE_TRIAL_INTERVAL == 0)
        if is_probe_trial:
            self.probe = self.probe_pot.pop()
            self.sample = None
            if len(self.probe_pot) == 0:
                self._create_new_probes()
            return self._display_probe(self.probe)

        else:
            self.probe = None
            super().display_sample()
            return config.SYMBOL_SHOW_TIME_MTS

    def display_options(self):
        self.gui.clear()
        if self.probe is not None:
            self.gui.clear()
            all_images = list(self.gui.image_files.keys())
            pool = [s for s in all_images if s != self.probe_stimulus1 and s != self.probe_stimulus2]  # Exclude the probe stimuli
            options = [self.probe_stimulus1, self.probe_stimulus2]  # The probe stimuli
            options.extend(list(random.sample(pool, 2)))  # Two other random symbols
            random.shuffle(options)

            # Pick four random canvases out of the six cells
            self.current_option_canvases = random.sample(['21', '22', '23', '31', '32', '33'], 4)

            self.canvas_option_dict = {key: option for key, option in zip(self.current_option_canvases, options)}
            for key, option in self.canvas_option_dict.items():
                self.gui._display_image(option, self.gui.canvas[key])

            self.gui.options_displayed = True
            self.tic = time.time()
        else:
            super().display_options()



 
            
            

    def _canvas_clicked(self, event, canvas_key):
        if self.probe is not None:
            if self.gui.options_displayed and (canvas_key in self.current_option_canvases):
                self.clicked_option = self.canvas_option_dict[canvas_key]
                self.is_correct = None
                self.write_to_file(event=event)
                self.gui.options_displayed = False
                self.gui.clear()
                self.get_ready_to_start_trial()
                self.gui.options_displayed = False
                self.write_to_file(event)
                return "break"
        else:
            return super()._canvas_clicked(event, canvas_key)
        # if canvas_key in ('21', '22', '23', '31', '32', '33'):
        #     if self.gui.options_displayed:
        #         self.clicked_option = self.canvas_option_dict[canvas_key]
        #         self.is_correct = (canv
        # as_key == self.correct_canvas_key)
        #         if self.is_correct:
        #             self.correct_choice()    
        #         else:
        #             self.incorrect_choice()
        #     self.gui.options_displayed = False
        #     self.write_to_file(event)
        #     return "break"

    def _create_new_probes(self):
        self.probe_pot = list(self.PROBE_POT)  # Make a copy
        random.shuffle(self.probe_pot)


class SubExperiment1(MatchingToSample):
    def __init__(self, gui):
        super().__init__(gui, is_combination=True, exp_abbrev="pretraining")
        self.sub_experiment_index = 1

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment2(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()

    def result_filename(self):
        return Combination1.result_filename()


class SubExperiment2(MatchingToSampleWithProbes):
    def __init__(self, gui):
        super().__init__(gui, is_combination=True, exp_abbrev="probes")
        self.sub_experiment_index = 2

        self.end_of_combination_sound_played = False

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            self.gui.display_pause_screen()

            if not self.end_of_combination_sound_played:
                self.gui.root.after(3000, _play, 'end_of_combination.wav')
            self.end_of_combination_sound_played = True
        else:
            super().get_ready_to_start_trial()

    def result_filename(self):
        return Combination1.result_filename()


class Combination1():
    def __init__(self, gui):
        self.gui = gui
        filename = self.result_filename()
        self.result_file = ResultFile(filename)

        sub_experiment_index = self.result_file.get_last_value('sub_experiment_index')
        if sub_experiment_index is None:
            sub_experiment_index = 1
        else:
            sub_experiment_index = int(sub_experiment_index)

        if sub_experiment_index == 1:
            SubExperiment1(gui)
        elif sub_experiment_index == 2:
            SubExperiment2(gui)
        else:
            raise Exception(f"Unknown sub experiment index {sub_experiment_index}.")

    @staticmethod
    def result_filename():
        experiment = Combination1._experiment_abbreviation()
        subject = config.SUBJECT_TAG.lower()
        return subject + "_" + experiment + ".csv"

    @staticmethod
    def _experiment_abbreviation():
        return "Combination1"


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

    def get_last_value(self, column_title):
        return ResultFile.get_last_value_static(self.path_and_file, column_title)

    @staticmethod
    def get_last_value_static(path_and_file, column_title):
        if ResultFile.is_empty_or_does_not_exist(path_and_file):
            return None
        else:
            file = open(path_and_file)
            is_title = True
            titles = None
            data = None
            with file as csvfile:
                reader = csv.reader(csvfile)
                for r in reader:
                    if is_title:
                        titles = r
                        is_title = False
                    else:
                        data = r
            if titles is not None:
                try:
                    title_ind = titles.index(column_title)
                except ValueError:
                    return None
                return data[title_ind]
            else:
                return None

    @staticmethod
    def is_empty_or_does_not_exist(path_and_file):
        if os.path.exists(path_and_file):
            return (os.path.getsize(path_and_file) == 0)
        else:
            return True


def _display_shape(symbol, canvas, shape_scale, square_fraction=1, force_mid=False):
    w = canvas.winfo_width()
    L = w * shape_scale
    if force_mid:
        square_args = [(w - L) / 2, (w - L) / 2, (w - L) / 2 + L, (w - L) / 2 + L]
    else:
        # if square_fraction <= 1:
        square_args = [(w - L) / 2, 0, (w - L) / 2 + L, L * square_fraction]
        # else:
        #     square_args = [(w - L) / 2, (w - L) / 2, (w - L) / 2 + L, (w - L) / 2 + L]
    if symbol == 'bluesquare':
        canvas.create_rectangle(*square_args, fill='blue', outline="", tags="shape")
    elif symbol == 'yellowsquare':
        canvas.create_rectangle(*square_args, fill='yellow', outline="", tags="shape")
    else:
        raise Exception("Unknown symbol {}".format(symbol))


def play_correct():
    _play('correct.wav')


def play_incorrect():
    _play('incorrect.wav')


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
    gui = Gui()
    e = None
    if config.EXPERIMENT == config.DMTS_PROBE:
        e = Combination1(gui)
    else:
        print("Error: Undefined experiment name '" + config.EXPERIMENT + "'.")
    if e is not None:
        e.gui.root.mainloop()
