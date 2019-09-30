# These names are used in the name of the result file.
EXP1a = "11"
EXP1b = "12"
EXP2 = "2"
EXP3a = "31"
EXP3b = "32"
EXP3c = "33"
EXP4 = "4"
EXP5 = "5"
EXP6 = "6"
EXP7 = "7"
EXP8 = "8"
COMBINATION1 = "Combination1"
COMBINATION2 = "Combination2"
SEQUENCE_DISCRIMINATION_PROBE = "SequenceDiscriminationProbe"

# The experiment to run. Remove the "#" before the one to run.
# EXPERIMENT = EXP1a
# EXPERIMENT = EXP1b
# EXPERIMENT = EXP2
# EXPERIMENT = EXP3a
# EXPERIMENT = EXP3b
# EXPERIMENT = EXP3c
# EXPERIMENT = EXP4
# EXPERIMENT = EXP5
# EXPERIMENT = EXP6
# EXPERIMENT = EXP7
# EXPERIMENT = EXP8
# EXPERIMENT = COMBINATION1
# EXPERIMENT = COMBINATION2
EXPERIMENT = SEQUENCE_DISCRIMINATION_PROBE

# The subject exposed to the experiment. Used in the name of the result file and
# as the "subject" column in the result file
SUBJECT_TAG = "johan"


####################
# General settings #
####################

# Initial visibility of mouse pointer (False/True). Can be toggled with <F10>.
HIDE_MOUSE_POINTER = False

# The number of trials before the start screen appears automatically
TRIALS_BEFORE_PAUSE = 60

# The start screen
START_SCREEN_COLOR_RGB = (255, 192, 203)

# The background screen color in red, green, blue (each ranging from 0 to 255)
BACKGROUND_COLOR_RGB = (0, 0, 0)

# The color of the Next button
NEXT_BUTTON_COLOR_RGB = (255, 255, 255)

# The color of the "blackout" screen after incorrect answer
BLACKOUT_COLOR_RGB = (100, 100, 100)

# Width (and height) of the Next button, as a fraction of H/3
NEXT_BUTTON_WIDTH = 0.65

# The time (in milliseconds) for the black screen after incorrect answer
BLACKOUT_TIME = 5000

# The delay (in milliseconds) after correct answer, before the next symbol is displayed
DELAY_AFTER_REWARD = 1000

# The name of the sound file to play if correct. File must be in the same directory as this file.
SOUND_CORRECT = 'correct.wav'

# The name of the sound file to play if incorrect. File must be in the same directory as this file.
SOUND_INCORRECT = 'incorrect.wav'

# The color of stimulus A
COLOR_A_RGB = (0, 0, 255)

# The color of stimulus B
COLOR_B_RGB = (255, 255, 0)

# The symbol to the left to press after the sequence presentation, which is correct choice after
# AB
LEFT_OPTION = 'horizontal_button.gif'

# The symbol to the right to press after the sequence presentation, which is correct choice after
# AA, BB and BA
RIGHT_OPTION = 'vertical_button.gif'

# The width (and height) of the stimulus canvas on the second screen, as a fraction of screen
# height
SCREEN2_STIMULUS_WIDTH = 0.5

# The width of the (square) sample (and the response buttons in MTS_SA and
# SINGLE_STIMULUS_DISCRIMINATION)
SYMBOL_WIDTH = 0.75

# Whether or not the yellow response should be to the 'left' or to the 'right'
YELLOW_POS = 'right'


###############################
# Matching to sample settings #
###############################

# The time (in milliseconds) that the symbol is displayed by itself in MTS
# before the options appear
SYMBOL_SHOW_TIME_MTS = 1000


##################################
# Single stimulus discrimination #
##################################

# The time (in milliseconds) that the stimulus is presented
STIMULUS_TIME = 2000

# The time (in ms) of delay between the stimulus disappears until the response buttons appear
# Note: Only used when EXPERIMENT = SINGLE_STIMULUS_DISCRIMINATION or
# SEQUENCE_DISCRIMINATION_PROBE, not in COMBINATION1
DELAY = 500


#################################
# Sequence discrimination probe #
#################################

# Every n:th trial is a probe trial where n = PROBE_TRIAL_INTERVAL
PROBE_TRIAL_INTERVAL = 5

# The time to display A when AB is displayed
LONG_A_TIME = 4000

# The time to display A when aB is displayed
SHORT_A_TIME = 1000

# The time to display B when aB or AB is displayed
B_TIME = 2000

# The inter-stimulus time for probes
INTER_STIMULUS_TIME = 300

# The time (in milliseconds) that the stimulus is presented, before the response buttons appear
STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS = 2000
