import speech_recognition as sr
import subprocess as sub
import pyttsx3, pywhatkit, wikipedia, datetime, keyboard, os
from pygame import mixer 
import threading as tr



name = "Poli"
listener = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
m = {}
for i in voices:
    print (i)
m = i
