import tkinter as tk
import random
import subprocess
import config
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
COLOR_A = hex_format % config.COLOR_A_RGB
COLOR_B = hex_format % config.COLOR_B_RGB

frame_options = dict()  # For debugging frame positioning
# frame_options = {'highlightbackground': 'blue',
#                  'highlightcolor': 'blue',
#                  'highlightthickness': 1,
#                  'bd': 0}

canvas_options = {'bd': 0, 'highlightthickness': 0}
# canvas_options = {'bd': 1, 'highlightthickness': 1}

TOL = 0.99
TIMETOL = 3  # Round delay times to nearest millisecond


class Gui():
    def __init__(self, use_screen2=False):
        self.use_screen2 = use_screen2
        self._make_widgets()
        self._make_images()

        self.next_displayed = False
        self.stimulus_displayed = False
        self.blackout_displayed = False
        self.pause_screen_displayed = False
        self.snack_time = False

        self.last_clicked_button_canvas = "None"

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
                            'vertical_button.gif': PhotoImage(file='vertical_button.gif')}
        self.root.update()
        for key, image_file in self.image_files.items():
            scaling_factor = ceil(image_file.width() / self.left_canvas.winfo_width())
            self.image_files[key] = image_file.subsample(scaling_factor)

    def _make_widgets(self):

        # For dual screen setup, self.root.winfo_screenwidth() returns the sum of the two screen
        # widths. This is to get only one screen (the screen where the window is launched)
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
        h = H / 3

        # print(f"self.root.winfo_screenwidth()={self.root.winfo_screenwidth()}")
        # print(f"self.root.winfo_screenheight()={self.root.winfo_screenheight()}")

        self.canvas_width = h

        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

        self.is_pointer_visible = True
        self.root.bind("<F10>", self.toggle_pointer_visibility)

        # TOP
        self.top_frame = tk.Frame(self.root, width=W, height=h, **frame_options)

        self.top_left_canvas = tk.Canvas(self.top_frame, width=self.canvas_width,
                                         height=self.canvas_width, **canvas_options)
        self.top_mid_canvas = tk.Canvas(self.top_frame, width=self.canvas_width,
                                        height=self.canvas_width, **canvas_options)
        self.top_right_canvas = tk.Canvas(self.top_frame, width=self.canvas_width,
                                          height=self.canvas_width, **canvas_options)
        self.top_left_canvas.pack(side=tk.LEFT)
        self.top_mid_canvas.place(relx=.5, rely=.5, anchor="center")
        self.top_right_canvas.pack(side=tk.RIGHT)

        self.top_frame.pack_propagate(False)
        self.top_frame.pack(expand=True, side=tk.TOP)

        # MIDDLE
        space_width = h
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

        self.left_canvas = tk.Canvas(self.middle_left_frame, width=self.canvas_width,
                                     height=self.canvas_width, **canvas_options)
        self.left_canvas.pack(side=tk.RIGHT)

        self.right_canvas = tk.Canvas(self.middle_right_frame, width=self.canvas_width,
                                      height=self.canvas_width, **canvas_options)
        self.right_canvas.pack(side=tk.LEFT)

        self.middle_frame.pack_propagate(False)
        self.middle_frame.pack(expand=True, side=tk.TOP)

        # BOTTOM
        self.bottom_canvas_width = h * config.NEXT_BUTTON_WIDTH
        self.bottom_frame = tk.Frame(self.root, width=W, height=h, **frame_options)
        self.bottom_canvas = tk.Canvas(self.bottom_frame, width=self.bottom_canvas_width,
                                       height=self.bottom_canvas_width, **canvas_options)
        self.bottom_left_canvas = tk.Canvas(self.bottom_frame, width=self.canvas_width,
                                            height=self.canvas_width, **canvas_options)
        self.bottom_right_canvas = tk.Canvas(self.bottom_frame, width=self.canvas_width,
                                             height=self.canvas_width, **canvas_options)
        self.bottom_left_canvas.pack(side=tk.LEFT)
        self.bottom_right_canvas.pack(side=tk.RIGHT)
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

        if config.HIDE_MOUSE_POINTER:
            # Hide mouse pointer
            self.toggle_pointer_visibility()
            # self.root.config(cursor="none")

        self.root.title("Main Window")
        self.root.protocol("WM_DELETE_WINDOW", self.delete_window)

        self.stimulus_window = None
        if self.use_screen2:
            self.stimulus_window = StimulusWindow(self)

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
        self.bottom_left_canvas.configure(background=color)
        self.bottom_right_canvas.configure(background=color)
        self.top_left_canvas.configure(background=color)
        self.top_mid_canvas.configure(background=color)
        self.top_right_canvas.configure(background=color)

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
        self.left_canvas.delete(tk.ALL)
        self.right_canvas.delete(tk.ALL)
        self.bottom_canvas.delete(tk.ALL)
        self.top_left_canvas.delete(tk.ALL)
        self.top_mid_canvas.delete(tk.ALL)
        self.top_right_canvas.delete(tk.ALL)
        self.bottom_left_canvas.delete(tk.ALL)
        self.bottom_right_canvas.delete(tk.ALL)
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
        self.bottom_canvas.create_polygon(*self.next_symbol_args, fill=NEXT_BUTTON_COLOR,
                                          outline='', width=0)
        self.next_displayed = True

    def display_stimulus(self, stimulus, shape_scale, fraction=1):
        _display_shape(stimulus, self.top_mid_canvas, shape_scale, fraction)
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

    def _screen_touched(self):
        if self.pause_screen_displayed:
            return "PS"  # Pause/Pink screen
        elif self.next_displayed:
            return "NBS"  # Next button screen
        elif self.blackout_displayed:
            return "BS"  # Blackout screen
        elif self.options_displayed:
            return "RS"  # Response screen
        elif self.snack_time:
            return "ST"  # Snack time
        elif self.stimulus_displayed:
            return "SS"  # Stimulus screen
        else:
            return "None"

    def _cell_touched(self, x, y):
        w = self.screen_width
        h = self.screen_height
        if x <= w / 3:
            horiz = 'L'
        elif x <= 2 * w / 3:
            horiz = 'M'
        else:
            horiz = 'R'

        if y <= h / 3:
            vert = 'T'
        elif y <= 2 * h / 3:
            vert = 'M'
        else:
            vert = 'B'
        return horiz + vert


