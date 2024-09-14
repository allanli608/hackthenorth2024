import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
led_pin = 23
servo_pin = 32

GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(servo_pin, GPIO.OUT)

p = GPIO.PWM(servo_pin, 50)  # 50 Hz frequency
# 2.5% duty cycle corresponds to 0 degrees
# 12.5% duty cycle corresponds to 90 degrees
# 22.5% duty cycle corresponds to 180 degrees
p.start(0)

def set_angle(angle):
    duty = angle / 18. + 2.5
    p.ChangeDutyCycle(duty)
    time.sleep(1) # delay so servo has time to move; proportional to angle
    # p.ChangeDutyCycle(0)

try:
    # while True:
    # Turn LED on
    GPIO.output(led_pin, GPIO.HIGH)
    # Rotate to 90 degrees
    set_angle(90)
    print("on")
    time.sleep(2)
    
    # Turn LED off
    GPIO.output(led_pin, GPIO.LOW)
    # Rotate to 0 degrees
    set_angle(0)
    print("off")
    time.sleep(2)

except KeyboardInterrupt:
    GPIO.cleanup()
    p.stop() # Stop PWM output
    print("GPIO cleaned up")

finally:
    GPIO.cleanup()
    p.stop()