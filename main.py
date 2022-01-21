# --- TESTING & PERFORMANCE ---
def check():
    global L_SELECT, R_SELECT, Lcycles, Rcycles, status_val, agc_val
    basic.show_string("L=" + str(L_SELECT) + "R=" +  str(R_SELECT))
    as5600_read(L_SELECT)
    basic.show_string("Lcycles=" + str(read_rotation(L_SELECT)) + ",S=" + str(status_val) + ",A=" + str(agc_val))
    as5600_read(R_SELECT)
    basic.show_string("Rcycles=" + str(read_rotation(R_SELECT)) + ",S=" + str(status_val) + ",A=" + str(agc_val))
def time_point24():
    dial24_init()
    ms = 0 - input.running_time()
    for index in range(1000):
        dial24_point(index)
    ms += input.running_time()
    dial24_finish()
    basic.show_number(ms)
    basic.pause(5000)
def time_track_update():
    ms2 = 0 - input.running_time()
    for index2 in range(1000):
        track_update()
    ms2 += input.running_time()
    basic.clear_screen()
    basic.show_number(ms2)
    basic.pause(5000)
    basic.clear_screen()
    basic.show_number(ms2)
#
#
# --- TRACKING ---
def activate():
    global active
    datalogger.delete_log()
    datalogger.set_columns(["Lfraction%", "Lcycles", "Rfraction%", "Rcycles", "distance", "turn"])
    datalogger.include_timestamp(FlashLogTimeStampFormat.SECONDS)
    track_start()
    active = 1
def track_start():
    global Lcycles, Lfraction, Lfraction_was, Rcycles, Rfraction, Rfraction_was, L_SELECT, R_SELECT
    Lcycles = 0
    Lfraction = read_rotation(L_SELECT) / 4096
    Lfraction_was = Lfraction
    Rcycles = 0
    Rfraction = read_rotation(R_SELECT) / 4096
    Rfraction_was = Rfraction
def track_update():
    global Lcycles, Lfraction, Lfraction_was, Rcycles, Rfraction, Rfraction_was, L_SELECT, R_SELECT, JUMP
    delta_was = Lfraction - Lfraction_was
    new = read_rotation(L_SELECT) / 4096
    delta = new - Lfraction
    if (delta_was < 0) and (delta > JUMP):
        delta += -1
    if (delta_was > 0) and (delta < (0- JUMP)):
        delta += 1
    Lcycles += delta
    Lfraction_was = Lfraction
    Lfraction = new
    delta_was = Rfraction - Rfraction_was
    new = read_rotation(R_SELECT) / 4096
    delta = new - Rfraction
    if (delta_was < 0) and (delta > JUMP):
        delta += -1
    if (delta_was > 0) and (delta < (0- JUMP)):
        delta += 1
    Rcycles += delta
    Rfraction_was = Rfraction
    Rfraction = new

def track_distance():
    return ((Lcycles + Rcycles) * MM_PER_CYCLE / 2)
def track_turn():
    return ((Lcycles - Rcycles) * DEG_PER_CYCLE)
#
#
# --- DIAL24 ---
def dial24_init():
    global dial24_list, dial24_is
    dial24_list = [2120,
        2130,
        3130,
        3140,
        3141,
        3241,
        3242,
        3243,
        3343,
        3344,
        3334,
        2334,
        2324,
        2314,
        1314,
        1304,
        1303,
        1203,
        1202,
        1201,
        1101,
        1100,
        1110,
        2110]
    dial24_is = -1
    basic.clear_screen()
    led.plot(2, 2)
def dial24_point(value: number):
    global dial24_is, dial24_list
    if dial24_is > -1:
        dial24_flip(dial24_is)
    dial24_is = dial24_list[(value + 24) % 24]
    dial24_flip(dial24_is)
def dial24_flip(xyxy: number):
    dial24_flip_xy(Math.idiv(xyxy, 100))
    dial24_flip_xy(xyxy % 100)
def dial24_flip_xy(xy: number):
    led.toggle(Math.idiv(xy, 10), xy % 10)
def dial24_finish():
    global dial24_list, dial24_is
    dial24_list = []
    if dial24_is != -1:
        basic.clear_screen()
        dial24_is = -1
