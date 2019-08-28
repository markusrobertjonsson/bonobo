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

# frame_options = dict()  # For debugging frame positioning
frame_options = {'highlightbackground': 'blue',
                 'highlightcolor': 'blue',
                 'highlightthickness': 1,
                 'bd': 0}

# canvas_options = {'bd': 0, 'highlightthickness': 0}
canvas_options = {'bd': 1, 'highlightthickness': 1}

TOL = 0.49
TIMETOL = 3  # Round delay times to nearest millisecond


class Experiment():
    def __init__(self, is_combination=False, use_screen2=False):
        self.is_combination = is_combination
        self.use_screen2 = use_screen2
        self.sub_experiment_index = None
        filename = self.result_filename()
        self.result_file = ResultFile(filename)
        self.started_trial_cnt = 0
        self.finished_trial_cnt = 0
        self.clicked_option = None
        self.last_clicked_button_canvas = "None"

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
        self.snack_time = False
        self.display_pause_screen()

        self.window_geometry = None  # Used when is_combination is True and
                                     # self.stimulus_window is not None

        # XXX add
        # if self.is_combination:
        #     self.toggle_fullscreen()

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
        t.attributes('-zoomed', True)  # Maximize window
        t.update()
        screen_width = t.winfo_width()
        screen_height = t.winfo_height()
        # print(f"screen_width={screen_width}")
        # print(f"screen_height={screen_height}")
        t.destroy()  # Delete the temporary window

        self.root = tk.Tk()

        W = screen_width * TOL
        H = screen_height * TOL
        h = H / 3

        # print(f"self.root.winfo_screenwidth()={self.root.winfo_screenwidth()}")
        # print(f"self.root.winfo_screenheight()={self.root.winfo_screenheight()}")

        self.canvas_width = h

        # self.root.attributes('-zoomed', True)  # Maximize window

        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)
        self.root.bind("<space>", self.space_pressed)
        self.root.bind("<Button-1>", self.undesired_click)

        # TOP
        self.top_frame = tk.Frame(self.root, width=W, height=h, **frame_options)

        self.top_left_canvas = tk.Canvas(self.top_frame, width=self.canvas_width,
                                         height=self.canvas_width, **canvas_options)
        self.top_mid_canvas = tk.Canvas(self.top_frame, width=self.canvas_width,
                                        height=self.canvas_width, **canvas_options)
        self.top_right_canvas = tk.Canvas(self.top_frame, width=self.canvas_width,
                                          height=self.canvas_width, **canvas_options)
        # self.top_right_canvas.bind("<Button-1>", self.right_clicked)
        self.top_left_canvas.pack(side=tk.LEFT)
        # self.top_mid_canvas.pack(side=tk.MIDDLE)
        self.top_mid_canvas.place(relx=.5, rely=.5, anchor="center")
        self.top_right_canvas.pack(side=tk.RIGHT)

        self.top_frame.pack_propagate(False)
        self.top_frame.pack(expand=True, side=tk.TOP)

        # MIDDLE
        # space_width = h / 3
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
        self.left_canvas.bind("<Button-1>", self.left_clicked)
        self.left_canvas.pack(side=tk.RIGHT)

        self.right_canvas = tk.Canvas(self.middle_right_frame, width=self.canvas_width,
                                      height=self.canvas_width, **canvas_options)
        self.right_canvas.bind("<Button-1>", self.right_clicked)
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
        # self.bottom_left_canvas.bind("<Button-1>", self.left_clicked)
        self.bottom_right_canvas = tk.Canvas(self.bottom_frame, width=self.canvas_width,
                                             height=self.canvas_width, **canvas_options)
        self.bottom_left_canvas.pack(side=tk.LEFT)
        self.bottom_right_canvas.pack(side=tk.RIGHT)
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

        if config.HIDE_MOUSE_POINTER:
            # Hide mouse pointer
            self.root.config(cursor="none")

        self.root.title("Main Window")
        if self.is_combination:
            self.root.protocol("WM_DELETE_WINDOW", self.delete_window)

        self.stimulus_window = None
        if self.use_screen2:
            self.stimulus_window = StimulusWindow(self.root)

    def delete_window(self):
        exit(0)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen  # Just toggling the boolean
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def end_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
        return "break"

    def blackout(self, color=BLACKOUT_COLOR):
        self._set_entire_screen_color(color)
        self.blackout_displayed = True
        if self.stimulus_window:
            self.stimulus_window.blackout()

    def display_pause_screen(self):
        if self.stimulus_window:
            self.stimulus_window.display_pause_screen()
        self._set_entire_screen_color(START_SCREEN_COLOR)
        self.pause_screen_displayed = True
        self.blackout_displayed = False
        self.snack_time = False

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
        self.bottom_left_canvas.configure(background=color)
        self.bottom_right_canvas.configure(background=color)
        self.top_left_canvas.configure(background=color)
        self.top_mid_canvas.configure(background=color)
        self.top_right_canvas.configure(background=color)

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
        self.go_displayed = False
        self.stimulus_displayed = False
        if hasattr(self, "options_displayed"):
            self.options_displayed = False
        if hasattr(self, "left_option_displayed"):
            self.left_option_displayed = False
        if hasattr(self, "right_option_displayed"):
            self.right_option_displayed = False

    def show_only_next(self):
        self.clear()
        self.display_next()

    def display_next(self):
        self.bottom_canvas.create_polygon(*self.next_symbol_args, fill=NEXT_BUTTON_COLOR,
                                          outline='', width=0)
        self.next_displayed = True

    def display_stimulus_symbol(self, symbol, canvas):
        self._display_symbol(symbol, canvas)
        self.stimulus_displayed = True

    def _display_symbol(self, symbol, canvas):
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        canvas.create_image(w / 2, h / 2, image=self.image_files[symbol], anchor=tk.CENTER)

    def next_clicked(self, event=None):
        self.last_clicked_button_canvas = "NB"
        if self.next_displayed:
            self.next_displayed = False
            self.started_trial_cnt += 1
            self.start_trial()
            return "break"  # To detect "undesired clicks" outside any button

    def space_pressed(self, event=None):
        if self.pause_screen_displayed:
            self.get_ready_to_start_trial()
            self.pause_screen_displayed = False
        else:
            self.display_pause_screen()
            self.cancel_all_after_jobs()

    def get_ready_to_start_trial(self):
        if self.is_combination:
            # print(self.success_frequency)
            if self.is_sub_experiment_done():
                if self.is_combination:
                    self.window_geometry = self.get_window_geometry()
                self.root.destroy()  # Quits mainloop of current sub-experiment to get to the next
                return

        self.blackout_displayed = False
        self.snack_time = False
        if self.finished_trial_cnt >= config.TRIALS_BEFORE_PAUSE:
            self.display_pause_screen()
            self.finished_trial_cnt = 0
        else:
            self.clear()
            self.display_next()

    def get_window_geometry(self):
        self.root.update()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        main_window_pos = f"{w}x{h}+{x}+{y}"

        if self.stimulus_window:
            self.stimulus_window.root.update()
            w = self.stimulus_window.root.winfo_width()
            h = self.stimulus_window.root.winfo_height()
            x = self.stimulus_window.root.winfo_x()
            y = self.stimulus_window.root.winfo_y()
            stimulus_window_pos = f"{w}x{h}+{x}+{y}"
        else:
            stimulus_window_pos = None
        return [main_window_pos, stimulus_window_pos]

    def set_window_geometry(window_geometry):
        self.root.geometry(window_geometry[0])
        if self.stimulus_window:
            self.stimulus_window.root.geometry(window_geometry[1])

    def cancel_all_after_jobs(self):
        for ind, job in enumerate(self.current_after_jobs):
            self.root.after_cancel(job)
            self.current_after_jobs[ind] = None
        self.current_after_jobs = []

    def start_trial(self, event=None):
        pass
        # assert(False)  # Must be overloaded

    def is_sub_experiment_done(self):
        return False

    def left_clicked(self, event=None):
        self.last_clicked_button_canvas = "R1"
        self.clicked_option = "left"
        return self._left_clicked(event)

    def right_clicked(self, event=None):
        self.last_clicked_button_canvas = "R2"
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
        if self.is_combination:
            return Combination1.result_filename()
        else:
            experiment = self.experiment_abbreviation()
            subject = config.SUBJECT_TAG.lower()
            date = datestamp()
            return subject + "_" + experiment + "_" + date + ".csv"

    def update_success_frequency(self, is_correct):
        if is_correct is None:  # For example for probe trials
            return
        self.success_list.append(int(is_correct))
        if len(self.success_list) > 20:
            self.success_list.pop(0)
        if len(self.success_list) >= 20:
            self.success_frequency = round(sum(self.success_list) / len(self.success_list), 3)

    def experiment_abbreviation(self):
        assert(False)  # Must be overloaded

    def correct_choice(self):
        self.clear()
        play_correct()
        self.snack_time = True
        job = self.root.after(config.DELAY_AFTER_REWARD, self.get_ready_to_start_trial)
        self.current_after_jobs = [job]

    def incorrect_choice(self):
        # self.cancel_all_after_jobs()
        self.blackout()
        play_incorrect()
        job = self.root.after(config.BLACKOUT_TIME, self.get_ready_to_start_trial)
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
                          ("LEFT_OPTION", config.LEFT_OPTION),
                          ("RIGHT_OPTION", config.RIGHT_OPTION),
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

        screen_touched = self._screen_touched()
        file_data.extend([("screen_touched", screen_touched)])

        cell_touched = self._cell_touched(x, y)
        file_data.extend([("cell_touched", cell_touched)])

        button_touched = self.last_clicked_button_canvas
        file_data.extend([("button_touched", button_touched)])
        self.last_clicked_button_canvas = "None"  # Reset for next click

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

    def _cell_touched(self, x, y):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
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

    def _screen_touched(self):
        if self.pause_screen_displayed:
            return "PS"  # Pause/Pink screen
        elif self.next_displayed:
            return "NBS"  # Next button screen
        elif self.blackout_displayed:
            return "BS"  # Blackout screen
        elif (hasattr(self, "options_displayed") and self.options_displayed) or \
             (hasattr(self, "left_option_displayed") and self.left_option_displayed) or  \
             (hasattr(self, "right_option_displayed") and self.right_option_displayed):
            return "RS"  # Response screen
        elif self.snack_time:
            return "ST"  # Snack time
        else:
            col = self.left_canvas["background"]
            if col == COLOR_A:
                return "STIMULUS_A"
            elif col == COLOR_B:
                return "STIMULUS_B"
            else:
                return "INTER_STIMULUS"

    def _display_shape(self, symbol, canvas, shape_scale):
        # L = self.L * 0.99  # self.top_frame.winfo_height() * config.SYMBOL_WIDTH
        # w = self.canvas_width
        w = canvas.winfo_width()
        L = w * shape_scale
        square_args = [(w - L) / 2, (w - L) / 2, (w - L) / 2 + L, (w - L) / 2 + L]
        if symbol == 'bluesquare':
            canvas.create_rectangle(*square_args, fill='blue', outline="", tags="shape")
        elif symbol == 'yellowsquare':
            canvas.create_rectangle(*square_args, fill='yellow', outline="", tags="shape")
        else:
            raise Exception("Unknown symbol {}".format(symbol))


