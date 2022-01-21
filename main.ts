//  --- TESTING & PERFORMANCE ---
function check() {
    
    basic.showString("L=" + ("" + L_SELECT) + "R=" + ("" + R_SELECT))
    as5600_read(L_SELECT)
    basic.showString("Lcycles=" + ("" + read_rotation(L_SELECT)) + ",S=" + ("" + status_val) + ",A=" + ("" + agc_val))
    as5600_read(R_SELECT)
    basic.showString("Rcycles=" + ("" + read_rotation(R_SELECT)) + ",S=" + ("" + status_val) + ",A=" + ("" + agc_val))
}

function time_point24() {
    dial24_init()
    let ms = 0 - input.runningTime()
    for (let index = 0; index < 1000; index++) {
        dial24_point(index)
    }
    ms += input.runningTime()
    dial24_finish()
    basic.showNumber(ms)
    basic.pause(5000)
}

function time_track_update() {
    let ms2 = 0 - input.runningTime()
    for (let index2 = 0; index2 < 1000; index2++) {
        track_update()
    }
    ms2 += input.runningTime()
    basic.clearScreen()
    basic.showNumber(ms2)
    basic.pause(5000)
    basic.clearScreen()
    basic.showNumber(ms2)
}

// 
// 
//  --- TRACKING ---
function activate() {
    
    datalogger.deleteLog()
    datalogger.setColumns(["Lfraction%", "Lcycles", "Rfraction%", "Rcycles", "distance", "turn"])
    datalogger.includeTimestamp(FlashLogTimeStampFormat.Seconds)
    track_start()
    active = 1
}

function track_start() {
    
    Lcycles = 0
    Lfraction = read_rotation(L_SELECT) / 4096
    Lfraction_was = Lfraction
    Rcycles = 0
    Rfraction = read_rotation(R_SELECT) / 4096
    Rfraction_was = Rfraction
}

function track_update() {
    
    let delta_was = Lfraction - Lfraction_was
    let new_ = read_rotation(L_SELECT) / 4096
    let delta = new_ - Lfraction
    if (delta_was < 0 && delta > JUMP) {
        delta += -1
    }
    
    if (delta_was > 0 && delta < 0 - JUMP) {
        delta += 1
    }
    
    Lcycles += delta
    Lfraction_was = Lfraction
    Lfraction = new_
    delta_was = Rfraction - Rfraction_was
    new_ = read_rotation(R_SELECT) / 4096
    delta = new_ - Rfraction
    if (delta_was < 0 && delta > JUMP) {
        delta += -1
    }
    
    if (delta_was > 0 && delta < 0 - JUMP) {
        delta += 1
    }
    
    Rcycles += delta
    Rfraction_was = Rfraction
    Rfraction = new_
}

function track_distance(): number {
    return (Lcycles + Rcycles) * MM_PER_CYCLE / 2
}

function track_turn(): number {
    return (Lcycles - Rcycles) * DEG_PER_CYCLE
}

// 
// 
//  --- DIAL24 ---
function dial24_init() {
    
    dial24_list = [2120, 2130, 3130, 3140, 3141, 3241, 3242, 3243, 3343, 3344, 3334, 2334, 2324, 2314, 1314, 1304, 1303, 1203, 1202, 1201, 1101, 1100, 1110, 2110]
    dial24_is = -1
    basic.clearScreen()
    led.plot(2, 2)
}

function dial24_point(value: number) {
    
    if (dial24_is > -1) {
        dial24_flip(dial24_is)
    }
    
    dial24_is = dial24_list[(value + 24) % 24]
    dial24_flip(dial24_is)
}

function dial24_flip(xyxy: number) {
    dial24_flip_xy(Math.idiv(xyxy, 100))
    dial24_flip_xy(xyxy % 100)
}

function dial24_flip_xy(xy: number) {
    led.toggle(Math.idiv(xy, 10), xy % 10)
}

function dial24_finish() {
    
    dial24_list = []
    if (dial24_is != -1) {
        basic.clearScreen()
        dial24_is = -1
    }
    
}