#
#
# --- ROTATION SENSORS ---
def read_rotation(select: number):
    global MPX_ADDR, AS5600_ADDR, RAW_REG
    # Write control byte with bit set to select which "line"
    pins.i2c_write_number(MPX_ADDR, select, NumberFormat.INT8_LE, False)
    # basic.pause(1)
    # Addressing rotation sensor on 0x36
    # Write 1 byte = 12  to  select RAW register.
    pins.i2c_write_number(AS5600_ADDR, RAW_REG, NumberFormat.INT8_LE, False)
    # basic.pause(1)
    # Read 2 bytes of RAW rotation
    return pins.i2c_read_number(AS5600_ADDR, NumberFormat.INT16_BE, False)
def fetch_byte_reg(byte_reg: number, select: number):
    global MPX_ADDR, AS5600_ADDR
    pins.i2c_write_number(MPX_ADDR, select, NumberFormat.INT8_LE, False)
    # basic.pause(1)
    pins.i2c_write_number(AS5600_ADDR, byte_reg, NumberFormat.INT8_LE, False)
    # basic.pause(1)
    return Ubyte(pins.i2c_read_number(AS5600_ADDR, NumberFormat.INT8_LE, False))
def fetch_word_reg(word_reg: number, select: number):
    global MPX_ADDR, AS5600_ADDR
    pins.i2c_write_number(MPX_ADDR, select, NumberFormat.INT8_LE, False)
    # basic.pause(1)
    pins.i2c_write_number(AS5600_ADDR, word_reg, NumberFormat.INT8_LE, False)
    # basic.pause(1)
    return Uword(pins.i2c_read_number(AS5600_ADDR, NumberFormat.INT16_BE, False))
def as5600_read(select: number):
    global config_val, status_val, agc_val, CONFIG_REG, STATUS_REG, AGC_REG, RAW_REG
    config_val = fetch_word_reg(CONFIG_REG, select)
    status_val = fetch_byte_reg(STATUS_REG, select)
    agc_val = fetch_byte_reg(AGC_REG, select)
    raw_val = fetch_word_reg(RAW_REG, select)
#
#
# --- MOTOR CONTROL ---
def switch_sides():
    global Side_is_L
    Side_is_L = 1 - Side_is_L
    if Side_is_L == 1:
        basic.show_arrow(ArrowNames.EAST)
    else:
        basic.show_arrow(ArrowNames.WEST)
    basic.pause(500)
def set_Lspeed(speed: number):
    if speed > 0:
        Kitronik_Move_Motor.motor_on(Kitronik_Move_Motor.Motors.MOTOR_LEFT,
            Kitronik_Move_Motor.MotorDirection.FORWARD,
            speed)
    else:
        Kitronik_Move_Motor.motor_on(Kitronik_Move_Motor.Motors.MOTOR_LEFT,
            Kitronik_Move_Motor.MotorDirection.REVERSE,
            0 - speed)
def set_Rspeed(speed2: number):
    if speed2 > 0:
        Kitronik_Move_Motor.motor_on(Kitronik_Move_Motor.Motors.MOTOR_RIGHT,
            Kitronik_Move_Motor.MotorDirection.FORWARD,
            speed2)
    else:
        Kitronik_Move_Motor.motor_on(Kitronik_Move_Motor.Motors.MOTOR_RIGHT,
            Kitronik_Move_Motor.MotorDirection.REVERSE,
            0 - speed2)
#
#
# --- DATA UTILITIES ---
def hex_int32(int32: number):
    return "" + hex_word(Math.floor(int32 / 65536)) + hex_word(int32 % 65536)
def hex_word(word: number):
    return "" + hex_byte(Math.floor(word / 256)) + hex_byte(word % 256)
def hex_byte(byte: number):
    return "" + hex_nibble(Math.floor(byte / 16)) + hex_nibble(byte % 16)
def hex_nibble(nibble: number):
    if nibble < 10:
        return String.from_char_code(48 + nibble)
    else:
        return String.from_char_code(55 + nibble)
def Uword(val: number):
    return (val + 65536) % 65536
def Ubyte(val2: number):
    return (val2 + 256) % 256
#
#
# --- SET LITERALS ---
def set_defs():
    global MPX_ADDR, AS5600_ADDR, CONFIG_REG, AGC_REG, STATUS_REG, RAW_REG
    global L_SELECT, R_SELECT, MM_PER_CYCLE
    # Address multiplexor on 0x70
    MPX_ADDR = 112
    # Address rotation sensor on 0x36
    AS5600_ADDR = 54
    # Configuration register starts at 7
    CONFIG_REG = 7
    # Automatic_Gain_Control register starts at 26
    AGC_REG = 26
    # Status register starts at 7
    STATUS_REG = 11
    # Raw_Rotation register starts at 7
    RAW_REG = 12
    # Set binary 00000001 to select line 0
    L_SELECT = 1
    # Set binary 00000010 to select line 1
    R_SELECT = 2
    MM_PER_CYCLE = 71.61
    DEG_PER_CYCLE = 39.25
    JUMP = 0.25