class StimulusWindow():
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        # self.root.focus_set()
        self.is_fullscreen = False
        self._make_widgets()

        self.set_background_color(BACKGROUND_COLOR)
        self.stimulus_displayed = False
        self.display_pause_screen()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen  # Just toggling the boolean
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

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

    def clear(self):
        self.set_background_color(BACKGROUND_COLOR)
        self.clear_canvases()

    def clear_canvases(self):
        self.bottom_canvas.delete(tk.ALL)
        self.stimulus_displayed = False

    def _make_widgets(self):
        self.root.bind("<F11>", self.toggle_fullscreen)
        # W = self.root.winfo_screenwidth() * TOL
        # H = self.root.winfo_screenheight() * TOL
        # h = H / 3

        # self.canvas_width = h

        # # self.root.attributes('-zoomed', True)  # Maximize window

        # self.is_fullscreen = False
        # self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)
        # self.root.bind("<space>", self.space_pressed)
        # self.root.bind("<Button-1>", self.undesired_click)

        # # TOP
        # self.top_frame = tk.Frame(self.root, width=W, height=h, **frame_options)

        # self.top_left_canvas = tk.Canvas(self.top_frame, width=self.canvas_width,
        #                                  height=self.canvas_width, **canvas_options)
        # self.top_mid_canvas = tk.Canvas(self.top_frame, width=self.canvas_width,
        #                                 height=self.canvas_width, **canvas_options)
        # self.top_right_canvas = tk.Canvas(self.top_frame, width=self.canvas_width,
        #                                   height=self.canvas_width, **canvas_options)
        # # self.top_right_canvas.bind("<Button-1>", self.right_clicked)
        # self.top_left_canvas.pack(side=tk.LEFT)
        # # self.top_mid_canvas.pack(side=tk.MIDDLE)
        # self.top_mid_canvas.place(relx=.5, rely=.5, anchor="center")
        # self.top_right_canvas.pack(side=tk.RIGHT)

        # self.top_frame.pack_propagate(False)
        # self.top_frame.pack(expand=True, side=tk.TOP)

        # # MIDDLE
        # space_width = h / 3
        # self.middle_frame = tk.Frame(self.root, width=W, height=h, **frame_options)

        # self.middle_left_frame = tk.Frame(self.middle_frame, width=(W - space_width) / 2, height=h,
        #                                   **frame_options)
        # self.middle_left_frame.pack_propagate(False)
        # self.middle_left_frame.pack(side=tk.LEFT)

        # self.middle_space_frame = tk.Frame(self.middle_frame, width=space_width, height=h,
        #                                    **frame_options)
        # self.middle_space_frame.pack_propagate(False)
        # self.middle_space_frame.pack(side=tk.LEFT)
        # self.middle_right_frame = tk.Frame(self.middle_frame, width=(W - space_width) / 2,
        #                                    height=h, **frame_options)
        # self.middle_right_frame.pack_propagate(False)
        # self.middle_right_frame.pack(side=tk.LEFT)

        # self.left_canvas = tk.Canvas(self.middle_left_frame, width=self.canvas_width,
        #                              height=self.canvas_width, **canvas_options)
        # self.left_canvas.bind("<Button-1>", self.left_clicked)
        # self.left_canvas.pack(side=tk.RIGHT)

        # self.right_canvas = tk.Canvas(self.middle_right_frame, width=self.canvas_width,
        #                               height=self.canvas_width, **canvas_options)
        # self.right_canvas.bind("<Button-1>", self.right_clicked)
        # self.right_canvas.pack(side=tk.LEFT)

        # self.middle_frame.pack_propagate(False)
        # self.middle_frame.pack(expand=True, side=tk.TOP)

        # # BOTTOM
        # self.bottom_canvas_width = h * config.NEXT_BUTTON_WIDTH
        H = self.root.winfo_screenheight() * TOL
        h = H * config.SCREEN2_STIMULUS_WIDTH
        self.bottom_frame = tk.Frame(self.root, width=h, height=h, **frame_options)
        self.bottom_canvas = tk.Canvas(self.bottom_frame, width=h, height=h * 0.99,
                                       **canvas_options)
        # self.bottom_left_canvas = tk.Canvas(self.bottom_frame, width=self.canvas_width,
        #                                     height=self.canvas_width, **canvas_options)
        # # self.bottom_left_canvas.bind("<Button-1>", self.left_clicked)
        # self.bottom_right_canvas = tk.Canvas(self.bottom_frame, width=self.canvas_width,
        #                                      height=self.canvas_width, **canvas_options)
        # self.bottom_left_canvas.pack(side=tk.LEFT)
        # self.bottom_right_canvas.pack(side=tk.RIGHT)
        # self.bottom_canvas.bind("<Button-1>", self.next_clicked)
        self.bottom_canvas.pack(expand=False, side=tk.BOTTOM)

        self.bottom_frame.pack_propagate(False)
        self.bottom_frame.pack(expand=False, side=tk.BOTTOM)

        # self.root.update()
        # w = self.bottom_canvas.winfo_width()
        # pw = w * 0.1
        # d1 = w / 2 - pw / 2
        # d2 = w / 2 + pw / 2
        # self.next_symbol_args = [0, d1,
        #                          d1, d1,
        #                          d1, 0,
        #                          d2, 0,
        #                          d2, d1,
        #                          w, d1,
        #                          w, d2,
        #                          d2, d2,
        #                          d2, w,
        #                          d1, w,
        #                          d1, d2,
        #                          0, d2]

        if config.HIDE_MOUSE_POINTER:
            # Hide mouse pointer
            self.root.config(cursor="none")

        self.root.title("Stimulus Window")
        # if self.is_combination:
        self.root.protocol("WM_DELETE_WINDOW", self.delete_window)

    def delete_window(self):
        exit(0)


