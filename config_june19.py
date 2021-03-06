# These names are used in the name of the result file.
PRETRAINING = "Pretraining"
SIMULTANEOUS_PRESENTATION = "SimulataneousPresentation"
SIMULTANEOUS_PRESENTATION_OVERLAP = "SimulataneousPresentationOverlap"
SEQUENCE_DISCRIMINATION_PROBE = "SequenceDiscriminationProbe"
COMBINATION1 = "CombinationAug2019"

# The experiment to run. Remove the "#" before the one to run.
# EXPERIMENT = PRETRAINING
# EXPERIMENT = SIMULTANEOUS_PRESENTATION
# EXPERIMENT = SIMULTANEOUS_PRESENTATION_OVERLAP
# EXPERIMENT = SEQUENCE_DISCRIMINATION_PROBE
EXPERIMENT = COMBINATION1

# The subject exposed to the experiment. Used in the name of the result file and
# as the "subject" column in the result file
SUBJECT_TAG = "markus"


####################
# General settings #
####################

# Set to False or True
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
BLACKOUT_TIME = 3000

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

# The time (in milliseconds) for the black screen after undesired click
UNDESIRED_CLICK_BLACKOUT_TIME = 3000

# The color of the "blackout" screen after undesired click
UNDESIRED_CLICK_BLACKOUT_COLOR_RGB = (100, 100, 100)


#########################################
# Simultaneous presentation and overlap #
#########################################

# The time (in milliseconds) that the stimulus is presented, before the response buttons appear
STIMULUS_TIME_BEFORE_RESPONSE_BUTTONS = 2000

# The time (in ms) that both stimulus and response buttons are diaplyed together
OVERLAP_TIME = 250


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

# The inter-stimulus time
INTER_STIMULUS_TIME = 300
