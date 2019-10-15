import tkinter as tk
import random
import subprocess
import config_human as config
import csv
import time
import os
from tkinter import PhotoImage
from sys import platform
from datetime import datetime
from math import ceil, sqrt  # , sin, cos, pi

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

BACKGROUND_COLOR = hex_format % (192, 192, 192)  # As in March 7
SEPARATOR_COLOR = hex_format % (255, 255, 255)

# The color of the "blackout" screen after incorrect answer
BLACKOUT_COLOR = hex_format % (100, 100, 100)

# Width (and height) of the Next button, as a fraction of H/3
NEXT_BUTTON_WIDTH = 0.65

SYMBOL_WIDTH = 0.75

frame_options = dict()  # For debugging frame positioning
'''
frame_options = {'highlightbackground': 'blue',
                 'highlightcolor': 'blue',
                 'highlightthickness': 1,
                 'bd': 0}
'''

canvas_options = {'bd': 0, 'highlightthickness': 0}
# canvas_options = {'bd': 1, 'highlightthickness': 1}

TOL = 0.99
TIMETOL = 3  # Round delay times to nearest millisecond


class Gui():
    def __init__(self):
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

        self.W = self.screen_width * TOL
        self.H = self.screen_height * TOL
        self.h = self.H / 3

        self.canvas_width = self.h

        self._make_images()
        self._make_widgets()

        self.next_displayed = False
        self.stimulus_displayed = False
        self.options_displayed = False
        self.left_option_displayed = False
        self.right_option_displayed = False
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
                            'vertical_button.gif': PhotoImage(file='vertical_button.gif'),
                            'happy_face.gif': PhotoImage(file='happy_face.gif'),
                            'sad_face.gif': PhotoImage(file='sad_face.gif')}
        self.root.update()
        for key, image_file in self.image_files.items():
            # scaling_factor = ceil(image_file.width() / self.left_canvas.winfo_width())
            scaling_factor = ceil(image_file.width() / self.canvas_width)
            self.image_files[key] = image_file.subsample(scaling_factor)

    def _make_widgets(self):
        W = self.W
        H = self.H
        h = self.h

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

        # SEPARATOR1
        self.separator1 = tk.Frame(height=4, background=SEPARATOR_COLOR, bd=0,
                                   highlightthickness=0)
        self.separator1.pack(fill=tk.X, padx=0, pady=0)

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

        # SEPARATOR2
        self.separator2 = tk.Frame(height=4, background='white', bd=0, highlightthickness=0)
        self.separator2.pack(fill=tk.X, padx=0, pady=0)

        # BOTTOM
        self.bottom_canvas_width = h * NEXT_BUTTON_WIDTH
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

        # Text
        self.text_frame = tk.Frame(self.root, width=W, height=H, **frame_options)
        # self.text_canvas = tk.Canvas(self.text_frame, width=W, height=H, **canvas_options)
        # self.text_frame.pack_propagate(False)

        # self.text_label = tk.Label(self.top_frame, text=config.INSTRUCTION_TEXT, justify=tk.LEFT)
        self.text_variable = tk.StringVar()
        self.text_variable.set(config.INSTRUCTION_TEXT)
        self.text_label = tk.Label(self.text_frame, textvariable=self.text_variable,
                                   justify=tk.LEFT, font=config.TEXTS_FONT,
                                   background=START_SCREEN_COLOR)
        self.text_label.pack()
        self.text_frame.place(relx=.5, rely=.5, anchor="center")
        # self.text_frame.pack(expand=True, side=tk.TOP)

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
        self.separator1.configure(background=color)
        self.separator2.configure(background=color)

    def clear(self):
        self.set_background_color(BACKGROUND_COLOR)
        self.separator1.configure(background=SEPARATOR_COLOR)
        self.separator2.configure(background=SEPARATOR_COLOR)
        self.clear_canvases()
        self.text_frame.place_forget()

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
        self.left_option_displayed = False
        self.right_option_displayed = False

    def delete_window(self):
        exit(0)

    def blackout(self, color=BLACKOUT_COLOR):
        self._set_entire_screen_color(color)
        self.blackout_displayed = True

    def show_only_next(self):
        self.clear()
        self.display_next()

    def display_next(self):
        self.bottom_canvas.create_polygon(*self.next_symbol_args, fill='white', outline='',
                                          width=0)
        self.next_displayed = True

    def display_stimulus(self, stimulus, shape_scale, fraction=1, force_mid=False):
        _display_shape(stimulus, self.top_mid_canvas, shape_scale, fraction)
        self.stimulus_displayed = True

    def _display_image(self, symbol, canvas):
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        canvas.create_image(w / 2, h / 2, image=self.image_files[symbol], anchor=tk.CENTER)

    def display_pause_screen(self):
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
        elif self.options_displayed or self.left_option_displayed or self.right_option_displayed:
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
    def __init__(self, gui, bind_diagonal_canvases=False):

        self.gui = gui

        self.gui.root.bind("<Button-1>", self.undesired_click)

        if bind_diagonal_canvases:  # config.RESPONSE_BUTTONS_DIAGONAL == "on":
            self.gui.bottom_left_canvas.bind("<Button-1>", self.left_clicked)
            self.gui.top_right_canvas.bind("<Button-1>", self.right_clicked)
        else:
            self.gui.left_canvas.bind("<Button-1>", self.left_clicked)
            self.gui.right_canvas.bind("<Button-1>", self.right_clicked)

        self.gui.bottom_canvas.bind("<Button-1>", self.next_clicked)
        self.gui.top_mid_canvas.bind("<Button-1>", self.stimulus_clicked)
        self.gui.root.bind("<space>", self.space_pressed)

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
        self.gui.text_frame.place_forget()
        _play('space_bar_sound.wav')

    def get_ready_to_start_trial(self):
        self.gui.blackout_displayed = False
        self.gui.snack_time = False
        # if self.finished_trial_cnt >= config.TRIALS_BEFORE_PAUSE:
        #     self.gui.display_pause_screen()
        #     _play('space_bar_sound.wav')
        #     self.finished_trial_cnt = 0
        # else:
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

    # def is_sub_experiment_done(self):
    #     return False

    def is_sub_experiment_done(self):
        return (self.success_frequency >= 0.8)

    def stimulus_clicked(self, event=None):
        self.gui.last_clicked_button_canvas = "S"

    def left_clicked(self, event=None):
        self.gui.last_clicked_button_canvas = "R1"
        self.clicked_option = "left"
        return self._left_clicked(event)

    def right_clicked(self, event=None):
        self.gui.last_clicked_button_canvas = "R2"
        self.clicked_option = "right"
        return self._right_clicked(event)

    def _left_clicked(self, event):
        assert(False)  # Must be overridden

    def _right_clicked(self, event):
        assert(False)  # Must be overridden

    def update_success_frequency(self, is_correct):
        if is_correct is None:  # For example for probe trials
            return
        self.success_list.append(int(is_correct))
        # if len(self.success_list) > 3:  # XXX
        if len(self.success_list) > 20:
            self.success_list.pop(0)
        # if len(self.success_list) >= 3:  # XXX
        if len(self.success_list) >= 20:
            self.success_frequency = round(sum(self.success_list) / len(self.success_list), 3)

    def correct_choice(self):
        # self.gui.clear()
        self.gui._set_entire_screen_color(BACKGROUND_COLOR)
        play_correct()
        self._show_happy_face()
        self.gui.snack_time = True
        job = self.gui.root.after(config.DELAY_AFTER_REWARD, self.get_ready_to_start_trial)
        self.current_after_jobs = [job]

    def incorrect_choice(self):
        # self.cancel_all_after_jobs()
        self.gui.blackout()
        play_incorrect()
        self._show_sad_face()
        job = self.gui.root.after(config.BLACKOUT_TIME, self.get_ready_to_start_trial)
        self.current_after_jobs = [job]

    def _show_happy_face(self):
        self.gui.text_frame.place(relx=.5, rely=.5, anchor="center")
        self.gui.text_label.configure(image=self.gui.image_files['happy_face.gif'],
                                      background=BACKGROUND_COLOR)

    def _show_sad_face(self):
        self.gui.text_frame.place(relx=.5, rely=.5, anchor="center")
        self.gui.text_label.configure(image=self.gui.image_files['sad_face.gif'],
                                      background=BLACKOUT_COLOR)

    def undesired_click(self, event=None):
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

        file_data.extend([("sub_experiment_index", self.sub_experiment_index)])

        file_data.extend([("subject", config.SUBJECT_TAG),
                          ("date", datestamp()),
                          ("timestamp", timestamp()),
                          ("trial", self.started_trial_cnt),
                          ("stimulus", stimulus_acronym),
                          ("response", self.clicked_option)])

        if hasattr(self, "is_practice_trial") and self.is_practice_trial is not None:
            file_data.extend([("is_practice_trial", self.is_practice_trial)])
        else:
            file_data.extend([("is_practice_trial", "na")])

        if self.success_frequency is not None and not is_undesired:
            file_data.extend([("is_correct", self.is_correct)])
        else:
            file_data.extend([("is_correct", "None")])

        file_data.extend([("response_time", response_time)])

        file_data.extend([("BLACKOUT_TIME", config.BLACKOUT_TIME),
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

        # Add experiment specific data
        file_data.extend(self.get_file_data())

        headers = list()
        values = list()
        for data in file_data:
            header, value = data
            if value is None:
                value = "None"
            headers.append(header)
            values.append(value)
        self.result_file.write(headers, values)

    def get_file_data(self):
        if self.sub_experiment_index == 4:
            return [("SDP_" + key, value) for key, value in config.SDP.items()]
        else:
            return [("SDP_" + key, "na") for key, value in config.SDP.items()]

    def get_stimulus_acronym(self):
        assert(False)  # Must be overloaded
        # stimulus_acronym = "None"
        # if hasattr(self, "stimulus") and self.stimulus is not None:
        #     if self.stimulus == COLOR_A:
        #         stimulus_acronym = "A"
        #     elif self.stimulus == COLOR_B:
        #         stimulus_acronym = "B"
        #     elif self.stimulus == SequenceDiscriminationProbe.LONG_AB:
        #         stimulus_acronym = "AB"
        #     elif self.stimulus == SequenceDiscriminationProbe.SHORT_AB:
        #         stimulus_acronym = "aB"
        #     else:
        #         assert(False)
        #     return stimulus_acronym
        # else:
        #     return None


BLUESQUARE = 'bluesquare'
YELLOWSQUARE = 'yellowsquare'
ORANGESQUARE = 'orangesquare'
LIGHTBLUESQUARE = 'lightbluesquare'

YELLOWCIRCLE = 'yellowcircle'
WHITECIRCLE = 'whitecircle'

BLUESTAR = 'bluestar'
WHITESTAR = 'whitestar'


# xyz exp1
class SingleStimulusDiscriminationMarch7(Experiment):
    def __init__(self, gui, delay=None):
        assert(delay is not None)
        self.delay = delay

        super().__init__(gui)

        self.is_correct = None

        self.is_practice_trial = None

        # The last displayed stimulus
        self.stimulus = None
        self.STIMULUS_TIME = 2000

        self.POT10 = [ORANGESQUARE, LIGHTBLUESQUARE] * 5

        self._create_new_stimuli()

    def _create_new_stimuli(self):
        self.stimulus_pot = list(self.POT10)  # Make a copy
        random.shuffle(self.stimulus_pot)

    def display_options(self):
        h = self.gui.canvas_width
        L = 0.75 * h  # self.gui.left_canvas.winfo_height()

        if (self.is_practice_trial and not self.is_lightblue) or (not self.is_practice_trial):
            # Circle
            self.gui.left_canvas.create_oval((h - L) / 2, (h - L) / 2, (h + L) / 2, (h + L) / 2,
                                             fill=hex_format % (255, 255, 255), outline="",
                                             tags="shape")
            self.gui.left_option_displayed = True
        if (self.is_practice_trial and self.is_lightblue) or (not self.is_practice_trial):
            # Triangle
            self.gui.right_canvas.create_polygon((h - L) / 2, h / 2 + L * sqrt(3) / 4,
                                                 h / 2, h / 2 - L * sqrt(3) / 4,
                                                 h - (h - L) / 2, h / 2 + L * sqrt(3) / 4,
                                                 fill=hex_format % (0, 0, 0),
                                                 outline="", tags="shape")
            self.gui.right_option_displayed = True

        self.tic = time.time()

    def _left_clicked(self, event=None):
        if self.gui.left_option_displayed:
            self.is_correct = not self.is_lightblue
            return self._option_clicked(event)

    def _right_clicked(self, event=None):
        if self.gui.right_option_displayed:
            self.is_correct = self.is_lightblue
            return self._option_clicked(event)

    def _option_clicked(self, event):
        if self.is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.gui.left_option_displayed = False
        self.gui.right_option_displayed = False
        self.write_to_file(event)
        return "break"

    def start_trial(self, event=None):
        practice_trial_interval = 4  # In March 7 set to 4
        # if self.use_practice_trials:
        self.is_practice_trial = (self.finished_trial_cnt % practice_trial_interval == 0)
        # else:
        # self.is_practice_trial = False
        self.gui.clear()
        self.display_random_symbol()
        job1 = self.gui.root.after(self.STIMULUS_TIME, self.gui.clear)
        job2 = self.gui.root.after(self.STIMULUS_TIME + self.delay, self.display_options)
        self.current_after_jobs = [job1, job2]

    def display_random_symbol(self):
        self.stimulus = self.stimulus_pot.pop()
        if len(self.stimulus_pot) == 0:
            self._create_new_stimuli()
        _display_shape(self.stimulus, self.gui.top_mid_canvas,
                       shape_scale=SYMBOL_WIDTH, force_mid=True)
        self.is_lightblue = (self.stimulus == LIGHTBLUESQUARE)
        self.stimulus_displayed = True

    def get_stimulus_acronym(self):
        return self.stimulus


# xyz exp2
class SequenceDiscriminationFullscreen(Experiment):
    def __init__(self, gui):
        super().__init__(gui, bind_diagonal_canvases=True)
        self.gui.options_displayed = False
        self.is_correct = True  # Initialize to True so that first sequence is taken from pot

        # The time (in milliseconds) that the stimulus (each stimulus in sequences) is presented
        self.STIMULUS_TIME = 1500

        # The inter-stimulus time
        self.INTER_STIMULUS_TIME = 300

        # The color of stimulus A
        self.COLOR_A = hex_format % (0, 0, 255)

        # The color of stimulus B
        self.COLOR_B = hex_format % (255, 255, 0)

        self.AA = (self.COLOR_A, self.COLOR_A)
        self.AB = (self.COLOR_A, self.COLOR_B)
        self.BA = (self.COLOR_B, self.COLOR_A)
        self.BB = (self.COLOR_B, self.COLOR_B)
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
        self.gui.clear()
        job1, job2, job3 = self.display_random_sequence()
        self.current_after_jobs = [job1, job2, job3]
        time_to_options = 2 * self.STIMULUS_TIME + self.INTER_STIMULUS_TIME
        job4 = self.gui.root.after(time_to_options, self.display_options)
        self.current_after_jobs.append(job4)

    def display_random_sequence(self):
        # if config.USE_CORRECTION_TRIALS == "on":
        if self.is_correct:
            self.stimulus1, self.stimulus2 = self.sequences.pop()
        else:
            pass  # Repeat the previous sequence (i.e. keep self.stimulus{1,2}))
        # else:
        #     self.stimulus1, self.stimulus2 = self.sequences.pop()
        if len(self.sequences) == 0:
            self._create_new_sequences()

        # self.display_symbol_top(self.stimulus1)
        self.gui._set_entire_screen_color(self.stimulus1)
        # job1 = self.gui.root.after(config.STIMULUS_TIME, self.gui.clear)
        job1 = self.gui.root.after(self.STIMULUS_TIME, self.gui._set_entire_screen_color,
                                   BACKGROUND_COLOR)
        job2 = self.gui.root.after(self.STIMULUS_TIME + self.INTER_STIMULUS_TIME,
                                   self.gui._set_entire_screen_color, self.stimulus2)
        job3 = self.gui.root.after(2 * self.STIMULUS_TIME + self.INTER_STIMULUS_TIME,
                                   self.gui._set_entire_screen_color, BACKGROUND_COLOR)
        self.current_after_jobs = [job1, job2, job3]
        self.is_AB = ((self.stimulus1, self.stimulus2) == self.AB)
        return job1, job2, job3

    def display_options(self):
        self.gui.clear()
        # if config.RESPONSE_BUTTONS_DIAGONAL == "on":
        self.gui._display_image('horizontal_button.gif', self.gui.bottom_left_canvas)
        self.gui._display_image('vertical_button.gif', self.gui.top_right_canvas)
        # else:
        #     self.gui._display_image(config.LEFT_OPTION, self.gui.left_canvas)
        #     self.gui._display_image(config.RIGHT_OPTION, self.gui.right_canvas)
        self.gui.options_displayed = True
        self.tic = time.time()

    def _display_symbol(self, symbol, canvas):
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        canvas.create_image(w / 2, h / 2, image=self.image_files[symbol], anchor=tk.CENTER)

    def _left_clicked(self, event=None):
        if self.gui.options_displayed:
            self.is_correct = self.is_AB
            self._option_chosen(event)

    def _right_clicked(self, event=None):
        if self.gui.options_displayed:
            self.is_correct = not self.is_AB
            self._option_chosen(event)

    def _option_chosen(self, event):
        if self.is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.write_to_file(event)
        self.gui.options_displayed = False

    def get_stimulus_acronym(self):
        if self.stimulus1 == self.COLOR_A and self.stimulus2 == self.COLOR_A:
            return "AA"
        elif self.stimulus1 == self.COLOR_A and self.stimulus2 == self.COLOR_B:
            return "AB"
        elif self.stimulus1 == self.COLOR_B and self.stimulus2 == self.COLOR_A:
            return "BA"
        elif self.stimulus1 == self.COLOR_B and self.stimulus2 == self.COLOR_B:
            return "BB"


# exp3
class SingleStimulusDiscrimination(Experiment):
    def __init__(self, gui, delay=None):

        assert(delay is not None)
        self.delay = delay

        self.STIMULUS_TIME = 2000

        super().__init__(gui)

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
        # if config.YELLOW_POS == 'left':
        #     self.left_is_correct = (self.stimulus == self.YELLOWSQUARE)
        # else:
        self.left_is_correct = (self.stimulus != self.YELLOWSQUARE)
        # if config.YELLOW_POS == 'left':
        #     self.gui._display_image("white_circle.gif", self.gui.left_canvas)
        #     self.gui._display_image("white_star.gif", self.gui.right_canvas)
        # else:
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
        job1 = self.gui.root.after(self.STIMULUS_TIME, self.gui.clear)
        job2 = self.gui.root.after(self.STIMULUS_TIME + self.delay, self.display_options)
        self.current_after_jobs = [job1, job2]

    def display_random_symbol(self):
        self.stimulus = self.stimulus_pot.pop()
        if len(self.stimulus_pot) == 0:
            self._create_new_stimuli()
        _display_shape(self.stimulus, self.gui.top_mid_canvas, shape_scale=SYMBOL_WIDTH,
                       force_mid=True)
        self.stimulus_displayed = True

    def get_stimulus_acronym(self):
        return self.stimulus


# exp4
class SequenceDiscriminationProbe(Experiment):
    SHORT_AB = "shortAB"
    LONG_AB = "longAB"

    def __init__(self, gui):
        super().__init__(gui)

        self.is_correct = None

        # The last displayed stimulus
        self.stimulus = None
        self.stimulus_cnt = 0

        self.STIMULUS_A = 'yellowsquare'
        self.STIMULUS_B = 'bluesquare'

        self.STIMULUS_POT = [self.STIMULUS_A, self.STIMULUS_B] * 5
        self.PROBE_POT = [SequenceDiscriminationProbe.SHORT_AB,
                          SequenceDiscriminationProbe.LONG_AB] * 5
        self._create_new_stimuli()
        self._create_new_probes()

    def _create_new_stimuli(self):
        self.stimulus_pot = list(self.STIMULUS_POT)  # Make a copy
        random.shuffle(self.stimulus_pot)

    def _create_new_probes(self):
        self.probe_pot = list(self.PROBE_POT)  # Make a copy
        random.shuffle(self.probe_pot)

    def display_options(self):
        # if config.YELLOW_POS == 'left':
        #     self.left_is_correct = (self.stimulus == self.STIMULUS_A)
        # else:
        self.left_is_correct = (self.stimulus != self.STIMULUS_A)
        # if config.YELLOW_POS == 'left':
        #     self.gui._display_image("white_circle.gif", self.gui.left_canvas)
        #     self.gui._display_image("white_star.gif", self.gui.right_canvas)
        # else:
        self.gui._display_image("white_star.gif", self.gui.left_canvas)
        self.gui._display_image("white_circle.gif", self.gui.right_canvas)
        self.gui.options_displayed = True
        self.tic = time.time()

    def start_trial(self, event=None):
        self.gui.clear()
        time_to_options = self.display_random_stimulus()
        job = self.gui.root.after(time_to_options, self.display_options)
        self.current_after_jobs.append(job)

    def display_random_stimulus(self):
        self.stimulus_cnt += 1
        is_probe_trial = (self.stimulus_cnt % config.SDP["PROBE_TRIAL_INTERVAL"] == 0)
        if is_probe_trial:
            self.stimulus = self.probe_pot.pop()
            if len(self.probe_pot) == 0:
                self._create_new_probes()
        else:
            self.stimulus = self.stimulus_pot.pop()
            if len(self.stimulus_pot) == 0:
                self._create_new_stimuli()

        self.is_seq = False
        if self.stimulus in (self.STIMULUS_A, self.STIMULUS_B):
            time_to_options = config.SDP["SINGLE_STIMULUS_TIME"] + config.SDP["DELAY"]
            # _display_shape(self.stimulus, self.gui.top_canvas,
            #                shape_scale=1)  # The canvas itself has the correct size
            _display_shape(self.stimulus, self.gui.top_mid_canvas, shape_scale=SYMBOL_WIDTH,
                           force_mid=True)
            job1 = self.gui.root.after(config.SDP["SINGLE_STIMULUS_TIME"], self.gui.clear)
            self.current_after_jobs = [job1]
            self.stimulus_displayed = True

        else:
            self.is_seq = True
            if self.stimulus == SequenceDiscriminationProbe.SHORT_AB:
                A_time = config.SDP["SHORT_A_TIME"]
            else:
                A_time = config.SDP["LONG_A_TIME"]
            _display_shape(self.STIMULUS_A, self.gui.top_mid_canvas,
                           shape_scale=SYMBOL_WIDTH, force_mid=True)
            job1 = self.gui.root.after(A_time, self.gui.clear)
            arg = [self.STIMULUS_B,
                   self.gui.top_mid_canvas,
                   SYMBOL_WIDTH,
                   1,
                   True]
            job2 = self.gui.root.after(A_time + config.SDP["INTER_STIMULUS_TIME"],
                                       _display_shape, *arg)
            job3 = self.gui.root.after(A_time + config.SDP["INTER_STIMULUS_TIME"] + config.SDP["B_TIME"],
                                       self.gui.clear)
            self.current_after_jobs = [job1, job2, job3]
            time_to_options = A_time + config.SDP["INTER_STIMULUS_TIME"] + config.SDP["B_TIME"] + config.SDP["DELAY"]

        return time_to_options

    def _left_clicked(self, event=None):
        if self.gui.options_displayed:
            if self.is_seq:
                self._option_chosen_after_seq(event)
            else:
                self.is_correct = self.left_is_correct
                self._option_chosen(event)
            return "break"

    def _right_clicked(self, event=None):
        if self.gui.options_displayed:
            if self.is_seq:
                self._option_chosen_after_seq(event)
            else:
                self.is_correct = not self.left_is_correct
                self._option_chosen(event)
            return "break"

    def _option_chosen_after_seq(self, event):
        self.is_correct = None
        self.write_to_file(event=event)
        self.gui.options_displayed = False
        self.gui.clear()
        self.get_ready_to_start_trial()

    def _option_chosen(self, event):
        if self.is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.write_to_file(event=event)
        self.gui.options_displayed = False

    def get_stimulus_acronym(self):
        if self.stimulus == self.STIMULUS_A:
            return "A"
        elif self.stimulus == self.STIMULUS_B:
            return "B"
        elif self.stimulus == SequenceDiscriminationProbe.SHORT_AB:
            return "aB"
        elif self.stimulus == SequenceDiscriminationProbe.LONG_AB:
            return "AB"


class SubExperiment1(SingleStimulusDiscriminationMarch7):
    def __init__(self, gui):
        super().__init__(gui, delay=0)
        self.sub_experiment_index = 1

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment2(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()

    def result_filename(self):
        return CombinationHuman.result_filename()


class SubExperiment2(SequenceDiscriminationFullscreen):
    def __init__(self, gui):
        super().__init__(gui)
        self.sub_experiment_index = 2
        global BACKGROUND_COLOR
        global SEPARATOR_COLOR
        BACKGROUND_COLOR = hex_format % (0, 0, 0)
        SEPARATOR_COLOR = hex_format % (0, 0, 0)

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment3(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()

    def result_filename(self):
        return CombinationHuman.result_filename()


class SubExperiment3(SingleStimulusDiscrimination):
    def __init__(self, gui):
        super().__init__(gui, delay=500)
        self.sub_experiment_index = 3

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            next_experiment = SubExperiment4(self.gui)
            next_experiment.finished_trial_cnt = self.finished_trial_cnt
            next_experiment.get_ready_to_start_trial()
        else:
            super().get_ready_to_start_trial()

    def result_filename(self):
        return CombinationHuman.result_filename()


class SubExperiment4(SequenceDiscriminationProbe):
    def __init__(self, gui):
        super().__init__(gui)
        self.sub_experiment_index = 4

    def get_ready_to_start_trial(self):
        if self.is_sub_experiment_done():
            self.gui.display_pause_screen()
            self.gui.text_variable.set(config.FINISH_TEXT)
            self.gui.text_label.configure(image='', background=START_SCREEN_COLOR)
            self.gui.text_frame.place(relx=.5, rely=.5, anchor="center")
        else:
            super().get_ready_to_start_trial()

    def result_filename(self):
        return CombinationHuman.result_filename()


class CombinationHuman():
    def __init__(self, gui):
        self.gui = gui
        filename = self.result_filename()
        self.result_file = ResultFile(filename)
        SubExperiment1(gui)

    @staticmethod
    def result_filename():
        d = datestamp()
        t = timestamp()
        return config.SUBJECT_TAG + "_" + d + "_" + t + ".csv"


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

    elif symbol == 'lightbluesquare':
        canvas.create_rectangle(*square_args, fill=hex_format % (51, 153, 255), outline="",
                                tags="shape")
    elif symbol == 'orangesquare':
        canvas.create_rectangle(*square_args, fill=hex_format % (255, 128, 0), outline="",
                                tags="shape")
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
    # e = None
    # if config.EXPERIMENT == config.COMBINATION_HUMAN:
    e = CombinationHuman(gui)

    # # exp1
    # elif config.EXPERIMENT == config.SINGLE_STIMULUS_DISCRIMINATION_MARCH7:
    #     e = SingleStimulusDiscriminationMarch7(gui,
    #                                            exp_abbrev=config.SINGLE_STIMULUS_DISCRIMINATION_MARCH7)

    # # exp2
    # elif config.EXPERIMENT == config.SEQUENCE_DISCRIMINATION_FULLSCREEN:
    #     e = SequenceDiscriminationFullscreen(gui,
    #                                          exp_abbrev=config.SEQUENCE_DISCRIMINATION_FULLSCREEN)

    # # exp3a
    # elif config.EXPERIMENT == config.PROBE_TRIAL_PRETRAINING:
    #     e = SingleStimulusDiscrimination(gui, exp_abbrev=config.PROBE_TRIAL_PRETRAINING)
    #     e.delay = 500

    # elif config.EXPERIMENT == config.SEQUENCE_DISCRIMINATION_PROBE:
    #     e = SequenceDiscriminationProbe(gui)

    # else:
    #     print("Error: Undefined experiment name '" + config.EXPERIMENT + "'.")
    # if e:
    e.gui.root.mainloop()