class MatchingToSample(Experiment):
    def __init__(self, is_combination=False, responses_are_samples=False, use_screen1=True,
                 use_screen2=False):
        # If true, the response buttons are the same as the samples
        # If false, the response buttons are the symbols in self.display_options
        self.responses_are_samples = responses_are_samples

        # Display samples on screen 1
        self.use_screen1 = use_screen1

        # Display samples on screen 2
        self.use_screen2 = use_screen2

        super().__init__(is_combination, use_screen2)

        if use_screen2:
            assert(self.stimulus_window)

        self.is_correct = None

        # The last displayed sample
        self.sample = None

        self.options_displayed = False

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
                self._display_shape(self.YELLOWSQUARE, self.left_canvas)
                self._display_shape(self.BLUESQUARE, self.right_canvas)
            else:
                self._display_shape(self.BLUESQUARE, self.left_canvas)
                self._display_shape(self.YELLOWSQUARE, self.right_canvas)
        else:
            if config.YELLOW_POS == 'left':
                self._display_symbol("yellow_circle.gif", self.left_canvas)
                self._display_symbol("blue_star.gif", self.right_canvas)
            else:
                self._display_symbol("blue_star.gif", self.left_canvas)
                self._display_symbol("yellow_circle.gif", self.right_canvas)
        self.options_displayed = True
        self.tic = time.time()

    def _left_clicked(self, event=None):
        if self.options_displayed:
            self.is_correct = self.left_is_correct
            return self._option_clicked(event)

    def _right_clicked(self, event=None):
        if self.options_displayed:
            self.is_correct = not self.left_is_correct
            return self._option_clicked(event)

    def _option_clicked(self, event):
        if self.is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.options_displayed = False
        self.write_to_file(event)
        return "break"

    def start_trial(self, event=None):
        self.clear()
        self.display_random_symbol()
        job = self.root.after(config.SYMBOL_SHOW_TIME_MTS, self.display_options)
        self.current_after_jobs = [job]

    def display_random_symbol(self):
        self.sample = self.sample_pot.pop()
        if len(self.sample_pot) == 0:
            self._create_new_samples()
        if self.use_screen1:
            self._display_shape(self.sample, self.top_mid_canvas,
                                shape_scale=config.SYMBOL_WIDTH_MTS)
        if self.use_screen2:
            self._display_shape(self.sample, self.stimulus_window.bottom_canvas,
                                shape_scale=1)  # The canvas itself has the correct size

    def get_file_data(self):
        return [("SYMBOL_SHOW_TIME_MTS", config.SYMBOL_SHOW_TIME_MTS),
                ("SYMBOL_WIDTH_MTS", config.SYMBOL_WIDTH_MTS)]

    def get_stimulus_acronym(self):
        return self.sample

    def is_sub_experiment_done(self):
        return (self.success_frequency >= 0.8)

    def experiment_abbreviation(self):
        if self.responses_are_samples:
            return config.MATCHING_TO_SAMPLE_SAMPLE
        else:
            return config.MATCHING_TO_SAMPLE_SYMBOLS


















