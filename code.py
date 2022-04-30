"""
<add a linnk to github>
<add a link to printables>
<add other required doc>

"""

import time
import board
import analogio
import usb_midi
import adafruit_ssd1306
import busio as io
import digitalio
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

# *~*~*~*~*~*~*~* Run Options ~*~*~*~*~*~*~*~
SLEEPY_TIME = 0.005  # How long to sleep
REPEAT_NUM = 8       # Lower = faster repeats. This affects ALL repeats.
VOLUME_MINUS = 2     # Higher = reduce velume more per repeat
SYNC = False         # SYNC settings for MIDI repeats
DEFAULT_SCRN = 0     # idx of the screen to boot on
MASTER_VEL = 120     # Starting velocity of note
MASTER_FACTOR = 30   # Midi falloff factor. Higher = quicker vol decrease
MIN_VOL_CHG = 3      # Minimum the volume can change between 2 notes in falloff mode
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~

# Display constants
TEXT_PAD = 4
TOP_SEC_HT = 48
CHAR_WIDTH = 3      # How many pixels wide a character is, avg
INVERTED = False    # Should pixel colors be inverted?
SCREEN_W = 128
SCREEN_H = 64

# Other value inits
time_prev = time.monotonic_ns()
time_now = time_prev
time_elapsed_sec = 0
time_elapsed_total = 0
send_new_val = False
bank = 3
FALLOFF_FACTOR = 0
REPEAT_DURATION = 1000
NUM_RELEASE_TO_IGNORE = 0
currentScreen_idx = DEFAULT_SCRN
POT_CHG_THRESH = 400           # Pot has to change by this much to be considered changed. Raw value ranges from ~ 0 - 69,000
POT_CHG_THRESH_BIG = 1000      # Pot has to change by this much to be considered changed BIGTIME. Raw value ranges from ~ 0 - 69,000
curr_repeat_spd_idx = 1          # Start repeats on the medium setting
cur_repeat_spd = REPEAT_NUM
ignore_note = False            # Set this to true to ignore a note
new_presses = []               # Use this to track new BUTTONS that were pressed in this loop. For FX
set_press = False
title_bar_text = ""
bpm = 120                         # User can set this to affect repeat timing
internal_latency_secs = 0.0165    # Amt of time it takes to do a full loop in seconds
has_interval = False

# Some variables to use with perf testing
util_perftimerstart = 0
util_perftimerend = 0
util_activetiming = False
util_perf_loops = 0
util_perftimerelapsedsecs = 0


# 0 - general setup
MIDI = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
I2C = io.I2C(board.GP7, board.GP6)
OLED = adafruit_ssd1306.SSD1306_I2C(SCREEN_W, SCREEN_H, I2C, addr=0x3C)

# 1 - Set up the BUTTONS. Each is the [button object, value now, value before, previous velume]
BUTTONS = [

digitalio.DigitalInOut(board.GP14),    # Bottom Left Button
digitalio.DigitalInOut(board.GP15),
digitalio.DigitalInOut(board.GP16),
digitalio.DigitalInOut(board.GP17),    # Bottom Right Button
digitalio.DigitalInOut(board.GP10),
digitalio.DigitalInOut(board.GP11),
digitalio.DigitalInOut(board.GP12),
digitalio.DigitalInOut(board.GP13),
digitalio.DigitalInOut(board.GP0),
digitalio.DigitalInOut(board.GP1),
digitalio.DigitalInOut(board.GP8),
digitalio.DigitalInOut(board.GP9),
digitalio.DigitalInOut(board.GP2),
digitalio.DigitalInOut(board.GP3),
digitalio.DigitalInOut(board.GP4),
digitalio.DigitalInOut(board.GP5)    # Top Right Button

]

CONTROL_BUTTONS = [                                       # use these to change the bank

[digitalio.DigitalInOut(board.GP20), False],
[digitalio.DigitalInOut(board.GP21), False]

]

for button in BUTTONS:
    button.switch_to_input(pull=digitalio.Pull.DOWN)

for button in CONTROL_BUTTONS:
    button[0].switch_to_input(pull=digitalio.Pull.DOWN)

