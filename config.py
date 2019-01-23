####################
# General settings #
####################

# The background screen color in reg, green, blue (each ranging from 0 to 255)
# BACKGROUND_COLOR_RGB = (0, 0, 0)
BACKGROUND_COLOR_RGB = (64, 204, 255)

# The color of the separator
SEPARATOR_COLOR_RGB = (255, 255, 255)

# The color of the Next button
NEXT_BUTTON_COLOR_RGB = (200, 200, 100)

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


######################################
# Delayed matched to sample settings #
######################################

# The symbols to use
SYMBOLS = ['redsquare', 'greensquare']
# SYMBOLS = ['redtriangle', 'bluecircle', 'greensquare',
#            'bluetriangle', 'greencircle', 'redsquare',
#            'greentriangle', 'redcircle', 'bluesquare']

# The nonzero delay times (in milliseconds) to use. It is chosen randomly in every other trial (every other is 0).
# Use [0] for no delay
DELAY_TIMES = [5000, 10000, 20000, 40000, 60000]
# DELAY_TIMES = [1000, 2000, 4000, 6000]

# The time (in milliseconds) that the symbol is displayed
SYMBOL_SHOW_TIME = 2000


####################################
# Sequence discrimination settings #
####################################

# The two symbols in the sequence
SYMBOL1 = 'redsquare'
SYMBOL2 = 'greensquare'

# The first symbol in the rewarding sequence
REWARDING_SEQUENCE = (SYMBOL1, SYMBOL2)

# The time (in milliseconds) that each symbol in the sequence is displayed
STIMULUS_TIME = 2000

# The inter-stimulus time
INTER_STIMULUS_TIME = 100

# If button is not pressed after a sequence display, the time to wait
# before the next sequence is displayed
GO_BUTTON_DURATION = 2000

# The time between the last stimulus and the display of the go button
RETENTION_TIME = 0

# Width (and height) of the button, as a fraction of H/2
GO_BUTTON_WIDTH = 0.6

# Color of the go button
GO_BUTTON_COLOR_RGB = (200, 200, 100)

assert(NEXT_BUTTON_WIDTH >= GO_BUTTON_WIDTH), "NEXT_BUTTON_WIDTH must be >= GO_BUTTON_WIDTH in config.py."


###########################################
# Single stimulus discrimination settings #
###########################################
SYMBOLS = ['redsquare', 'greensquare']

REWARDING_STIMULUS = 'redsquare'