# ---------------------------------------------------------------------------

class Pretraining(Experiment):
    def __init__(self, is_combination=False):
        super().__init__(is_combination)
        self.success_frequency = None
        self.left_option_displayed = False
        self.right_option_displayed = False
        self.stimulus_list = [COLOR_A] * 20 + [COLOR_B] * 20

    def start_trial(self, event=None):
        self.clear()
        is_done = self.display_next_stimulus()
        if is_done:
            self.display_pause_screen()
            self.cancel_all_after_jobs()
        else:
            self.display_option()

    def display_next_stimulus(self):
        if len(self.stimulus_list) == 0:
            return True
        self.stimulus = self.stimulus_list.pop()
        self._set_entire_screen_color(self.stimulus)
        self.is_A = (self.stimulus == COLOR_A)
        return False

    def display_option(self):
        # self.clear()
        if self.is_A:
            self._display_symbol(config.LEFT_OPTION, self.bottom_left_canvas)
            self.left_option_displayed = True
            self.right_option_displayed = False
        else:
            self._display_symbol(config.RIGHT_OPTION, self.top_right_canvas)
            self.right_option_displayed = True
            self.left_option_displayed = False
        self.tic = time.time()

    def _left_clicked(self, event=None):
        if self.left_option_displayed:
            self._option_chosen(event)
            return "break"

    def _right_clicked(self, event=None):
        if self.right_option_displayed:
            self._option_chosen(event)
            return "break"

    def _option_chosen(self, event):
        self.correct_choice()
        self.write_to_file(event=event)
        self.left_option_displayed = False
        self.right_option_displayed = False

    def is_sub_experiment_done(self):
        return (len(self.stimulus_list) == 0)

    def get_file_data(self):
        if self.is_combination:
            return [("STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS", config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS),
                    ("overlap_time", "na"),
                    ("STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS", config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS)]
        else:
            return list()  # No additional file content

    def experiment_abbreviation(self):
        return config.PRETRAINING