class Experiment():
    def __init__(self, gui, is_combination=False):

        self.gui = gui

        self.gui.root.bind("<Button-1>", self.undesired_click)
        self.gui.left_canvas.bind("<Button-1>", self.left_clicked)
        self.gui.right_canvas.bind("<Button-1>", self.right_clicked)
        self.gui.bottom_canvas.bind("<Button-1>", self.next_clicked)
        self.gui.top_mid_canvas.bind("<Button-1>", self.stimulus_clicked)
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
        self.success_frequency = 0

        self.gui.set_background_color(BACKGROUND_COLOR)
        self.gui.display_pause_screen()

    def next_clicked(self, event=None):
        self.gui.last_clicked_button_canvas = "NB"
        if self.gui.next_displayed:
            self.gui.next_displayed = False
            self.started_trial_cnt += 1
            self.start_trial()
            return "break"  # To detect "undesired clicks" outside any button

    def space_pressed(self, event=None):
        if self.gui.pause_screen_displayed:
            self.get_ready_to_start_trial()
            self.gui.pause_screen_displayed = False
        else:
            self.gui.display_pause_screen()
            self.cancel_all_after_jobs()
        _play('space_bar_sound.wav')

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

    def cancel_all_after_jobs(self):
        for ind, job in enumerate(self.current_after_jobs):
            self.gui.root.after_cancel(job)
            self.current_after_jobs[ind] = None
        self.current_after_jobs = []

    def start_trial(self, event=None):
        pass
        # assert(False)  # Must be overridden

    def is_sub_experiment_done(self):
        return False

    def stimulus_clicked(self, event=None):
        self.gui.last_clicked_button_canvas = "S"

    def left_clicked(self, event=None):
        self.gui.last_clicked_button_canvas = "R1"
        self.gui.clicked_option = "left"
        return self._left_clicked(event)

    def right_clicked(self, event=None):
        self.gui.last_clicked_button_canvas = "R2"
        self.gui.clicked_option = "right"
        return self._right_clicked(event)

    def _left_clicked(self, event):
        assert(False)  # Must be overridden

    def _right_clicked(self, event):
        assert(False)  # Must be overridden

    def result_filename(self):
        """
        Return the file name of the result file.
        """
        if self.is_combination:
            return Combination2.result_filename()
        else:
            experiment = self.experiment_abbreviation()
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
            self.success_frequency = round(sum(self.success_list) / len(self.success_list), 3)

    def experiment_abbreviation(self):
        assert(False)  # Must be overloaded

    def correct_choice(self):
        self.gui.clear()
        play_correct()
        self.gui.snack_time = True
        job = self.gui.root.after(config.DELAY_AFTER_REWARD, self.get_ready_to_start_trial)
        self.current_after_jobs = [job]

    def incorrect_choice(self):
        # self.cancel_all_after_jobs()
        self.gui.blackout()
        play_incorrect()
        job = self.gui.root.after(config.BLACKOUT_TIME, self.get_ready_to_start_trial)
        self.current_after_jobs = [job]

    def undesired_click(self, event=None):
        # self.cancel_all_after_jobs()
        # self.blackout(UNDESIRED_CLICK_BLACKOUT_COLOR)
        # job = self.root.after(config.UNDESIRED_CLICK_BLACKOUT_TIME, self.get_ready_to_start_trial)
        # self.current_after_jobs = [job]
        self.write_to_file(event=event, is_undesired=True)

    def write_to_file(self, event, is_undesired=False):
        if not is_undesired:
            self.finished_trial_cnt += 1

        stimulus_acronym = self.get_stimulus_acronym()

        toc = time.time()
        response_time = None
        if hasattr(self, "tic") and self.tic is not None:
            response_time = round(toc - self.tic, TIMETOL)

        file_data = list()
        if is_undesired:
            file_data.extend([("freq_correct", self.success_frequency)])
        elif self.success_frequency is not None:
            self.update_success_frequency(self.is_correct)
            file_data.extend([("freq_correct", self.success_frequency)])
        else:
            file_data.extend([("freq_correct", "None")])

        if self.is_combination:
            file_data.extend([("sub_experiment_index", self.sub_experiment_index)])

        file_data.extend([("subject", config.SUBJECT_TAG),
                          ("experiment", self.experiment_abbreviation()),
                          ("date", datestamp()),
                          ("timestamp", timestamp()),
                          ("trial", self.started_trial_cnt),
                          ("stimulus", stimulus_acronym),
                          ("response", self.clicked_option)])

        if self.success_frequency is not None and not is_undesired:
            file_data.extend([("is_correct", self.is_correct)])
        else:
            file_data.extend([("is_correct", "None")])

        file_data.extend([("response_time", response_time)])

        # Add experiment specific data
        file_data.extend(self.get_file_data())

        file_data.extend([("COLOR_A", COLOR_A),
                          ("COLOR_B", COLOR_B),
                          ("SYMBOL_WIDTH", config.SYMBOL_WIDTH),
                          ("BACKGROUND_COLOR", BACKGROUND_COLOR),
                          ("NEXT_BUTTON_COLOR", NEXT_BUTTON_COLOR),
                          ("BLACKOUT_COLOR", BLACKOUT_COLOR),
                          ("NEXT_BUTTON_WIDTH", config.NEXT_BUTTON_WIDTH),
                          ("BLACKOUT_TIME", config.BLACKOUT_TIME),
                          ("DELAY_AFTER_REWARD", config.DELAY_AFTER_REWARD)])

        # The coordinate of the click
        x = y = "None"
        if event is not None:
            x = event.x_root
            y = event.y_root
        file_data.extend([("x", x), ("y", y)])

        # The "undesired click" related data
        file_data.extend([("undesired_touch", is_undesired)])

        screen_touched = self.gui._screen_touched()
        file_data.extend([("screen_touched", screen_touched)])

        cell_touched = self.gui._cell_touched(x, y)
        file_data.extend([("cell_touched", cell_touched)])

        button_touched = self.gui.last_clicked_button_canvas
        file_data.extend([("button_touched", button_touched)])
        self.gui.last_clicked_button_canvas = "None"  # Reset for next click

        headers = list()
        values = list()
        for data in file_data:
            header, value = data
            if data is None:
                data = "None"
            headers.append(header)
            values.append(value)
        self.result_file.write(headers, values)

    def get_stimulus_acronym(self):
        stimulus_acronym = "None"
        if hasattr(self, "stimulus") and self.stimulus is not None:
            if self.stimulus == COLOR_A:
                stimulus_acronym = "A"
            elif self.stimulus == COLOR_B:
                stimulus_acronym = "B"
            elif self.stimulus == SequenceDiscriminationProbe.LONG_AB:
                stimulus_acronym = "AB"
            elif self.stimulus == SequenceDiscriminationProbe.SHORT_AB:
                stimulus_acronym = "aB"
            else:
                assert(False)
            return stimulus_acronym
        else:
            return None