#
#
# --- DECLARATIONS ---
MM_PER_CYCLE = 0
DEG_PER_CYCLE = 0
RAW_REG = 0
AGC_REG = 0
STATUS_REG = 0
CONFIG_REG = 0
TURN = 0
JUMP = 0
L_SELECT = 0
R_SELECT = 0
AS5600_ADDR = 0
MPX_ADDR = 0
Lspeed = 0
Rspeed = 0
active = 0
dial24_is = 0
dial24_list: List[number] = []
Side_is_L = 0
Rfraction_was = 0
Rfraction = 0
Rcycles = 0
Lfraction_was = 0
Lfraction = 0
Lcycles = 0
agc_val = 0
status_val = 0
config_val = 0
raw_val = 0
distance = 0
turn = 0
#
#
# --- MAIN CODE ---
set_defs()
basic.show_icon(IconNames.YES)
basic.pause(1000)
# dial24_init()
# for index3 in range(25):
    # dial24_point(index3)
    # basic.pause(100)
# dial24_finish()
# basic.pause(1000)
switch_sides()
# time_update_track()
#start_track()
#basic.show_number(read_rotation(L_SELECT))
basic.pause(1000)
#check()
#
#
# --- SET INTERRUPT HANDLERS ---
def on_button_pressed_a():
    global Lspeed, Rspeed, Rfraction, Lfraction
    if Side_is_L == 1:
        if Lspeed > -100:
            Lspeed += -10
            set_Lspeed(Lspeed)
            dial24_point(Math.round(Lfraction))
    elif Rspeed > -100:
        Rspeed += -10
        set_Rspeed(Rspeed)
        dial24_point(Math.round(Rfraction))
input.on_button_pressed(Button.A, on_button_pressed_a)
def on_button_pressed_b():
    global Lspeed, Rspeed, Rfraction, Lfraction
    if Side_is_L == 1:
        if Lspeed < 100:
            Lspeed += 10
            set_Lspeed(Lspeed)
            dial24_point(Math.round(Lfraction))
    elif Rspeed < 100:
        Rspeed += 10
        set_Rspeed(Rspeed)
        dial24_point(Math.round(Rfraction))
input.on_button_pressed(Button.B, on_button_pressed_b)
def on_button_pressed_ab():
    global active
    if active == 0:
        dial24_init()
        activate()
    else:
        active = 0
        dial24_finish()
input.on_button_pressed(Button.AB, on_button_pressed_ab)
def on_logo_pressed():
    switch_sides()
input.on_logo_event(TouchButtonEvent.PRESSED, on_logo_pressed)
def on_every_interval():
    global Lcycles, Lfraction, Rcycles, Rfraction, distance, turn
    if active == 1:
        track_update()
        distance = track_distance()
        turn = track_turn()
    #********************
        datalogger.log_data([datalogger.create_cv("Lfraction%", Math.round(Lfraction * 100)),
                datalogger.create_cv("Lcycles", Math.round(Lcycles)),
                datalogger.create_cv("Rfraction%", Math.round(Rfraction * 100)),
                datalogger.create_cv("Rcycles", Math.round(Rcycles)),
                datalogger.create_cv("distance", Math.round(distance)),
                datalogger.create_cv("turn", Math.round(turn))])
        #********************
loops.every_interval(50, on_every_interval)
def on_every_interval2():
    global Lcycles, Lfraction, Rcycles, Rfraction, distance, turn
    if active == 1:
        distance = track_distance()
        turn = track_turn()
        datalogger.log_data([datalogger.create_cv("Lfraction%", Math.round(Lfraction * 100)),
                datalogger.create_cv("Lcycles", Math.round(Lcycles)),
                datalogger.create_cv("Rfraction%", Math.round(Rfraction * 100)),
                datalogger.create_cv("Rcycles", Math.round(Rcycles)),
                datalogger.create_cv("distance", Math.round(distance)),
                datalogger.create_cv("turn", Math.round(turn))])
# loops.every_interval(200, on_every_interval2)
def on_log_full():
    global active
    active = 1 - active
    dial24_finish()
    set_Lspeed(0)
    set_Rspeed(0)
datalogger.on_log_full(on_log_full)