class SimultaneousPresentation(Experiment):
    def __init__(self, is_combination):
        super().__init__(is_combination)
        self.options_displayed = False
        self.is_correct = None
        self.POT10 = [COLOR_A, COLOR_B] * 5
        self._create_new_sequences()

    def _create_new_sequences(self):
        self.stimuli_pot = list(self.POT10)  # Make a copy
        random.shuffle(self.stimuli_pot)

    def start_trial(self, event=None):
        self.clear()
        self.display_random_stimulus()
        job = self.root.after(config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS, self.display_options)
        self.current_after_jobs = [job]

    def display_random_stimulus(self):
        self.stimulus = self.stimuli_pot.pop()
        if len(self.stimuli_pot) == 0:
            self._create_new_sequences()
        self._set_entire_screen_color(self.stimulus)
        self.is_A = (self.stimulus == COLOR_A)

    def display_options(self):
        # self.clear()
        self._display_symbol(config.LEFT_OPTION, self.bottom_left_canvas)
        self._display_symbol(config.RIGHT_OPTION, self.top_right_canvas)
        self.options_displayed = True
        self.tic = time.time()

    def _left_clicked(self, event=None):
        if self.options_displayed:
            self.is_correct = self.is_A
            self._option_chosen(event)
            return "break"

    def _right_clicked(self, event=None):
        if self.options_displayed:
            self.is_correct = not self.is_A
            self._option_chosen(event)
            return "break"

    def is_sub_experiment_done(self):
        return (self.success_frequency >= 0.8)

    def _option_chosen(self, event):
        if self.is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.write_to_file(event=event)
        self.options_displayed = False

    def get_file_data(self):
        if self.is_combination:
            return [("STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS", config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS),
                    ("overlap_time", "na"),
                    ("STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS", config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS)]
        else:
            return [("STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS", config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS)]

    def experiment_abbreviation(self):
        return config.SIMULTANEOUS_PRESENTATION


