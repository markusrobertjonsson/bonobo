# These abbreviations are used in the name of the result file.
SSDIS_PRETRAININGA_GO = "SSDisPreGo"
SSDIS_PRETRAININGA_A_AND_GO = "SSDisPreAandGo"
SSDIS_PRETRAININGA_A_THEN_GO = "SSDisPreAthenGo"
SSDIS_PRETRAININGB = "SSDisPreB"
SSDIS_PRETRAININGB_B_AND_GO = "SSDisPreBandGo"
SSDIS_PRETRAININGB_B_THEN_GO = "SSDisPreBthenGo"
SINGLE_STIMULUS_DISCRIMINATION_OLD = "SSDis_old"
SEQUENCE_DISCRIMINATION = "SeqDis"
SEQUENCE_DISCRIMINATION_SOUND = "SeqDisSound"
SINGLE_STIMULUS_DISCRIMINATION = "SSDis"
SINGLE_STIMULUS_DISCRIMINATION_SOUND = "SSDisSound"
SINGLE_STIMULUS_DISCRIMINATION_SYMBOL = "SSDisSymb"
SINGLE_STIMULUS_VS_SEQ = "SSvsSeq"

# The experiment to run. Remove the "#" before the one to run.
# EXPERIMENT = SSDIS_PRETRAININGA_GO
# EXPERIMENT = SSDIS_PRETRAININGA_A_AND_GO
# EXPERIMENT = SSDIS_PRETRAININGA_A_THEN_GO
# EXPERIMENT = SSDIS_PRETRAININGB
# EXPERIMENT = SSDIS_PRETRAININGB_B_AND_GO
# EXPERIMENT = SSDIS_PRETRAININGB_B_THEN_GO
# EXPERIMENT = SEQUENCE_DISCRIMINATION
# EXPERIMENT = SEQUENCE_DISCRIMINATION_SOUND
# EXPERIMENT = SINGLE_STIMULUS_DISCRIMINATION
# EXPERIMENT = SINGLE_STIMULUS_DISCRIMINATION_SOUND
EXPERIMENT = SINGLE_STIMULUS_DISCRIMINATION_SYMBOL
# EXPERIMENT = SINGLE_STIMULUS_VS_SEQ

# The subject exposed to the experiment. Used in the name of the result file and
# as the "subject" column in the result file
SUBJECT_TAG = "johan"


####################
# General settings #
####################

# Whether or not to use corrections_trials
USE_CORRECTION_TRIALS = "off"

# Response buttons placement: "on" for diagonal placement, "off" for next to each other
RESPONSE_BUTTONS_DIAGONAL = "on"

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

# The duration of the go-button for a go-stimulus/sequence
GO_BUTTON_DURATION_GO = 3000

# The duration of the go-button for a go-stimulus/sequence
GO_BUTTON_DURATION_NOGO = 1000

# Width (and height) of the button, as a fraction of H/3
GO_BUTTON_WIDTH = 0.5

# Color of the go button
GO_BUTTON_COLOR_RGB = (0, 0, 0)

# The color of the "blackout" screen
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


###################################
# General discrimination settings #
###################################

# The time (in milliseconds) that the stimulus (each stimulus in sequences) is presented
STIMULUS_TIME = 1500


###########################################
# Single stimulus discrimination settings #
###########################################

# Stimulus symbols
SS_STIMULUS_A = 'circle.gif'
SS_STIMULUS_B = 'star.gif'

SS_SOUND_A = 'Alesis-Fusion-Nylon-String-Guitar-C4.wav'
SS_SOUND_B = 'Crash-Cymbal-1.wav'

SS_COLOR_A_RGB = (255, 88, 0)
SS_COLOR_B_RGB = (0, 0, 255)

SS_STIMULUS_TIME = 1000


#########################################
# Single stimulus vs. sequence settings #
#########################################

LONG_A_TIME = 4000
SHORT_A_TIME = 200
B_TIME = 1000


####################################
# Sequence discrimination settings #
####################################

# The two colors in the sequence
COLOR_A_RGB = (0, 0, 255)
COLOR_B_RGB = (255, 255, 0)

SOUND_A = '1980s-Casio-Clarinet-C5.wav'
SOUND_B = 'Crash-Cymbal-1.wav'

# The inter-stimulus time
INTER_STIMULUS_TIME = 300

# The symbol to the left to press after the sequence presentation, which is correct choice after
# AB
LEFT_OPTION = 'horizontal_lines.gif'

# The symbol to the right to press after the sequence presentation, which is correct choice after
# AA, BB and BA
RIGHT_OPTION = 'vertical_lines.gif'
