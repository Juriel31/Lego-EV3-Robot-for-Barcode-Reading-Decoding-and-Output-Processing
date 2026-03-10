#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import time


class Robot:
    """
    -- TEMPLATE --
    This class provides logic for moving the sensor and scrolling the bar code cards
    """
    # motors
    sensor_motor = ev3.LargeMotor('outD')   # X-axis (sensor belt)
    paper_motor = ev3.LargeMotor('outC')    # Y-axis (paper)

    # touch Sensor
    touch_sensor_l = ev3.TouchSensor()
    touch_sensor_r = ev3.TouchSensor()
   
    
    def sensor_step(self):
        """
        Moves the sensor one step to read the next bar code value
        """
        # Calibaration for X axis Paper
        with open('/sys/class/power_supply/lego-ev3-battery/voltage_now') as voltage_file:
            voltage = int(voltage_file.read())
            #print(voltage,"voltage")
            
        V_REF = 7_500_000  # µV
        voltage_factor = V_REF / voltage
        voltage_factor = max(0.9, min(1.2, voltage_factor))

        distance=7.2 # distance to travel 
        speed = 50
        d=36 #wheel dia in mm
        circumference=3.149*d
        degrees =int((distance/ circumference) * 360)

        # Actual Movement
        self.sensor_motor.reset()
        self.sensor_motor.position_sp = -degrees
        self.sensor_motor.speed_sp = int(speed * voltage_factor)
        self.sensor_motor.command = "run-to-rel-pos"
        time.sleep(2)

        return 1




    def sensor_reset(self):
        """
        Resets the sensor position
        """

        self.sensor_motor.stop_action = "brake"
        self.sensor_motor.speed_sp = 50
        self.sensor_motor.command = "run-forever"

        while self.touch_sensor_l.value() == 0:
            time.sleep(0.01)  # prevent CPU overload

        self.sensor_motor.stop()
        self.sensor_motor.wait_while('running')

        self.sensor_motor.position = 0

    
    
        
      

    def scroll_step(self):
        """
        Moves the bar code card to the next line.
        """
        # Calibaration for Y axis Paper
        with open('/sys/class/power_supply/lego-ev3-battery/voltage_now') as voltage_file:
            voltage = int(voltage_file.read())
            
        V_REF = 7_500_000  # µV
        voltage_factor = V_REF / voltage
        voltage_factor = max(0.9, min(1.2, voltage_factor))

        speed = 50
        d=31
        distance_cm=2.5 
        distance_y=(distance_cm*10) #with error correction
        circumference=3.149*d
        degrees =int((distance_y / circumference) * 360)

        # Actual Movement
        self.paper_motor.run_to_rel_pos(
            position_sp=-degrees, 
            speed_sp=int(speed * voltage_factor)
        )
        self.paper_motor.wait_while('running')

    def read_value(self):
        """
        RGB-RAW based BLACK / WHITE detection with temporal filtering

        Returns:
        1 = BLACK/RED
        0 = WHITE"""

        cs = ev3.ColorSensor()
        cs.mode = 'RGB-RAW'

        BLACK_THRESHOLD = 600

        SAMPLES = 10          # number of readings
        REQUIRED_MATCH = 5    # how many must agree

        readings = []

        for _ in range(SAMPLES):
            try:
                r, g, b = cs.bin_data("hhh")
            except Exception:
                r, g, b, _ = cs.bin_data("hhhh")

            total = r + g + b

            if total < BLACK_THRESHOLD:
                readings.append(1)

            else:
                readings.append(0)

        # Count stable values
        black_count = readings.count(1)

        if black_count >= REQUIRED_MATCH:
            return 1

        else:
             return 0
        
    
    def sensor_start(self):
         # Calibaration for X axis Paper
        with open('/sys/class/power_supply/lego-ev3-battery/voltage_now') as voltage_file:
            voltage = int(voltage_file.read())
            #print(voltage,"voltage")
            
        V_REF = 7_500_000  # µV
        voltage_factor = V_REF / voltage
        voltage_factor = max(0.9, min(1.2, voltage_factor))

        distance=9 # distance to travel 
        speed = 50
        d=36 #wheel dia in mm
        circumference=3.149*d
        degrees =int((distance/ circumference) * 360)

        # Actual Movement
        self.sensor_motor.reset()
        self.sensor_motor.position_sp = -degrees
        self.sensor_motor.speed_sp = int(speed * voltage_factor)
        self.sensor_motor.command = "run-to-rel-pos"
        time.sleep(1)

        return 1
        
        
    def speak(self,word):
        text=str(word)
        ev3.Sound.speak(text).wait()  # speak given text

    
