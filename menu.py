#!/usr/bin/python
# Raspberry pi control
# menu to run through items
# items to display are: time, wlanIP, Eth0IP, last button called

from time import *
import time
import datetime
import sys
import collections
import datetime
import lcddriver
import stepper
from subprocess import *
import RPi.GPIO as GPIO

# clear screen
GPIO.cleanup()

# # Define GPIO inputs and outputs
# MODE
E_PULSE = 0.00005
E_DELAY = 0.00005
wait = 0.1

DIR = 16  # Direction GPIO Pin
STEP = 18  # Step GPIO Pin
CW = 1     # Clockwise Rotation
CCW = 0  # Counterclockwise Rotation
delay = .006

display = lcddriver.lcd()
# BUTTONS
RT = 38
OK = 31
DN = 33
RI = 35
LE = 37
UP = 29
ST = 40

tag = 0
val = 0
p = 0

try:
    def main():
        
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(22, GPIO.OUT)
        GPIO.setup(RT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(OK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(DN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(RI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(LE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(UP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ST, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(DIR, GPIO.OUT)
        GPIO.setup(STEP, GPIO.OUT)
        GPIO.setup(13, GPIO.OUT) #stepper motor controler enable
        GPIO.output(22, 1)
        p = 0
        tag = 0
        val = 0
        i = 0
        display.lcd_backlight(1)
        menu(0,0,0)
        display.lcd_display_string("      MENU      ",1)
        while True:
            
            rt = GPIO.input(RT)
            ok = GPIO.input(OK)
            dn = GPIO.input(DN)
            ri = GPIO.input(RI)
            le = GPIO.input(LE)
            up = GPIO.input(UP)
            if rt == True:
                p = "rt"
            if ok == True:
                p = "ok"
            if dn == True:
                p = "dn"
            if ri == True:
                p = "ri"
            if le == True:
                p = "le"
            if up == True:
                p = "up"
            if p != 0:
                result = message(tag, val, p)
                val = result['val']
                tag = result['tag']
                result = menu(tag, val, i)
                i = result['i']
                print "Tag: " + str(tag)
                print "Wartosc: " + str(val)
                p = 0
            sleep(wait)


    def message(tag, val, button):
        if button == "ok":
            tag = 10
            val = 0
        if button == "rt":
            tag = -10
            val = 0
        if button == "dn":
            val = -1
        if button == "up":
            val = 1
        if button == "le":
            tag = -1
            val = 0
        if button == "ri":
            tag = 1
            val = 0

        return {'tag': tag, 'val': val}
    
    def menu(tag, val, i):
        menuList = ["Start", "L. krokow:", "L. przejazdow:", "Wolny przejazd", "Wylacz"]
        
        
        if tag == 10:
            val = 0
            tag = 0
            #print "now"
            if i == 1:
                howMuchSteps()
            elif i == 2:
                howMuchMoves()
            elif i == 3:
                moveRightLeft("prawo",0,False,True)
            elif i == 0:
                numberOfMoved = 0
                moveRightLeft("lewo",numberOfMoved,True,False)
                stepper.setPositionZero(1000,0)
                display.lcd_clear()
                data = open("liczbakrokowdonoza.txt", "r").read().split()
                manySteps = data[0]
                stepper.moveStepperMotor(int(manySteps), CCW,True) 
                moveRightLeft("prawo", -1, False,False)
                display.lcd_clear()
                display.lcd_display_string("Wlacz silnik",1)
                display.lcd_display_string("i wcisnij OK",2)
                sleep(3)
                while True:
                    if GPIO.input(OK):
                        display.lcd_clear()
                        break
                stepper.moveStepperMotor(int(manySteps), CW,True)
                moveRightLeft("lewo",0, False,False)

        if val == 1:
            i = i - 1
            val = 0
        if val == -1:
            i = i + 1
            val = 0

        if i > 4:
            i = 0
        if i < 0:
            i = 4

        if tag != 0:
            tag = 0

        
        display.lcd_clear()
        display.lcd_display_string("      MENU      ",1)
        display.lcd_display_string(menuList[i],2)
        print i 
        return {'i': i}   
        
    def moveRightLeft(direction, numberOfMoved, shortMove, freeMove):
        print "prawo lewo"
        data = open("dane.txt", "r").read().split()
        steps = int(data[0])
        moves = int(data[1])
        display.lcd_clear()
        display.lcd_display_string("     Praca      ",1)
        display.lcd_display_string("Przejazd: " + str(numberOfMoved+1) + "/" + str(moves),2)
        #GPIO.output(22, 1)
        rightLimitSwitch=11
        leftLimitSwitch=7
        GPIO.setup(32, GPIO.OUT)
        GPIO.setup(36, GPIO.OUT)
        GPIO.setup(rightLimitSwitch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(leftLimitSwitch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        if (shortMove):
            start = datetime.datetime.now()

        while True:
            sleep(0.01)
            if GPIO.input(38):
                sleep(0.01)
                if freeMove:
                    moveRightLeft("prawo",-1,False,True)
                    main()
                else:
                    #GPIO.output(32, 0)
                    #GPIO.output(36, 0)
                    moveRightLeft("prawo", -1, False, False)
                    data = open("liczbakrokowdonoza.txt", "r")
                    howMuchStepsDo = int(data.read().split()[0])
                    data.close()
                    stepper.moveStepperMotor(howMuchStepsDo, 0, False)
                    sleep(0.5)
                    print ("to teraz: ",howMuchStepsDo)
                    #moveRightLeft("prawo",-1,False,False)
                    main()
            if direction == "prawo":
                GPIO.output(32, 1)
                GPIO.output(36, 0)
                if (GPIO.input(rightLimitSwitch) == 1):
                    direction = "lewo"
                    print "teraz lewo + " + str(GPIO.input(rightLimitSwitch))
                    break
                #print "prawo"
            elif direction == "lewo":
                GPIO.output(32, 0)
                GPIO.output(36, 1)
                #print "lewo"
                if (GPIO.input(leftLimitSwitch) == 1):
                    direction = "prawo"
                    #print "teraz prawo"
                    print "teraz prawo + " + str(GPIO.input(leftLimitSwitch))
                    break
            
            if (shortMove):
                elapsed = datetime.datetime.now() - start
                if elapsed.seconds >= 3:
                    GPIO.output(32, 0)
                    GPIO.output(36, 0)
                    return "siema"
                    print("Czas ktory minal: ",elapsed.seconds,":",elapsed.microseconds)
            
        GPIO.output(32, 0)
        GPIO.output(36, 0)
        
        if (numberOfMoved == -1):       
            return "koniec"
        numberOfMoved += 1
        print "Liczba ruchow: " + str(numberOfMoved)
        
        
        #print direction
        if not freeMove:
            if numberOfMoved < moves:
                sleep(1)
                if (numberOfMoved + 1) % 2 == 0:
                    display.lcd_clear()
                    display.lcd_display_string(" Przesuwanie... ",1)
                    stepper.moveStepperMotor(steps, CW, True)
                    sleep(1)
                    data = open("liczbakrokowdonoza.txt", "r")
                    howMuchStepsDo = int(data.read().split()[0])
                    data.close()

                    howMuchStepsDone = howMuchStepsDo + steps
                    f = open("liczbakrokowdonoza.txt", "w")
                    f.write(str(howMuchStepsDone))
                    f.close()

                moveRightLeft(direction, numberOfMoved, False,False)
            else:
                data = open("liczbakrokowdonoza.txt", "r")
                howMuchStepsDo = int(data.read().split()[0])
                data.close()
                sleep(0.5)
                stepper.moveStepperMotor(howMuchStepsDo, CCW,True)
                print "koniec"
                main()
        else:
            if numberOfMoved < moves:
                sleep(1)
                moveRightLeft(direction, numberOfMoved, False,False)
            else:
                main()
        

    def howMuchSteps():
        data = open("dane.txt", "r").read().split()
        steps = int(data[0])
        display.lcd_clear()
        display.lcd_display_string(" Liczba krokow",1)
        display.lcd_display_string("ile: " + str(steps),2)
        while True:
            sleep(0.1)
            if GPIO.input(38):
                f = open("dane.txt", "w")
                f.write(str(steps) + "\n" + data[1])
                f.close()
                main()
            elif GPIO.input(37):
                if steps > 0:
                    steps -= 1
                    display.lcd_display_string("                ",2)
                    display.lcd_display_string("ile: " + str(steps),2)
            elif GPIO.input(35):
                steps += 1
                display.lcd_display_string("                ",2)
                display.lcd_display_string("ile: " + str(steps),2)

    def howMuchMoves():
        data = open("dane.txt", "r").read().split()
        moves = int(data[1])
        display.lcd_clear()
        display.lcd_display_string("L. przejazdow",1)
        display.lcd_display_string("ile: " + str(moves),2)
        while True:
            sleep(0.1)
            if GPIO.input(38):
                f = open("dane.txt", "w")
                f.write(data[0] + "\n" + str(moves))
                f.close()
                main()
            elif GPIO.input(37):
                if moves > 0:
                    moves -= 2
                    display.lcd_display_string("                ",2)
                    display.lcd_display_string("ile: " + str(moves),2)
            elif GPIO.input(35):
                moves += 2
                display.lcd_display_string("                ",2)
                display.lcd_display_string("ile: " + str(moves),2)

    if __name__ == '__main__':
        main()

finally:
    GPIO.cleanup()
    display.lcd_clear()
    display.lcd_backlight(0)