// 
// 
//  --- ROTATION SENSORS ---
function read_rotation(select: number): number {
    
    //  Write control byte with bit set to select which "line"
    pins.i2cWriteNumber(MPX_ADDR, select, NumberFormat.Int8LE, false)
    //  basic.pause(1)
    //  Addressing rotation sensor on 0x36
    //  Write 1 byte = 12  to  select RAW register.
    pins.i2cWriteNumber(AS5600_ADDR, RAW_REG, NumberFormat.Int8LE, false)
    //  basic.pause(1)
    //  Read 2 bytes of RAW rotation
    return pins.i2cReadNumber(AS5600_ADDR, NumberFormat.Int16BE, false)
}

function fetch_byte_reg(byte_reg: number, select: number): number {
    
    pins.i2cWriteNumber(MPX_ADDR, select, NumberFormat.Int8LE, false)
    //  basic.pause(1)
    pins.i2cWriteNumber(AS5600_ADDR, byte_reg, NumberFormat.Int8LE, false)
    //  basic.pause(1)
    return Ubyte(pins.i2cReadNumber(AS5600_ADDR, NumberFormat.Int8LE, false))
}

function fetch_word_reg(word_reg: number, select: number): number {
    
    pins.i2cWriteNumber(MPX_ADDR, select, NumberFormat.Int8LE, false)
    //  basic.pause(1)
    pins.i2cWriteNumber(AS5600_ADDR, word_reg, NumberFormat.Int8LE, false)
    //  basic.pause(1)
    return Uword(pins.i2cReadNumber(AS5600_ADDR, NumberFormat.Int16BE, false))
}

function as5600_read(select: number) {
    
    config_val = fetch_word_reg(CONFIG_REG, select)
    status_val = fetch_byte_reg(STATUS_REG, select)
    agc_val = fetch_byte_reg(AGC_REG, select)
    let raw_val = fetch_word_reg(RAW_REG, select)
}

// 
// 
//  --- MOTOR CONTROL ---
function switch_sides() {
    
    Side_is_L = 1 - Side_is_L
    if (Side_is_L == 1) {
        basic.showArrow(ArrowNames.East)
    } else {
        basic.showArrow(ArrowNames.West)
    }
    
    basic.pause(500)
}

function set_Lspeed(speed: number) {
    if (speed > 0) {
        Kitronik_Move_Motor.motorOn(Kitronik_Move_Motor.Motors.MotorLeft, Kitronik_Move_Motor.MotorDirection.Forward, speed)
    } else {
        Kitronik_Move_Motor.motorOn(Kitronik_Move_Motor.Motors.MotorLeft, Kitronik_Move_Motor.MotorDirection.Reverse, 0 - speed)
    }
    
}

function set_Rspeed(speed2: number) {
    if (speed2 > 0) {
        Kitronik_Move_Motor.motorOn(Kitronik_Move_Motor.Motors.MotorRight, Kitronik_Move_Motor.MotorDirection.Forward, speed2)
    } else {
        Kitronik_Move_Motor.motorOn(Kitronik_Move_Motor.Motors.MotorRight, Kitronik_Move_Motor.MotorDirection.Reverse, 0 - speed2)
    }
    
}

// 
// 
//  --- DATA UTILITIES ---
function hex_int32(int32: number) {
    return "" + hex_word(Math.floor(int32 / 65536)) + hex_word(int32 % 65536)
}

function hex_word(word: number) {
    return "" + hex_byte(Math.floor(word / 256)) + hex_byte(word % 256)
}

function hex_byte(byte: number) {
    return "" + hex_nibble(Math.floor(byte / 16)) + hex_nibble(byte % 16)
}

function hex_nibble(nibble: number): string {
    if (nibble < 10) {
        return String.fromCharCode(48 + nibble)
    } else {
        return String.fromCharCode(55 + nibble)
    }
    
}

function Uword(val: number): number {
    return (val + 65536) % 65536
}

function Ubyte(val2: number): number {
    return (val2 + 256) % 256
}

// 
// 
//  --- SET LITERALS ---
function set_defs() {
    
    
    //  Address multiplexor on 0x70
    MPX_ADDR = 112
    //  Address rotation sensor on 0x36
    AS5600_ADDR = 54
    //  Configuration register starts at 7
    CONFIG_REG = 7
    //  Automatic_Gain_Control register starts at 26
    AGC_REG = 26
    //  Status register starts at 7
    STATUS_REG = 11
    //  Raw_Rotation register starts at 7
    RAW_REG = 12
    //  Set binary 00000001 to select line 0
    L_SELECT = 1
    //  Set binary 00000010 to select line 1
    R_SELECT = 2
    MM_PER_CYCLE = 71.61
    let DEG_PER_CYCLE = 39.25
    let JUMP = 0.25
}