class StimulusWindow():
    def __init__(self, gui):
        self.gui = gui
        self.root = tk.Toplevel(gui.root)
        self.is_fullscreen = False
        self.is_pointer_visible = True
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
        _display_shape(stimulus, self.bottom_canvas, shape_scale)
        self.stimulus_displayed = True

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


class MatchingToSample(Experiment):
    def __init__(self, gui, is_combination=False, responses_are_samples=False,
                 use_screen1=True, stimulus_fraction_screen1=1, white_circle=False,
                 white_star=False):
        # If true, the response buttons are the same as the samples
        # If false, the response buttons are the symbols in self.display_options
        self.responses_are_samples = responses_are_samples

        # Display samples on screen 1
        self.use_screen1 = use_screen1

        # The fraction of the stimulus to display on screen 1
        self.stimulus_fraction_screen1 = stimulus_fraction_screen1

        # If true, use white circle instead of the same color as the sample
        self.white_circle = white_circle

        # If true, use white star instead of the same color as the sample
        self.white_star = white_star

        super().__init__(gui, is_combination=is_combination)

        self.is_correct = None

        # The last displayed sample
        self.sample = None

        self.YELLOWSQUARE = 'yellowsquare'
        self.BLUESQUARE = 'bluesquare'

        self.POT10 = [self.YELLOWSQUARE, self.BLUESQUARE] * 5

        self._create_new_samples()

    def _create_new_samples(self):
        self.sample_pot = list(self.POT10)  # Make a copy
        random.shuffle(self.sample_pot)

    def display_options(self):
        if config.YELLOW_POS == 'left':
            self.left_is_correct = (self.sample == self.YELLOWSQUARE)
        else:
            self.left_is_correct = (self.sample != self.YELLOWSQUARE)
        if self.responses_are_samples:
            if config.YELLOW_POS == 'left':
                _display_shape(self.YELLOWSQUARE, self.gui.left_canvas,
                               shape_scale=config.SYMBOL_WIDTH)
                _display_shape(self.BLUESQUARE, self.gui.right_canvas,
                               shape_scale=config.SYMBOL_WIDTH)
            else:
                _display_shape(self.BLUESQUARE, self.gui.left_canvas,
                               shape_scale=config.SYMBOL_WIDTH)
                _display_shape(self.YELLOWSQUARE, self.gui.right_canvas,
                               shape_scale=config.SYMBOL_WIDTH)
        else:
            if config.YELLOW_POS == 'left':
                if self.white_circle:
                    self.gui._display_image("white_circle.gif", self.gui.left_canvas)
                else:
                    self.gui._display_image("yellow_circle.gif", self.gui.left_canvas)
                if self.white_star:
                    self.gui._display_image("white_star.gif", self.gui.right_canvas)
                else:
                    self.gui._display_image("blue_star.gif", self.gui.right_canvas)
            else:
                if self.white_star:
                    self.gui._display_image("white_star.gif", self.gui.left_canvas)
                else:
                    self.gui._display_image("blue_star.gif", self.gui.left_canvas)
                if self.white_circle:
                    self.gui._display_image("white_circle.gif", self.gui.right_canvas)
                else:
                    self.gui._display_image("yellow_circle.gif", self.gui.right_canvas)
        self.gui.options_displayed = True
        self.tic = time.time()

    def _left_clicked(self, event=None):
        if self.gui.options_displayed:
            self.is_correct = self.left_is_correct
            return self._option_clicked(event)

    def _right_clicked(self, event=None):
        if self.gui.options_displayed:
            self.is_correct = not self.left_is_correct
            return self._option_clicked(event)

    def _option_clicked(self, event):
        if self.is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.gui.options_displayed = False
        self.write_to_file(event)
        return "break"

    def start_trial(self, event=None):
        self.gui.clear()
        self.display_random_symbol()
        job = self.gui.root.after(config.SYMBOL_SHOW_TIME_MTS, self.display_options)
        self.current_after_jobs = [job]

    def display_random_symbol(self):
        self.sample = self.sample_pot.pop()
        if len(self.sample_pot) == 0:
            self._create_new_samples()
        if self.use_screen1:
            self.gui.display_stimulus(self.sample, shape_scale=config.SYMBOL_WIDTH,
                                      fraction=self.stimulus_fraction_screen1)
        if self.gui.use_screen2:
            self.gui.stimulus_window.display_stimulus(self.sample, shape_scale=1)
        self.stimulus_displayed = True

    def get_file_data(self):
        if self.is_combination:
            return [("YELLOW_POS", config.YELLOW_POS),
                    ("SYMBOL_SHOW_TIME_MTS", config.SYMBOL_SHOW_TIME_MTS),
                    ("STIMULUS_TIME", config.STIMULUS_TIME),
                    ("DELAY", config.DELAY)]
        else:
            return [("YELLOW_POS", config.YELLOW_POS),
                    ("SYMBOL_SHOW_TIME_MTS", config.SYMBOL_SHOW_TIME_MTS)]

    def get_stimulus_acronym(self):
        return self.sample

    def is_sub_experiment_done(self):
        return (self.success_frequency >= 0.8)

    def experiment_abbreviation(self):
        if self.responses_are_samples:
            if self.white_circle and self.white_star:
                return config.MATCHING_TO_SAMPLE_SAMPLE_BOTHWHITE
            elif (not self.white_circle) and self.white_star:
                return config.MATCHING_TO_SAMPLE_SAMPLE_STARWHITE
            else:
                return config.MATCHING_TO_SAMPLE_SAMPLE
        else:
            return config.MATCHING_TO_SAMPLE_SYMBOLS