class SimultaneousPresentationOverlap(Experiment):
    def __init__(self, is_combination=False, overlap_time=None):
        super().__init__(is_combination)
        if overlap_time is not None:
            self.overlap_time = overlap_time
        else:
            self.overlap_time = config.OVERLAP_TIME
        self.options_displayed = False
        self.is_correct = None
        self.POT10 = [COLOR_A, COLOR_B] * 5
        self._create_new_stimuli()

    def _create_new_stimuli(self):
        self.stimuli_pot = list(self.POT10)  # Make a copy
        random.shuffle(self.stimuli_pot)

    def start_trial(self, event=None):
        self.clear()
        self.display_random_stimulus()
        job1 = self.root.after(config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS, self.display_options)
        job2 = self.root.after(config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS + self.overlap_time,
                               self.remove_stimulus)
        self.current_after_jobs = [job1, job2]

    def remove_stimulus(self):
        self.set_background_color(BACKGROUND_COLOR)

    def display_random_stimulus(self):
        self.stimulus = self.stimuli_pot.pop()
        if len(self.stimuli_pot) == 0:
            self._create_new_stimuli()
        self._set_entire_screen_color(self.stimulus)
        self.is_A = (self.stimulus == COLOR_A)

    def display_options(self):
        # self.clear()
        self._display_symbol(config.LEFT_OPTION, self.bottom_left_canvas)
        self._display_symbol(config.RIGHT_OPTION, self.top_right_canvas)
        self.options_displayed = True
        self.tic = time.time()

    def _left_clicked(self, event=None):
        if self.options_displayed:
            self.is_correct = self.is_A
            self._option_chosen(event)
            return "break"

    def _right_clicked(self, event=None):
        if self.options_displayed:
            self.is_correct = not self.is_A
            self._option_chosen(event)
            return "break"

    def _option_chosen(self, event):
        if self.is_correct:
            self.correct_choice()
        else:
            self.incorrect_choice()
        self.write_to_file(event=event)
        self.options_displayed = False

    def is_sub_experiment_done(self):
        return (self.success_frequency >= 0.8)

    def get_file_data(self):
        if self.is_combination:
            return [("STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS", config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS),
                    ("overlap_time", self.overlap_time),
                    ("STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS", config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS)]
        else:
            return [("overlap_time", self.overlap_time),
                    ("STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS", config.STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS)]

    def experiment_abbreviation(self):
        return config.SIMULTANEOUS_PRESENTATION_OVERLAP


