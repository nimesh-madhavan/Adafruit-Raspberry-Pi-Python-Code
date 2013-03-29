#!/usr/bin/python

from Adafruit_CharLCD import Adafruit_CharLCD
from time import sleep
from datetime import datetime
import urllib2
import json

digits = [[30,18,18,18,18,18,30,0],             # digit 0
                [8,8,8,8,8,8,8,0],              # digit 1   
                [30,2,2,30,16,16,30,0],         # digit 2
                [30,2,2,14,2,2,30,0],           # digit 3
                [16,20,20,20,30,4,4,0],         # digit 4
                [30,16,16,30,2,2,30,0],         # digit 5
                [30,16,16,30,18,18,30,0],       # digit 6
                [30,2,2,4,8,8,8,0],             # digit 7
                [30,18,18,30,18,18,30,0],       # digit 8
                [30,18,18,30,2,2,30,0],         # digit 9
                [28,20,28,0,14,8,8,14],         # degree celsius symbol
                [28,20,28,0,14,8,14,8],         # degree fahrenheit symbol
                [28,20,28,0,14,8,14,8]]         # negetive symbol (hyphen)

lineStart = [0x80, 0xC0, 0x94, 0xD4]    #starting position for LCD lines
        
def setupCustomChars(lcd):
        # define 2 custom chacters with half filled blocks, this will give us 8 lines in a 4 line LCD

        lcd.write4bits(0x40) #write to CGRAM

        #First char, upper 4 lines active
        lcd.write4bits(31, True)
        lcd.write4bits(31, True)
        lcd.write4bits(31, True)
        lcd.write4bits(31, True)
        lcd.write4bits(0, True)
        lcd.write4bits(0, True)
        lcd.write4bits(0, True)
        lcd.write4bits(0, True)
        
        #Second char, lower 4 lines active
        lcd.write4bits(0, True)
        lcd.write4bits(0, True)
        lcd.write4bits(0, True)
        lcd.write4bits(0, True)
        lcd.write4bits(31, True)
        lcd.write4bits(31, True)
        lcd.write4bits(31, True)
        lcd.write4bits(31, True)

def largeprint(lcd, text):
        
        text = text.replace("-","C") #Position 12 (0xC) has the - symbol
            
        for counter in range (4):
            if (len(text) <= counter):
                return
            
            position = int(text[counter:counter+1],16) # use the base 16 int parsing to get the position ofthe character
            for index in range (4):
                lcd.write4bits(lineStart[index] + counter * 5) # position the cursor

                #each physical line in LCD is composed of 2 logical lines
                line1 = digits[position][index * 2]
                line2 = digits[position][index * 2 + 1]
                
                for index in range(5):
                    bit1 = (line1 << index) & 16
                    bit2 = (line2 << index) & 16
                    charcode = 32   # the block is 'off'
                    if (bit1 != 0 and bit2 == 0):
                        charcode = 0  # First custom charater
                    elif (bit1 == 0 and bit2 != 0):        
                        charcode = 1  # Second custom character
                    elif (bit1 != 0 and bit2 != 0):
                        charcode = 255 # the block is 'on'
                    lcd.write4bits(charcode, True)    

def getTemperature():
    #call the yahoo weather API to get the current weather. As discussed in http://stackoverflow.com/questions/5000926/yahoo-weather-api-response-as-json
        
    json_data = urllib2.urlopen("http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20location%3D%2260601%22&format=json")          
    data = json.load(json_data)    

    temp = data["query"]["results"]["channel"]["item"]["condition"]["temp"]     
    json_data.close()

    return temp + 'B'   #Append 'B' for farhenheit symbol, append 'A' for celsius symmbol
    
if __name__ == '__main__':   
    
    lcd = Adafruit_CharLCD()
    
    lcd.clear()
    setupCustomChars(lcd)
    
    delay =2000000
    
    while 1:
        temp = getTemperature()

        for index in range(30*5): # Call the temperature service once in every 5 minutes
            lcd.clear() 
            largeprint(lcd, datetime.now().strftime('%I%M')) 
            lcd.delayMicroseconds(delay)
            lcd.clear() 
            largeprint(lcd, temp) 
            lcd.delayMicroseconds(delay)
            