class SingleStimulusDiscrimination(Experiment):
    def __init__(self, gui, is_combination=False, use_screen1=True, delay=None):
        # Display stimuli on screen 1
        self.use_screen1 = use_screen1

        if delay is None:
            self.delay = config.DELAY
        else:
            self.delay = delay

        super().__init__(gui, is_combination=is_combination)

        self.is_correct = None

        # The last displayed stimulus
        self.stimulus = None

        self.YELLOWSQUARE = 'yellowsquare'
        self.BLUESQUARE = 'bluesquare'

        self.POT10 = [self.YELLOWSQUARE, self.BLUESQUARE] * 5

        self._create_new_stimuli()

    def _create_new_stimuli(self):
        self.stimulus_pot = list(self.POT10)  # Make a copy
        random.shuffle(self.stimulus_pot)

    def display_options(self):
        if config.YELLOW_POS == 'left':
            self.left_is_correct = (self.stimulus == self.YELLOWSQUARE)
        else:
            self.left_is_correct = (self.stimulus != self.YELLOWSQUARE)
        if config.YELLOW_POS == 'left':
            self.gui._display_image("white_circle.gif", self.gui.left_canvas)
            self.gui._display_image("white_star.gif", self.gui.right_canvas)
        else:
            self.gui._display_image("white_star.gif", self.gui.left_canvas)
            self.gui._display_image("white_circle.gif", self.gui.right_canvas)
        self.gui.options_displayed = True
        self.tic = time.time()

    def _left_clicked(self, event=None):
        if self.gui.options_displayed:
            self.is_correct = self.left_is_correct
            return self._option_clicked(event)

    def _right_clicked(self, event=None):
        if self.gui.options_displayed:
            self.is_correct = not self.left_is_correct
            return self._option_clicked(event)

    def _option_clicked(self, event):
        if self.is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.gui.options_displayed = False
        self.write_to_file(event)
        return "break"

    def start_trial(self, event=None):
        self.gui.clear()
        self.display_random_symbol()
        job1 = self.gui.root.after(config.STIMULUS_TIME, self.gui.clear)
        job2 = self.gui.root.after(config.STIMULUS_TIME + self.delay, self.display_options)
        self.current_after_jobs = [job1, job2]

    def display_random_symbol(self):
        self.stimulus = self.stimulus_pot.pop()
        if len(self.stimulus_pot) == 0:
            self._create_new_stimuli()
        if self.use_screen1:
            _display_shape(self.stimulus, self.top_mid_canvas,
                           shape_scale=config.SYMBOL_WIDTH)
        if self.gui.use_screen2:
            _display_shape(self.stimulus, self.gui.stimulus_window.bottom_canvas,
                           shape_scale=1)  # The canvas itself has the correct size
        self.stimulus_displayed = True

    def get_file_data(self):
        if self.is_combination:
            return [("YELLOW_POS", config.YELLOW_POS),
                    ("SYMBOL_SHOW_TIME_MTS", config.SYMBOL_SHOW_TIME_MTS),
                    ("STIMULUS_TIME", config.STIMULUS_TIME),
                    ("DELAY", self.delay)]
        else:
            return [("STIMULUS_TIME", config.STIMULUS_TIME),
                    ("DELAY", self.delay)]

    def get_stimulus_acronym(self):
        return self.stimulus

    def is_sub_experiment_done(self):
        return (self.success_frequency >= 0.8)

    def experiment_abbreviation(self):
        return config.SINGLE_STIMULUS_DISCRIMINATION