class SequenceDiscriminationProbe(Experiment):
    SHORT_AB = "shortAB"
    LONG_AB = "longAB"

    def __init__(self):
        super().__init__()
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
        self._display_symbol(config.LEFT_OPTION, self.bottom_left_canvas)
        self._display_symbol(config.RIGHT_OPTION, self.top_right_canvas)
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


class Combination1():
    def __init__(self):
        filename = self.result_filename()
        self.result_file = ResultFile(filename)

        sub_experiment_index = self.result_file.get_last_value('sub_experiment_index')
        if sub_experiment_index is None:
            sub_experiment_index = 1
        else:
            sub_experiment_index = int(sub_experiment_index)

        if sub_experiment_index == 1:
            exp1 = MatchingToSample(is_combination=True, responses_are_samples=True)
            exp1.sub_experiment_index = 1
            exp1.root.mainloop()

        if sub_experiment_index <= 2:
            exp2 = MatchingToSample(is_combination=True, responses_are_samples=False)
            exp2.sub_experiment_index = 2
            if sub_experiment_index < 2:
                exp2.set_window_geometry(exp1.window_geometry)
                exp2.space_pressed()
                exp2.finished_trial_cnt = exp1.finished_trial_cnt
            exp2.root.mainloop()

        if sub_experiment_index <= 3:
            exp3 = MatchingToSample(is_combination=True, responses_are_samples=False,
                                    use_screen1=True, use_screen2=True)
            exp3.sub_experiment_index = 3
            if sub_experiment_index < 3:
                exp3.space_pressed()
                exp3.finished_trial_cnt = exp2.finished_trial_cnt
            exp3.root.mainloop()

        if sub_experiment_index <= 4:
            exp4 = MatchingToSample(is_combination=True, responses_are_samples=False,
                                    use_screen1=False, use_screen2=True)
            exp4.sub_experiment_index = 4
            if sub_experiment_index < 4:
                exp4.space_pressed()
                exp4.finished_trial_cnt = exp3.finished_trial_cnt
            exp4.root.mainloop()

        # if sub_experiment_index <= 3:
        #     exp3 = SimultaneousPresentationOverlap(is_combination=True, overlap_time=1000)
        #     exp3.sub_experiment_index = 3
        #     if sub_experiment_index < 3:
        #         exp3.space_pressed()
        #         exp3.finished_trial_cnt = exp2.finished_trial_cnt
        #     exp3.root.mainloop()

        # if sub_experiment_index <= 4:
        #     exp4 = SimultaneousPresentationOverlap(is_combination=True, overlap_time=500)
        #     exp4.sub_experiment_index = 4
        #     if sub_experiment_index < 4:
        #         exp4.space_pressed()
        #         exp4.finished_trial_cnt = exp3.finished_trial_cnt
        #     exp4.root.mainloop()

        # if sub_experiment_index <= 5:
        #     exp5 = SimultaneousPresentationOverlap(is_combination=True, overlap_time=250)
        #     exp5.sub_experiment_index = 5
        #     if sub_experiment_index < 5:
        #         exp5.space_pressed()
        #         exp5.finished_trial_cnt = exp4.finished_trial_cnt
        #     exp5.root.mainloop()

        # if sub_experiment_index <= 6:
        #     exp6 = SimultaneousPresentationOverlap(is_combination=True, overlap_time=0)
        #     exp6.sub_experiment_index = 6
        #     if sub_experiment_index < 6:
        #         exp6.space_pressed()
        #         exp6.finished_trial_cnt = exp5.finished_trial_cnt
        #     exp6.root.mainloop()

    @staticmethod
    def result_filename():
        experiment = Combination1.experiment_abbreviation()
        subject = config.SUBJECT_TAG.lower()
        return subject + "_" + experiment + ".csv"

    @staticmethod
    def experiment_abbreviation():
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
    if config.EXPERIMENT == config.COMBINATION1:
        Combination1()
    else:
        e = None
        if config.EXPERIMENT == config.MATCHING_TO_SAMPLE_SAMPLE:
            e = MatchingToSample(is_combination=False, responses_are_samples=True)
        elif config.EXPERIMENT == config.MATCHING_TO_SAMPLE_SYMBOLS:
            e = MatchingToSample(is_combination=False, responses_are_samples=False,
                                 use_screen1=False, use_screen2=True)
        # elif config.EXPERIMENT == config.SIMULTANEOUS_PRESENTATION:
        #     e = SimultaneousPresentation()
        # elif config.EXPERIMENT == config.SIMULTANEOUS_PRESENTATION_OVERLAP:
        #     e = SimultaneousPresentationOverlap()
        # elif config.EXPERIMENT == config.SEQUENCE_DISCRIMINATION_PROBE:
        #     e = SequenceDiscriminationProbe()
        else:
            print("Error: Undefined experiment name '" + config.EXPERIMENT + "'.")
        if e:
            e.root.mainloop()