// 
// 
//  --- DECLARATIONS ---
let MM_PER_CYCLE = 0
let DEG_PER_CYCLE = 0
let RAW_REG = 0
let AGC_REG = 0
let STATUS_REG = 0
let CONFIG_REG = 0
let TURN = 0
let JUMP = 0
let L_SELECT = 0
let R_SELECT = 0
let AS5600_ADDR = 0
let MPX_ADDR = 0
let Lspeed = 0
let Rspeed = 0
let active = 0
let dial24_is = 0
let dial24_list : number[] = []
let Side_is_L = 0
let Rfraction_was = 0
let Rfraction = 0
let Rcycles = 0
let Lfraction_was = 0
let Lfraction = 0
let Lcycles = 0
let agc_val = 0
let status_val = 0
let config_val = 0
let raw_val = 0
let distance = 0
let turn = 0
// 
// 
//  --- MAIN CODE ---
set_defs()
basic.showIcon(IconNames.Yes)
basic.pause(1000)
//  dial24_init()
//  for index3 in range(25):
//  dial24_point(index3)
//  basic.pause(100)
//  dial24_finish()
//  basic.pause(1000)
switch_sides()
//  time_update_track()
// start_track()
// basic.show_number(read_rotation(L_SELECT))
basic.pause(1000)
// check()
// 
// 
//  --- SET INTERRUPT HANDLERS ---
input.onButtonPressed(Button.A, function on_button_pressed_a() {
    
    if (Side_is_L == 1) {
        if (Lspeed > -100) {
            Lspeed += -10
            set_Lspeed(Lspeed)
            dial24_point(Math.round(Lfraction))
        }
        
    } else if (Rspeed > -100) {
        Rspeed += -10
        set_Rspeed(Rspeed)
        dial24_point(Math.round(Rfraction))
    }
    
})
input.onButtonPressed(Button.B, function on_button_pressed_b() {
    
    if (Side_is_L == 1) {
        if (Lspeed < 100) {
            Lspeed += 10
            set_Lspeed(Lspeed)
            dial24_point(Math.round(Lfraction))
        }
        
    } else if (Rspeed < 100) {
        Rspeed += 10
        set_Rspeed(Rspeed)
        dial24_point(Math.round(Rfraction))
    }
    
})
input.onButtonPressed(Button.AB, function on_button_pressed_ab() {
    
    if (active == 0) {
        dial24_init()
        activate()
    } else {
        active = 0
        dial24_finish()
    }
    
})
input.onLogoEvent(TouchButtonEvent.Pressed, function on_logo_pressed() {
    switch_sides()
})
// ********************
loops.everyInterval(50, function on_every_interval() {
    
    if (active == 1) {
        track_update()
        distance = track_distance()
        turn = track_turn()
        // ********************
        datalogger.logData([datalogger.createCV("Lfraction%", Math.round(Lfraction * 100)), datalogger.createCV("Lcycles", Math.round(Lcycles)), datalogger.createCV("Rfraction%", Math.round(Rfraction * 100)), datalogger.createCV("Rcycles", Math.round(Rcycles)), datalogger.createCV("distance", Math.round(distance)), datalogger.createCV("turn", Math.round(turn))])
    }
    
})
function on_every_interval2() {
    
    if (active == 1) {
        distance = track_distance()
        turn = track_turn()
        datalogger.logData([datalogger.createCV("Lfraction%", Math.round(Lfraction * 100)), datalogger.createCV("Lcycles", Math.round(Lcycles)), datalogger.createCV("Rfraction%", Math.round(Rfraction * 100)), datalogger.createCV("Rcycles", Math.round(Rcycles)), datalogger.createCV("distance", Math.round(distance)), datalogger.createCV("turn", Math.round(turn))])
    }
    
}

//  loops.every_interval(200, on_every_interval2)
datalogger.onLogFull(function on_log_full() {
    
    active = 1 - active
    dial24_finish()
    set_Lspeed(0)
    set_Rspeed(0)
})