# ---------------------------------------------------------------------------


class SequenceDiscriminationProbe(Experiment):
    SHORT_AB = "shortAB"
    LONG_AB = "longAB"

    def __init__(self, gui):
        super().__init__(gui)
        self.options_displayed = False
        self.is_correct = True  # Initialize to True so that first sequence is taken from pot
        self.stimulus_cnt = 0
        self.POT8 = [COLOR_A, COLOR_B] * 4
        self.PROBE_POT10 = [SequenceDiscriminationProbe.SHORT_AB, SequenceDiscriminationProbe.LONG_AB] * 5
        self._create_new_stimuli()
        self._create_new_probes()

    def _create_new_stimuli(self):
        self.stimuli_pot = list(self.POT8)  # Make a copy
        random.shuffle(self.stimuli_pot)

    def _create_new_probes(self):
        self.probe_pot = list(self.PROBE_POT10)  # Make a copy
        random.shuffle(self.probe_pot)

    def start_trial(self, event=None):
        self.clear()
        time_to_options = self.display_random_stimulus()
        job = self.root.after(time_to_options, self.display_options)
        self.current_after_jobs.append(job)

    def display_random_stimulus(self):
        self.stimulus_cnt += 1
        is_probe_trial = (self.stimulus_cnt % config.PROBE_TRIAL_INTERVAL == 0)
        if is_probe_trial:
            self.stimulus = self.probe_pot.pop()
            if len(self.probe_pot) == 0:
                self._create_new_probes()
        else:
            self.stimulus = self.stimuli_pot.pop()
            if len(self.stimuli_pot) == 0:
                self._create_new_stimuli()

        self.is_seq = False
        if self.stimulus in (COLOR_A, COLOR_B):
            self._set_entire_screen_color(self.stimulus)
            job = self.root.after(config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS, self.clear)
            self.current_after_jobs = [job]
            time_to_options = config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS
        else:
            self.is_seq = True
            if self.stimulus == SequenceDiscriminationProbe.SHORT_AB:
                A_time = config.SHORT_A_TIME
            else:
                A_time = config.LONG_A_TIME
            self._set_entire_screen_color(COLOR_A)
            job1 = self.root.after(A_time, self.clear)
            job2 = self.root.after(A_time + config.INTER_STIMULUS_TIME,
                                   self._set_entire_screen_color, COLOR_B)
            job3 = self.root.after(A_time + config.B_TIME, self.clear)
            self.current_after_jobs = [job1, job2, job3]
            time_to_options = A_time + config.B_TIME

        self.is_A = (self.stimulus == COLOR_A)
        return time_to_options

    def display_options(self):
        self.clear()
        self._display_image(config.LEFT_OPTION, self.bottom_left_canvas)
        self._display_image(config.RIGHT_OPTION, self.top_right_canvas)
        self.options_displayed = True
        self.tic = time.time()

    def _left_clicked(self, event=None):
        if self.options_displayed:
            if self.is_seq:
                self._option_chosen_after_seq(event)
            else:
                self.is_correct = self.is_A
                self._option_chosen(event)
            return "break"

    def _right_clicked(self, event=None):
        if self.options_displayed:
            if self.is_seq:
                self._option_chosen_after_seq(event)
            else:
                self.is_correct = not self.is_A
                self._option_chosen(event)
            return "break"

    def _option_chosen_after_seq(self, event):
        self.is_correct = None
        self.write_to_file(event=event)
        self.options_displayed = False
        self.clear()
        self.get_ready_to_start_trial()

    def _option_chosen(self, event):
        if self.is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.write_to_file(event=event)
        self.options_displayed = False

    def get_file_data(self):
        return [("STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS", config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS),
                ("LONG_A_TIME", config.LONG_A_TIME),
                ("SHORT_A_TIME", config.SHORT_A_TIME),
                ("B_TIME", config.B_TIME)]

    def experiment_abbreviation(self):
        return config.SEQUENCE_DISCRIMINATION_PROBE

