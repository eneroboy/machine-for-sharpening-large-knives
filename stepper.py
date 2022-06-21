#!/usr/bin/python
from time import *
import lcddriver
from subprocess import *
import RPi.GPIO as GPIO

DIR = 16  # Direction GPIO Pin
STEP = 18  # Step GPIO Pin
CW = 1     # Clockwise Rotation
CCW = 0    # Counterclockwise Rotation
SPR = 1000  # Steps per Revolution (360 / 7.5) 2100 krokow do noza
RT = 38
OK = 31
DN = 33
RI = 35
LE = 37
UP = 29
ST = 40


GPIO.setmode(GPIO.BOARD)
GPIO.setup(RT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(OK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(UP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ST, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)


display = lcddriver.lcd()
delay = .003

def setPositionZero(numberOfStepsToDo,numberOfStepsDone):
    howManySteps = 100
    while True:
        display.lcd_display_string("Ile krokow: " + str(numberOfStepsToDo),1)
        display.lcd_display_string("Ile zrobil: " + str(numberOfStepsDone),2)
        if GPIO.input(RI):
            sleep(0.01)
            display.lcd_clear()
            numberOfStepsToDo += howManySteps
        elif GPIO.input(LE):
            display.lcd_clear()
            sleep(0.01)
            if numberOfStepsToDo <= 0:
                numberOfStepsToDo = 0
            elif numberOfStepsToDo-howManySteps < 0:
                numberOfStepsToDo = numberOfStepsToDo
            else: 
                numberOfStepsToDo -= howManySteps
        elif GPIO.input(UP) or GPIO.input(DN):
            display.lcd_clear()
            if GPIO.input(UP):
                display.lcd_display_string(" Przesuwanie... ",1)
                numberOfStepsDone += moveStepperMotor(numberOfStepsToDo, CW,True)
                sleep(0.3)
                print "Liczba zrobionych krokow: " + str(numberOfStepsDone)

            elif GPIO.input(DN):
                if numberOfStepsDone > 0 and numberOfStepsDone-numberOfStepsToDo >= 0:
                    display.lcd_display_string(" Przesuwanie... ",1)
                    numberOfStepsDone -= moveStepperMotor(numberOfStepsToDo, CCW,True)
                    print "Liczba cofnietych krokow: " + str(numberOfStepsDone)
                else:
                    display.lcd_display_string("Nie mozna wiecej",1)
                    display.lcd_display_string("cofnac",2)
                    sleep(0.5)
                sleep(0.3)
                
        elif GPIO.input(ST):
            display.lcd_clear()
            if howManySteps == 10:
                howManySteps = 100
            elif howManySteps == 100:
                howManySteps = 1
            else:
                howManySteps = 10
            display.lcd_display_string_pos("Teraz zmiana",1,0)
            display.lcd_display_string_pos("o: " + str(howManySteps),2,0)
            sleep(1)
        elif GPIO.input(OK):
            f = open("liczbakrokowdonoza.txt", "w")
            f.write(str(numberOfStepsDone))
            f.close()
            return "koniec"

        
def moveStepperMotor(step_count, direction, possibleStop):
    GPIO.output(DIR, direction)
    GPIO.output(13, 1) #zasilanie do sterownika krokowego
    k = 0
    
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        print "przod: " + str(k)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)
        k = k + 1
        if GPIO.input(RT) and possibleStop:
            GPIO.output(13, 0)
            return k
            
        
    #display.lcd_clear()
    GPIO.output(13, 0) #zasilanie do sterownika krokowego
    return k

if __name__ == '__main__':
    try:
        setPositionZero(1000,0)
    finally:
        GPIO.cleanup()
        display.lcd_clear()
        display.lcd_backlight(0)