# 2 - Set up the MIDI note arrays. Each array needs to be the same length.
midi_banks = [

[1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,3],
[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
[20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35],
[36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51],                  # bank 0 (default)
[52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67],                  # bank 1
[68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83],                  # bank 2
[84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99],
[100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115],
[116,117,118,119,120,121,122,123,124,125,126,127,127,127,127,127]

]

# Keep this in SYNC with MIDI banks
MIDI_BANKS_DEFAULT = [

[1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,3],
[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
[20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35],
[36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51],                  # bank 0 (default)
[52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67],                  # bank 1
[68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83],                  # bank 2
[84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99],
[100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115],
[116,117,118,119,120,121,122,123,124,125,126,127,127,127,127,127]

]

midi_bank_temp = []

# 3 - Set up the POTS
POT_1 = analogio.AnalogIn(board.GP26)
POT_2 = analogio.AnalogIn(board.GP27)
POT_3 = analogio.AnalogIn(board.GP28)
POTS = [POT_1, POT_2, POT_3]
pots_raw = [[300, 300], [300, 300], [300, 300]]
POTS_MIDI = [[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0],]      # Each item is [MIDI now, MIDI before, haschanged]

# 4 - Set up the screens
REPEAT_SPDS_TEXT = ["Low", "Med", "High", "Insane"]
SCREENS_LIST = [(1, "B A N K  S E L E C T", "Current bank"), (2, "R P T  M O D E", "Mode"), (3, "R P T  S P E E D","Speed"), (4, "M I D I  A S S I G N", "New Value"),(5, "B P M  or  N A H", "BPM") ]

# Set text, font, and color
# Refff https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html

#*************************************************
#************** DEFINE SOME FUNCTIONS ************
#*************************************************

# Lez use a class this time for the BUTTONS...
class Button:

    def __init__(self, gpioObject, idx):
        self.gpioObject = gpioObject
        self.valueBefore = False
        self.timeElapsed = 0
        self.velocity_now = 120
        self.velocityBefore = 120
        self.sendNewNote = False
        self.prevTime = time.monotonic_ns()
        self.lockHold = False
        self.press = False
        self.idx = idx

    def get_current_btn_value(self):
        return self.gpioObject.value

# Class for each menu screen
class menu_Screen:

    def __init__(self, screenNumber, screenTitle, main_text):
        self.screenNumber = screenNumber
        self.screenTitle = screenTitle
        self.main_text = main_text

    def display_screen(self, setting = "", extra = "", total_refresh = "True"):

        global title_bar_text
        global INVERTED

        if setting == "":
            if currentScreen_idx == 0:
                setting = str(bank)
            elif currentScreen_idx == 1:
                if SYNC:
                    setting = "SYNC"
                else:
                    setting = "Free"

            elif currentScreen_idx == 2:
                setting = REPEAT_SPDS_TEXT[curr_repeat_spd_idx]

        screen_num_text = str(self.screenNumber) + "/" + str(len(SCREENS_LIST))
        main_text = self.main_text
        title_bar_text = self.screenTitle
        value_text = setting
        startw = round((SCREEN_W/2) - (CHAR_WIDTH * len(main_text)))                # where should we start drawing the main text? The middle.
        starth = round(SCREEN_H/2) - 5
        startw_value = round((SCREEN_W/2) - (CHAR_WIDTH * len(value_text)))


        # Init screen, Draw outlines
        if total_refresh:
            OLED.fill(0)
            OLED.rect(0, 0, SCREEN_W, SCREEN_H - TOP_SEC_HT, 1)             # Top section Outline
            OLED.rect(0, SCREEN_H - TOP_SEC_HT, SCREEN_W, SCREEN_H, 1)      # Bottom Section Outline
            OLED.text(title_bar_text, TEXT_PAD, TEXT_PAD, 1)                # Show the title bar text (yellow section)
            OLED.text(screen_num_text, TEXT_PAD, SCREEN_H - TEXT_PAD*3, 1)  # Screen num. ex. 1/4

            # Special handling for MIDI assignment mode
            if currentScreen_idx == 3:
                OLED.text(main_text + ":", TEXT_PAD, starth, 1)              # Main description
                OLED.text(value_text, round(SCREEN_W / 2) + 7, starth, 1)    # Show the value
                OLED.text("Orig Value:",TEXT_PAD, starth + 10, 1)            # Second line of data for the MIDI assn screen
                OLED.text(extra, round(SCREEN_W / 2) + 7, starth + 10, 1)    # Show the orig value
                INVERTED = True
                OLED.invert(True)

            else:
                if INVERTED:
                    INVERTED = False
                    OLED.invert(False)
                OLED.text(main_text, startw, starth, 1)                  # Main description
                OLED.text(value_text, startw_value, starth + 10,1)       # Show the value
        else:
            if currentScreen_idx == 3:

                OLED.fill_rect(round(SCREEN_W / 2) + 7, starth, CHAR_WIDTH * 6,18, 0)                  # Clear the value pixels
                OLED.text(value_text, round(SCREEN_W / 2) + 7, starth, 1)       # Show the value
                OLED.text(extra, round(SCREEN_W / 2) + 7, starth + 10, 1)      # Show the orig value

            else:
                OLED.fill_rect(startw_value - 5, starth + 10, CHAR_WIDTH * len(value_text) * 4,CHAR_WIDTH * 3, 0)                  # Clear the value pixels
                OLED.text(value_text, startw_value, starth + 10,1)       # Show the value


        OLED.show()

    def next_screen(self):                                 # update some global vars for the screen we are on
        global currentScreen_idx
        global currentScreen

        if currentScreen_idx > (len(SCREENS_LIST) - 2):
            currentScreen_idx = 0
        else:
            currentScreen_idx += 1

        currentScreen = menuScreens[currentScreen_idx]


def midi_mapper(value):
    """Maps values from 0-65520 (raw pot value) to 0-127 (MIDI)"""

    return round(127 * (value / (65520 - 200)))


def perf_timer(loops = 1):
    """
    performance timer function to help with testing

    Args:
        loops (int, optional): number of loops to measure. Defaults to 1.
    """
    global perfTimerElapsedms_util
    global util_perf_loops
    global util_activetiming
    global util_perftimerstart
    global util_perftimerend

    if not util_perftimerstart:
        util_perftimerstart = time.monotonic_ns()

    if util_perf_loops >= loops:                                # Already started the timing so this is the end
        util_perftimerend = time.monotonic_ns()
        perfTimerElapsedms_util = (util_perftimerend - util_perftimerstart) / 1000000000 * 1000
        print(f"Perf Timer (ms): {perfTimerElapsedms_util}")
        util_perftimerstart = 0
        perfTimerElapsedms_util = 0 

    elif util_activetiming:                                           # First call to the function.. note the start time
        util_perf_loops += 1
    
    util_activetiming = not util_activetiming


def get_pot_values():
    """gets current pot values"""

    for idx, pot in enumerate(POTS):

        value_now = pot.value

        POTS_MIDI[idx][1] = POTS_MIDI[idx][0]              # Save off the current value as the previous value
        POTS_MIDI[idx][0] = midi_mapper(value_now)          # Get the new current value

        pots_raw[idx][1] = pots_raw[idx][0]
        pots_raw[idx][0] = value_now

        # -- Use the raw data to determine if the pot changed.
        # -- Store it in MIDI array since that's the useful one
        POTS_MIDI[idx][2] = (abs(pots_raw[idx][0] - pots_raw[idx][1]) > POT_CHG_THRESH)
        POTS_MIDI[idx][3] = (abs(pots_raw[idx][0] - pots_raw[idx][1]) > POT_CHG_THRESH_BIG)

def calc_bpm():
    """

    Returns number of seconds between notes, depending on BPM, 
    accounting for internal latency (processing time) to do a loop.

    Returns:
        Float: Seconds      
    """

    midi_val = POTS_MIDI[2][0]
    whole_note_secs = 1/ (bpm / 60)
    half_note_secs = whole_note_secs / 2
    quarter_note_secs = half_note_secs / 2
    eigth_note_secs = quarter_note_secs / 2
    sixteenth_note_secs = eigth_note_secs / 2

    if midi_val < 25:
        return whole_note_secs - internal_latency_secs

    if midi_val < 50:
        return half_note_secs - internal_latency_secs

    if midi_val < 75:
        return quarter_note_secs  - internal_latency_secs

    if midi_val < 100:
        return eigth_note_secs - internal_latency_secs

    return sixteenth_note_secs - internal_latency_secs


# Update the interval for repeats. Only if pot 3 has a value > 3 and has changed.
def update_repeat_interval(reset = False):
    """Update the interval for repeats. Only if pot 3 has a value > 3 and has changed."""

    global has_interval
    global REPEAT_DURATION

    if POTS_MIDI[2][0] > 3:

        has_interval = 1

        if POTS_MIDI[2][2] or reset:
            if bpm:
                REPEAT_DURATION = calc_bpm()                      # Using BPM. Get a value based on current BPM
                print(REPEAT_DURATION)

            else:
                REPEAT_DURATION = cur_repeat_spd / POTS_MIDI[2][0]  # Not using BPM.. deal wit it

    else:
        has_interval = 0

def update_global_times():
    """Helper function to keep track of times"""

    # Keep track of time for the FX
    global time_prev
    global time_now
    global time_elapsed_sec
    global time_elapsed_total
    global send_new_val


    time_prev = time_now
    time_now = time.monotonic_ns()
    time_elapsed_sec = (time_now - time_prev) / 1000000000
    time_elapsed_total = time_elapsed_total + time_elapsed_sec

    # Lets go ahead and determine if we should send a new value
    send_new_val = False
    update_repeat_interval()

    if time_elapsed_total > REPEAT_DURATION and has_interval:
        send_new_val = True
        time_elapsed_total = 0

    else:
        pass


def update_velocity(button):
    """sets note velocity for a button

    Args:
        button (button object): button object

    Returns:
        float: velocity value
    """

    velocity_now = round(button.velocityBefore - MIN_VOL_CHG - (FALLOFF_FACTOR * MASTER_FACTOR))
    velocity_now = max(velocity_now, 0)

    return velocity_now


def falloff_factor_settings():
    """Get fallout factor settings based on pot val"""

    global FALLOFF_FACTOR

    if has_interval:                                 # Skip this if we aren't doing repeats
        if POTS_MIDI[1][0] > 3:                      # Make sure the pot is "on"
            FALLOFF_FACTOR = POTS_MIDI[1][0] / 127    # Make a number between 0 and 1
        else:
            FALLOFF_FACTOR = 0                       # No falloff.. set to 0


def clear_all_holds():
    """kills all midi values"""

    for button in BUTTONS:
        button.lockHold = False
        MIDI.send(NoteOff(bankNow[button.idx], 0))

def clear_bank_notes():
    """send midi off message for all notes in current bank"""

    for note in midi_banks[bank]:
        MIDI.send(NoteOff(note, 0))

# Maps a MIDI value to a BPM between 50 and 200
def midi_map_to_bpm(val):
    """maps a midi value to a BPM between 50 and 200

    Args:
        val (int): midi value to map

    Returns:
        int: BPM from 50-200
    """

    min_val = 50
    max_val = 200
    val_range = max_val - min_val

    if val == 0:
        return min_val

    mapped_val = round((val / 127) * val_range + min_val)

    return mapped_val

#---------
# SCREEN 1
#---------
def update_bank(direction = "L"):
    """goes to the next or previous midi bank

    Args:
        direction (str, optional): Direction to go. Accepts "L" or "R". Defaults to "L".
    """

    global bank

    if (bank > 0) and (direction.upper() == "L"):                          # Left button pressed and we have room to go left
        clear_bank_notes()
        bank -= 1
        currentScreen.display_screen(setting = str(bank), total_refresh = False)

    elif (bank < (len(midi_banks) - 1)) and (direction.upper() == "R"):
        clear_bank_notes()
        bank += 1
        currentScreen.display_screen(setting = str(bank), total_refresh = False)

#---------
# SCREEN 2
#---------
def update_sync_mode():
    """toggle between sync and free midi mode"""

    global SYNC

    SYNC = not SYNC

    if SYNC:
        dispText = "SYNC"
    else:
        dispText = "Free"

    currentScreen.display_screen(setting = dispText, total_refresh = False)

#---------
# SCREEN 3
#---------
def update_repeat_speed(direction = "L"):
    """update the repeat speed depending on pot value.

    Args:
        direction (str, optional): toggle thru speeds to the right or left. Defaults to "L".
    """

    global curr_repeat_spd_idx
    global cur_repeat_spd

    if (curr_repeat_spd_idx > 0) and (direction.upper() == "L"):
        curr_repeat_spd_idx -= 1

        if curr_repeat_spd_idx == 0:
            cur_repeat_spd = REPEAT_NUM * 2

        else:
            cur_repeat_spd = REPEAT_NUM / curr_repeat_spd_idx
        update_repeat_interval(reset = True)
        speed_text = REPEAT_SPDS_TEXT[curr_repeat_spd_idx]
        currentScreen.display_screen(setting = speed_text, total_refresh = False)


    elif (curr_repeat_spd_idx < (len(REPEAT_SPDS_TEXT) - 1)) and (direction.upper() == "R"):
        curr_repeat_spd_idx += 1
        cur_repeat_spd = REPEAT_NUM / curr_repeat_spd_idx
        update_repeat_interval(reset = True)
        speed_text = REPEAT_SPDS_TEXT[curr_repeat_spd_idx]
        currentScreen.display_screen(setting = speed_text, total_refresh = False)

#---------
# SCREEN 4
#---------
def remap_button_midi(noteIdx):
    """remap a button to a new midi value

    Args:
        noteIdx (int): IDX of note to remap
    """

    changed = False

    pot1_val = POTS_MIDI[0][0]
    if POTS_MIDI[0][3]:
        changed = True
        midi_banks[bank][noteIdx] = pot1_val

    else:
        if btn_R_press and midi_banks[bank][noteIdx] < 127:
            changed = True
            midi_banks[bank][noteIdx] = midi_banks[bank][noteIdx] + 1

        if btn_L_press and midi_banks[bank][noteIdx] > 0:
            changed = True
            midi_banks[bank][noteIdx] = midi_banks[bank][noteIdx] - 1

    if changed:  # Only need to update the screen if something changed
        currentScreen.display_screen(setting = str(midi_banks[bank][noteIdx]), extra = str(MIDI_BANKS_DEFAULT[bank][noteIdx]), total_refresh = False)

#---------
# SCREEN 5
#---------
def update_bpm():
    """sets the bpm, which is only used in sync repeat mode"""

    global bpm
    changed = False

    pot1_val = POTS_MIDI[0][0]
    if POTS_MIDI[0][3]:
        changed = True
        bpm = midi_map_to_bpm(pot1_val)   # Map MIDI value to a real BPM

    else:
        if btn_R_press and bpm < 200:
            changed = True
            bpm = bpm + 1

        elif btn_L_press and bpm > 50:
            changed = True
            bpm = bpm - 1

    if changed:  # Only need to update the screen if something changed
        update_repeat_interval(reset = True)
        currentScreen.display_screen(setting = str(bpm), total_refresh = False)

# Init a few more things before starting now that we have functions defined....

#*********************************************************************
#************** G E T   R E A D Y    F O R    L A U N C H ************
#*********************************************************************

buttons_classvers = []                        # Init an array to store button objects
for idx, button in enumerate(BUTTONS):
    buttons_classvers.append(Button(button, idx))

BUTTONS = buttons_classvers                   # Reclaim the BUTTONS array. It's now filled with button objects

menuScreens = []
for screen in SCREENS_LIST:
    menuScreens.append(menu_Screen(screen[0], screen[1], screen[2]))

SCREENS_LIST = menuScreens
currentScreen = menuScreens[currentScreen_idx]
currentScreen.display_screen(setting = str(bank))


#*********************************************************************************
# $$$$$$$$$$$$$$$$$$$$$$$ M  A  I  N       L  O  O  P  $$$$$$$$$$$$$$$$$$$$$$$$$$
#**********************************************************************************
while True:

    get_pot_values()                                  # Update the pot values
    update_global_times()                             # Update times for the FX

    if POTS_MIDI[0][2] and not (currentScreen_idx == 3 or currentScreen_idx == 4):
        MASTER_VEL = POTS_MIDI[0][0]                      # Get the base volume

    if currentScreen_idx == 4:
        update_bpm()

    falloff_factor_settings()
    new_presses.clear()                              # Store BUTTONS that were pressed since last cycle


# ------------------------------ Button Loop ------------------------------------------------------
# ------------------------------------------------------------------------------------------------
    # Loop over each button and send a MIDI note if it was pressed
    for idx, button in enumerate(BUTTONS):

        value_now = button.get_current_btn_value()
        valueBefore = button.valueBefore
        button.valueBefore = value_now
        vel = MASTER_VEL
        sendNoteForButton = False
        button.sendNewNote = False
        press = (value_now and not valueBefore)
        button.press = press
        bankNow = midi_banks[bank]
        lockHold = button.lockHold

        #Check to see if we are in MIDI mapping mode. Intercept before getting to note sending.
        if currentScreen_idx == 3:
            if valueBefore and value_now:
                remap_button_midi(idx)

        else:
            midi_bank_temp = bankNow

        if value_now or (lockHold and has_interval):   # Either pressing the button, or the button is hold locked and we care about repeats.

            if press:
                new_presses.append(button)
                button.timeElapsed = 0

            if SYNC:
                sendNoteForButton = press or send_new_val

            else:
                button.timeElapsed = button.timeElapsed + ((time_now - button.prevTime) / 1000000000)
                button.prevTime = time_now

                if button.timeElapsed > REPEAT_DURATION:
                    button.sendNewNote = True
                    button.timeElapsed = 0

                sendNoteForButton = press or (button.sendNewNote and has_interval)

            if sendNoteForButton:

                if (valueBefore or lockHold) and (FALLOFF_FACTOR > 0) and has_interval: # Update the volume if needed
                    vel = update_velocity(button)
                
                MIDI.send(NoteOn(bankNow[idx], vel))            # Choose the right note, depending on the bank
                button.velocityBefore = vel
        else:
            MIDI.send(NoteOff(bankNow[idx], 0))
       

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ^^^^^^^^^^^^^^^^^^^^     Options / Screen Controls   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    
    btn_L_now = CONTROL_BUTTONS[0][0].value
    btn_L_then = CONTROL_BUTTONS[0][1]
    btn_L_press = btn_L_now and not btn_L_then
    btn_L_hold = btn_L_now and btn_L_then
    btn_L_release = btn_L_then and not btn_L_now
    CONTROL_BUTTONS[0][1] = btn_L_now

    btn_R_now = CONTROL_BUTTONS[1][0].value
    btn_R_then = CONTROL_BUTTONS[1][1]
    btn_R_press = btn_R_now and not btn_R_then
    btn_R_hold = btn_R_now and btn_R_then
    btn_R_release = btn_R_then and not btn_R_now
    CONTROL_BUTTONS[1][1] = btn_R_now

    if (btn_L_hold and (btn_R_hold or btn_R_release)):                 # User wants to change the screen. Reset the button release counter and change the screen.

        if btn_R_hold:
            if POTS_MIDI[0][3]:
                clear_all_holds()                                      # Hold both BUTTONS and twist knob 1 to clear all holds
                set_press = True

        if new_presses:
            set_press = True
            for button in new_presses:
                button.lockHold = not button.lockHold

        elif btn_R_release and not set_press:
            currentScreen.next_screen()
            currentScreen.display_screen()

        NUM_RELEASE_TO_IGNORE = 1

    elif (NUM_RELEASE_TO_IGNORE < 1) and btn_L_release:
        set_press = False
        if currentScreen_idx == 0:                  # 1 - bank Selector
            update_bank("L")

        elif currentScreen_idx == 1:                # 2 - Repeat SYNC mode
            update_sync_mode()

        elif currentScreen_idx == 2:                # 3 - Repeat Speeds
            update_repeat_speed("L")


    elif (NUM_RELEASE_TO_IGNORE < 1) and btn_R_release:
        set_press = False

        if currentScreen_idx == 0:                  # 1 - bank Selector
            update_bank("R")

        elif currentScreen_idx == 1:                # 2 - Repeat SYNC mode
            update_sync_mode()

        elif currentScreen_idx == 2:                # 3 - Repeat Speeds
            update_repeat_speed("R")

    elif btn_L_release or btn_R_release:
        set_press = False
        NUM_RELEASE_TO_IGNORE -= 1

    time.sleep(SLEEPY_TIME)


# XXXXXXXXXXXXXXXX END XXXXXXXXXXXXXXXXXX
# Notes from performance testing (per... 10 or 100 loops maybe?
# I forget.. but still useful for relative comparison

    # OLED.fill ms:      10
    # OLED.text ms:      9 ms   (per character.. spaces save maybe 1-2 ms per)
    # OLED.show ms:      100.6
    # OLED.rect ms:      19.5   (for two)
    # OLED.vline ms:     2.9    (full height)
    # OLED.hline ms:     3.9    (full width)
    # OLED.fill_rect ms: 116    ( > 10x if not filled)
    # OLED.pixel ms:     11.7   (for a loop of 64 pixels)
    # OLED.line ms:      22.4   (full diag)

    # min latency 1 loop: 22 ms