# ---------------------------------------------------------------------------


class SubExperiment3a(MatchingToSample):
    def __init__(self, gui):
        super().__init__(gui, is_combination=True)
        self.gui = gui
        self.sub_experiment_index = 31
        self.stimulus_fraction_screen1 = 1

        self.responses_are_samples = False
        self.use_screen1 = True

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment3b(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()


class SubExperiment3b(MatchingToSample):
    def __init__(self, gui):
        super().__init__(gui, is_combination=True)
        self.gui = gui
        self.sub_experiment_index = 32
        self.stimulus_fraction_screen1 = 0.5

        self.responses_are_samples = False
        self.use_screen1 = True

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment3c(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()


class SubExperiment3c(MatchingToSample):
    def __init__(self, gui):
        super().__init__(gui, is_combination=True)
        self.gui = gui
        self.sub_experiment_index = 33
        self.stimulus_fraction_screen1 = 0.25

        self.responses_are_samples = False
        self.use_screen1 = True

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment4(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()


class SubExperiment4(MatchingToSample):
    def __init__(self, gui):
        super().__init__(gui, is_combination=True)
        self.gui = gui
        self.sub_experiment_index = 4

        self.responses_are_samples = False
        self.use_screen1 = False

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment5(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()


class SubExperiment5(MatchingToSample):
    def __init__(self, gui):
        super().__init__(gui, is_combination=True)
        self.gui = gui
        self.sub_experiment_index = 5

        self.responses_are_samples = False
        self.use_screen1 = False
        self.white_circle = False
        self.white_star = True

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment6(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()


class SubExperiment6(MatchingToSample):
    def __init__(self, gui):
        super().__init__(gui, is_combination=True)
        self.gui = gui
        self.sub_experiment_index = 6

        self.responses_are_samples = False
        self.use_screen1 = False
        self.white_circle = True
        self.white_star = True

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment7(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()


class SubExperiment7(SingleStimulusDiscrimination):
    def __init__(self, gui):
        super().__init__(gui, is_combination=True)
        self.gui = gui
        self.sub_experiment_index = 7

        self.responses_are_samples = False
        self.use_screen1 = False
        self.delay = 0

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment8(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()


class SubExperiment8(SingleStimulusDiscrimination):
    def __init__(self, gui):
        super().__init__(gui, is_combination=True)
        self.gui = gui
        self.sub_experiment_index = 8

        self.responses_are_samples = False
        self.use_screen1 = False
        self.delay = 500

        self.end_of_combination_sound_played = False

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            self.gui.display_pause_screen()
            if not self.end_of_combination_sound_played:
                self.gui.root.after(5000, _play, 'end_of_combination.wav')
            self.end_of_combination_sound_played = True
        else:
            super().get_ready_to_start_trial()


class Combination2():
    def __init__(self, gui):
        self.gui = gui
        filename = self.result_filename()
        self.result_file = ResultFile(filename)

        sub_experiment_index = self.result_file.get_last_value('sub_experiment_index')
        if sub_experiment_index is None:
            sub_experiment_index = 1
        else:
            sub_experiment_index = int(sub_experiment_index)

        if sub_experiment_index <= 3:
            SubExperiment3a(gui)
        elif sub_experiment_index == 4:
            SubExperiment4(gui)
        elif sub_experiment_index == 5:
            SubExperiment5(gui)
        elif sub_experiment_index == 6:
            SubExperiment6(gui)
        elif sub_experiment_index == 7:
            SubExperiment7(gui)
        elif sub_experiment_index == 8:
            SubExperiment8(gui)
        else:
            raise Exception(f"Unknown sub experiment index {sub_experiment_index}.")

    @staticmethod
    def result_filename():
        experiment = Combination2.experiment_abbreviation()
        subject = config.SUBJECT_TAG.lower()
        return subject + "_" + experiment + ".csv"

    @staticmethod
    def experiment_abbreviation():
        return "Combination2"


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


def _display_shape(symbol, canvas, shape_scale, square_fraction=1):
    w = canvas.winfo_width()
    L = w * shape_scale
    if square_fraction < 1:
        square_args = [(w - L) / 2, 0, (w - L) / 2 + L, L * square_fraction]
    else:
        square_args = [(w - L) / 2, (w - L) / 2, (w - L) / 2 + L, (w - L) / 2 + L]
    if symbol == 'bluesquare':
        canvas.create_rectangle(*square_args, fill='blue', outline="", tags="shape")
    elif symbol == 'yellowsquare':
        canvas.create_rectangle(*square_args, fill='yellow', outline="", tags="shape")
    else:
        raise Exception("Unknown symbol {}".format(symbol))


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
    gui = Gui(use_screen2=True)
    e = None
    if config.EXPERIMENT == config.COMBINATION2:
        e = Combination2(gui)
    elif config.EXPERIMENT == config.MATCHING_TO_SAMPLE_SAMPLE:
        e = MatchingToSample(gui, is_combination=False, responses_are_samples=True)
    elif config.EXPERIMENT == config.MATCHING_TO_SAMPLE_SYMBOLS:
        e = MatchingToSample(gui, is_combination=False, responses_are_samples=False,
                             use_screen1=False)
    elif config.EXPERIMENT == config.MATCHING_TO_SAMPLE_SYMBOLS_STARWHITE:
        e = MatchingToSample(gui, is_combination=False, responses_are_samples=False,
                             use_screen1=False, white_circle=False, white_star=True)
    elif config.EXPERIMENT == config.MATCHING_TO_SAMPLE_SYMBOLS_BOTHWHITE:
        e = MatchingToSample(gui, is_combination=False, responses_are_samples=False,
                             use_screen1=False, white_circle=True, white_star=True)
    elif config.EXPERIMENT == config.SINGLE_STIMULUS_DISCRIMINATION:
        e = SingleStimulusDiscrimination(gui, is_combination=False, use_screen1=False)
    else:
        print("Error: Undefined experiment name '" + config.EXPERIMENT + "'.")
    if e:
        e.gui.root.mainloop()
