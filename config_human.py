# The subject exposed to the experiment. Used in the name of the result file and
# as the "subject" column in the result file
SUBJECT_TAG = "johan"


####################
# General settings #
####################

# The instruction text to display in the beginning
INSTRUCTION_TEXT = """Welcome to this experiment!

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris accumsan aliquet erat. Proin id
metus pretium, pharetra ex sed, fringilla velit. Morbi mattis lectus vitae nunc dapibus, vel
lobortis justo tincidunt. Curabitur dictum nisl in placerat elementum. Aenean at dictum enim.
Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Aliquam
bibendum ligula id diam mattis, at aliquet lectus faucibus. Mauris euismod metus dui, sit amet
aliquet erat feugiat vitae. Aliquam faucibus nulla id neque bibendum ornare pharetra sed leo.

Nullam condimentum aliquam purus sit amet elementum. Suspendisse vestibulum hendrerit erat.
Nulla semper at risus rutrum vestibulum. Vestibulum sodales lorem nec nulla faucibus suscipit.
Nulla dictum ut tellus id pretium. Suspendisse auctor tempus nisl vitae rhoncus. Mauris malesuada
volutpat eros eget tincidunt. Cras at rhoncus metus. Vestibulum ante ipsum primis in faucibus orci
luctus et ultrices posuere cubilia Curae; Aliquam lobortis est sit amet ornare maximus.
Aliquam lacinia erat sit amet nisl efficitur suscipit.

Sed et neque cursus, auctor massa in, dictum tellus. Aenean ullamcorper, ligula vitae semper
hendrerit, turpis erat ultricies dui, a pellentesque nisl eros in leo. Donec euismod viverra enim,
ut mattis justo facilisis sed. Vivamus sapien ligula, rutrum a magna in, placerat scelerisque
felis. Donec porta tristique orci eu feugiat. Cras ut pharetra nunc. Maecenas accumsan neque vel
suscipit viverra.

Sed interdum ante nulla, quis porta libero facilisis a. Nullam nisl velit, auctor eget ex sit
amet, blandit maximus neque. Phasellus pretium venenatis mauris, eu lacinia purus faucibus non.
Pellentesque elementum turpis ut tellus hendrerit, mattis ultricies urna finibus. Vivamus nec
elementum purus. Vestibulum mollis varius dolor vel tincidunt. Vestibulum hendrerit tristique
lacinia. Quisque vitae rhoncus diam. Duis convallis imperdiet urna sit amet vulputate. Nam nisl
tellus, posuere interdum risus ac, tempor sodales dolor. Praesent ut risus velit.

Press the space bar to start.
"""

FINISH_TEXT = """Thank you for participating in this experiment!

Phasellus viverra sollicitudin dolor in blandit. Donec dapibus velit magna, in vehicula diam
mattis eget. Aenean purus metus, rhoncus vitae feugiat non, mollis et massa. Nam interdum lacinia
tempus. Aenean suscipit mauris a risus dictum suscipit. Praesent placerat, arcu eu rhoncus
interdum, nisi arcu semper risus, nec rutrum sem eros eget magna. Orci varius natoque penatibus et
magnis dis parturient montes, nascetur ridiculus mus. Vestibulum lacinia vel tellus ac dictum.
Integer rutrum scelerisque urna, in mollis magna imperdiet sed. Praesent non bibendum erat.
Quisque id lorem id massa rutrum hendrerit dapibus ac ipsum. Etiam vitae tempus lacus. Sed
sagittis dui ipsum, eget aliquam sapien congue ut. Proin tincidunt varius enim in laoreet. Ut odio
ex, rutrum id ornare ut, accumsan sit amet ex. Nam finibus tincidunt mauris sit amet consectetur.
"""

# The font and font size of the INSTRUCTION_TEXT and FINISH_TEXT
TEXTS_FONT = ("Helvetica", 15)

# Initial visibility of mouse pointer (False/True). Can be toggled with <F10>.
HIDE_MOUSE_POINTER = False

# The start (and pause) screen color
START_SCREEN_COLOR_RGB = (255, 192, 203)  # Pink

# The time (in milliseconds) for the black screen after incorrect answer
BLACKOUT_TIME = 3000

# The delay (in milliseconds) after correct answer, before the next stimulus is displayed
DELAY_AFTER_REWARD = 1000


#################################
# Sequence discrimination probe #
#################################

SDP = {
    # The time to display the single stimuli
    "SINGLE_STIMULUS_TIME": 1500,

    # Every n:th trial is a probe trial where n = PROBE_TRIAL_INTERVAL
    "PROBE_TRIAL_INTERVAL": 10,

    # The time to display A when AB is displayed
    "LONG_A_TIME": 4000,

    # The time to display A when aB is displayed
    "SHORT_A_TIME": 1000,

    # The time to display B when aB or AB is displayed
    "B_TIME": 2000,

    # The inter-stimulus time for probes
    "INTER_STIMULUS_TIME": 300,

    # The time (in ms) of delay between the last stimulus disappears until the response buttons appear
    "DELAY": 500
}
