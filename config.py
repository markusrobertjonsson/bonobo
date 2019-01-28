# These abbreviations are used in the name of the result file.
NEXT_BUTTON_TRAINING = "NBT"
GO_BUTTON_TRAINING = "GBT"
MATCHING_TO_SAMPLE = "MTS"
ZERO_DELAY_MATCHING_TO_SAMPLE = "ZDMTS"
DELAYED_MATCHING_TO_SAMPLE = "DMTS"
SEQUENCE_DISCRIMINATION = "SeqDis"
SINGLE_STIMULUS_DISCRIMINATION = "SSDis"

# The experiment to run. Remove the "#" before the one to run.
# EXPERIMENT = NEXT_BUTTON_TRAINING
# EXPERIMENT = MATCHING_TO_SAMPLE
# EXPERIMENT = ZERO_DELAY_MATCHING_TO_SAMPLE
# EXPERIMENT = DELAYED_MATCHING_TO_SAMPLE
# EXPERIMENT = GO_BUTTON_TRAINING
EXPERIMENT = SINGLE_STIMULUS_DISCRIMINATION
# EXPERIMENT = SEQUENCE_DISCRIMINATION

# The subject exposed to the experiment. Used in the name of the result file and
# as the "subject" column in the result file
SUBJECT_TAG = "kanzi"


####################
# General settings #
####################

# The background screen color in reg, green, blue (each ranging from 0 to 255)
BACKGROUND_COLOR_RGB = (0, 0, 0)
# BACKGROUND_COLOR_RGB = (64, 204, 255)

# The color of the separator
SEPARATOR_COLOR_RGB = (255, 255, 255)

# The color of the Next button
NEXT_BUTTON_COLOR_RGB = (255, 255, 255)

# The color of the "blackout" screen
BLACKOUT_COLOR_RGB = (100, 100, 100)

# Width (and height) of colored square, as a fraction of H/3
SYMBOL_WIDTH = 0.75

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


#######################################
# Delayed matching to sample settings #
#######################################

# The symbols to use. Shapes to choose from:
# 'redtriangle', 'bluecircle', 'greensquare', 'bluetriangle', 'greencircle', 'redsquare',
# 'greentriangle', 'redcircle', 'bluesquare'
SYMBOLS_MTS = ['redsquare', 'greensquare']

# The nonzero delay times (in milliseconds) to use. It is chosen randomly in every other
# trial (and every other is 0). Use [0] for no delay.
DELAY_TIMES = [5000, 10000, 20000, 40000, 60000]  # Use
# DELAY_TIMES = [1000, 2000, 4000, 6000]

# The time (in milliseconds) that the symbol is displayed
SYMBOL_SHOW_TIME = 2000


###################################
# General discrimination settings #
###################################

# The time (in milliseconds) that each symbol in the sequence is displayed
STIMULUS_TIME = 2000

# If button is not pressed after a sequence display, the time to wait
# before the next sequence is displayed
GO_BUTTON_DURATION = 2000

# The time between the last stimulus and the display of the go button
RETENTION_TIME = 0

# Width (and height) of the button, as a fraction of H/2
GO_BUTTON_WIDTH = 0.65

# Color of the go button
GO_BUTTON_COLOR_RGB = (255, 255, 255)


####################################
# Sequence discrimination settings #
####################################

# The two symbols in the sequence
SYMBOL1 = 'redsquare'
SYMBOL2 = 'greensquare'

# The first symbol in the rewarding sequence
REWARDING_SEQUENCE = (SYMBOL1, SYMBOL2)

# The inter-stimulus time
INTER_STIMULUS_TIME = 100


###########################################
# Single stimulus discrimination settings #
###########################################
SYMBOLS_SS = ['redsquare', 'greensquare']

REWARDING_STIMULUS = 'redsquare'
