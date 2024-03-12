from fileinput import close
from tkinter import font
from tkinter.ttk import Style
from types import resolve_bases
from typing import Sized
from urllib import request
import weakref
import webbrowser
from pygame.constants import TIMER_RESOLUTION
import speech_recognition as sr
import subprocess as sub
import pyttsx3, pywhatkit, wikipedia, datetime, keyboard, os
from tkinter import *
from PIL import Image, ImageTk
from pygame import mixer 
import threading as tr
import whatsapp as whapp

BGcolor = '#eef2f3'
bottoncolor = '#FF9800'
bottonletra = 'Black'
#Gui
main_window = Tk()
main_window.title("Poli AV")

main_window.geometry("900x700")
main_window.resizable(0,0)
main_window.configure(bg=BGcolor)

comandos = """
    Comandos que puedes usar:
     -Abre (Páginas web)
     -Búsca (Wikipedia)
     -Búscame (Google)
     -Escribe (Nota)
     -Mensaje (WhatsApp)
     -Reproduce (Youtube)
     -Termina (Deja de escuchar)
    Los botones de voz actuarán 
    con las voces que tegas en 
    tu pc (máximo 3), si alguno
    de los 3 botones no da 
    respuesta es por que tu Pc 
    solo tiene 2 voces incorporadas
"""


Label_title = Label(main_window, text="POLI", bg="#eef2f3", fg="#200122", 
                     font=('TIMES NEW ROMAN', 30, 'bold'))
Label_title.pack(pady=10)

canvas_comandos= Canvas(bg="#cbb4d4", height=300, width=200)
canvas_comandos.place(x=0, y=0)
canvas_comandos.create_text(96, 140, text=comandos, fill="black", font='Arial 10')

text_info = Text(main_window, bg="#D3CCE3", fg="black")
text_info.place(x=0, y=300, height=500, width=203)


poli_photo = ImageTk.PhotoImage(Image.open("POLI1.png"))
window_photo = Label(main_window, image=poli_photo)
window_photo.pack(pady=4)

#funciones para el cambio de voz
def mexican_voice ():
    change_voice(2)
def spanish_voice ():
    change_voice(0)
def english_voice ():
    change_voice(1)
def change_voice(id):
    engine.setProperty('voice', voices[id].id)
    engine.setProperty('rate', 145)
    talk("hola soy poli!")


name = "Poli"
engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('rate', 145)

def charge_data(name_dict, name_file):
    try:
        with open(name_file) as f:
            for line in f:
                (key, val) = line.split(",")
                val = val.rstrip("\n")
                name_dict[key] = val
    except FileNotFoundError as e:
        pass 

sites = dict()
charge_data(sites, "pages.txt")
contacts = dict()
charge_data(contacts, "contacts.txt")

def talk(text):
    engine.say(text)
    engine.runAndWait()

#función para leer la búsqueda en wikipedia
def read_and_talk ():
    text = text_info.get("1.0", "end")
    talk(text)

#función para escribir la búsqueda en wikipedia
def write_text(text_wiki):
    text_info.insert(INSERT, text_wiki)

#función para escuchar
def listen():
    listener = sr.Recognizer()
    with sr.Microphone() as source:
        listener.adjust_for_ambient_noise(source)
        talk("Poli te escucha")
        pc = listener.listen(source)
    try:
        rec = listener.recognize_google(pc, language="es")
        rec = rec.lower()
    except sr.UnknownValueError:
        print("No entendí, intenta de nuevo")
    except sr.RequestError as e:
        print("Could not resquest results from Google Speech Recognition service; {0}".format(e))
    return rec

#funciones de las palabras claves
def reproduce(rec):
    music = rec.replace('reproduce', '')
    print("Reproduciendo " + music)
    talk("Reproduciendo " + music)
    pywhatkit.playonyt(music)

def busca(rec):
    search = rec.replace('busca','')
    wikipedia.set_lang("es") 
    wiki = wikipedia.summary(search, 1)
    talk (wiki)
    write_text(search + ": " + wiki)

def thread_alarma(rec):
    t = tr.Thread(target=clock, args=(rec,))
    t.start()

def abre(rec):
    task = rec.replace('abre', '').strip()

    if task in sites:
        for task in sites:
            if task in rec:
                sub.call(f'start chrome.exe {sites[task]}', shell= True)
                talk (f'Abriendo {task}') 
    else:
        talk("Lo lamento, parece que aún no has agregado esa página web, usa los botones de agregar para poder ayudarte la próxima vez")


def escribe(rec):
    try:  
        with open ("nota.txt", 'a') as f:
            write(f)
    except FileNotFoundError as e:
        file = open("nota.txt", 'w')
        write(file) 

def clock(rec):
    num = rec.replace('alarma', '')
    num = num.strip()
    talk("Alarma activada a las " + num + " horas")
    if num[0] != '0' and len(num) < 5:
        num = '0' + num
    print(num)
    while True:
        if datetime.datetime.now().strftime('%H:%M') == num:
            print("DESPIERTA!!!")
            mixer.init()
            mixer.music.load("alarma_auron.mp3")
            mixer.music.play()
        else:
            continue
        if keyboard.read_key() == "s":
            mixer.music.stop()
            break

def enviar_mensaje(rec):
    talk("¿A quién quieres enviar el mensaje?")
    contact = listen()
    if contact in contacts:
        for cont in contacts:
            if cont == contact:
                contact = contacts[cont]
                talk("¿Qué mensaje deseas enviarle?")
                message = listen()
                talk("Enviando mensaje....")
                whapp.send_message(contact, message)
    else:
        talk("Lo lamento, parece que aún no has agregado ese contacto, usa los botones de agregar para poder ayudarte la próxima vez")


def buscame(rec):
    something = rec.replace('búscame', '').strip()
    talk("Buscando " + something)
    link_buscar = 'https://www.google.com/search?q='
    busqueda = link_buscar + something
    webbrowser.open_new_tab(busqueda)
    try:
        webbrowser.get("chrome").open_new(busqueda)
    except webbrowser.Error:
        print ("No se ha encontrado Chrome.")


#palabras claves
key_words = {
    'reproduce' : reproduce,
    'busca' : busca,
    'abre': abre,
    'escribe' : escribe,
    'mensaje': enviar_mensaje,
    'búscame' : buscame,
    'alarma' : thread_alarma
}


#función principal
def run_poli():
    while True:
        try:
            rec = listen()
        except UnboundLocalError:
            talk("No entendí, por favor intente de nuevo")
            continue
        if 'busca' in rec:
            key_words['busca'](rec)
            break
        else:
            for word in key_words:
                if word in rec:
                    key_words[word](rec)
        if 'termina' in rec:
            talk("Hasta la próxima, aquí estaré para ayudarte!")
            break
    main_window.update()

def write (f):
    talk("¿Qué quieres que escriba?")
    rec_write = listen()
    f.write(rec_write + os.linesep)
    f.close()
    talk("Listo, puedes revisarlo")
    sub.Popen("nota.txt", shell=True)



#Funcion para agregar paginas

def open_w_pages():
    global namepages_entry, pathp_entry
    window_pages = Toplevel()
    window_pages.title("Agregar archivos")
    window_pages.configure(bg="#0f9b0f")
    window_pages.geometry("300x300")
    window_pages.resizable(0,0)

    title_label = Label(window_pages, text="Agrega una página web", fg="black", bg="#0f9b0f", font=('Arial', 15, 'bold'))
    title_label.pack(pady=3)
    name_label = Label(window_pages, text="Nombre de la página web", fg="black", bg="#0f9b0f", font=('Arial', 15, 'bold'))
    name_label.pack(pady=2)

    namepages_entry = Entry(window_pages)
    namepages_entry.pack(pady=1)
    
    path_label = Label(window_pages, text="URL de la página web", fg="black", bg="#0f9b0f", font=('Arial', 15, 'bold'))
    path_label.pack(pady=2)

    pathp_entry = Entry(window_pages, width=45)
    pathp_entry.pack(pady=1)

    save_button = Button(window_pages, text="Guardar", bg="black", fg='white', width=10, height=1, command=add_pages)
    save_button.pack(pady=4)

def add_pages():
    name_page = namepages_entry.get().strip()
    url_pages = pathp_entry.get().strip()

    sites[name_page] = url_pages
    save_data(name_page, url_pages, "pages.txt")
    namepages_entry.delete(0, "end")
    pathp_entry.delete(0, "end")
def save_data(key, value, file_name):
    try:
        with open(file_name, 'a') as f:
            f.write(key +"," + value + "\n")
    except FileNotFoundError:
        file = open(file_name, 'a')
        file.write(key + "," + value + "\n")

#Funcion para saber que paginas se han agregado

def talk_pages():
    if bool(sites) == True:
        talk("Has agregado las siguientes páginas web")
        for site in sites:
            talk(site)
    else:
        talk("Aún no has agregado ninguna página web, puedes agregarla con el botón de agregar páginas")

#Funcion para agregar un contacto
def open_w_contacts():
    global namecontact_entry, phone_entry
    window_contacts = Toplevel()
    window_contacts.title("Agregar un contacto")
    window_contacts.configure(bg="#0f9b0f")
    window_contacts.geometry("300x300")
    window_contacts.resizable(0,0)

    title_label = Label(window_contacts, text="Agregar un contacto", fg="black", bg="#0f9b0f", font=('Arial', 15, 'bold'))
    title_label.pack(pady=3)
    name_label = Label(window_contacts, text="Nombre del contacto", fg="black", bg="#0f9b0f", font=('Arial', 15, 'bold'))
    name_label.pack(pady=2)

    namecontact_entry = Entry(window_contacts)
    namecontact_entry.pack(pady=1)
    
    path_label = Label(window_contacts, text="Número del contacto", fg="black", bg="#0f9b0f", font=('Arial', 15, 'bold'))
    path_label.pack(pady=2)

    phone_entry = Entry(window_contacts, width=45)
    phone_entry.pack(pady=1)

    save_button = Button(window_contacts, text="Guardar", bg="black", fg='white', width=10, height=1, command=add_contacts)
    save_button.pack(pady=4)

def add_contacts():
    name_contact = namecontact_entry.get().strip()
    phone = phone_entry.get().strip()

    contacts[name_contact] = phone
    save_data(name_contact, phone, "contacts.txt")
    namecontact_entry.delete(0, "end")
    phone_entry.delete(0, "end")
#Funcion para saber que contactos se han agregado
def talk_contacts():
    if bool(contacts) == True:
        talk("Has agregado los siguientes contactos")
        for cont in contacts:
            talk(cont)
    else:
        talk("Aún no has agregado ningún contacto, puedes agregarlo con el botón de agregar contactos")


def give_me_name():
    talk("Hola, ¿cómo te llamas?")
    name = listen()
    name = name.strip()
    talk(f"Bienvenido {name}")

    try:
        with open("name.txt", 'w') as f:
            f.write(name)
    except FileNotFoundError:
        file = open("name.txt", 'w')
        file.write(name)


def say_hello():

    if os.path.exists("name.txt"):
        with open("name.txt") as f:
            for name in f:
                talk(f"Hola, bienvenido {name}")
    else:
        give_me_name()


def thread_hello():
    t = tr.Thread(target=say_hello)
    t.start()


thread_hello()

#botones de  cambio de voz

button_voice_mx = Button(main_window, text ="Voz 1", fg="white", bg="#c31432",
                        font=("Arial", 14, "bold"), command=mexican_voice)
button_voice_mx.place(x=700, y=74, width=150, height=30)
button_voice_es = Button(main_window, text ="Voz 2", fg="white", bg="#D3CCE3",
                        font=("Arial", 14, "bold"), command=spanish_voice)
button_voice_es.place(x=700, y=114, width=150, height=30)
button_voice_us = Button(main_window, text ="Voz 3", fg="white", bg="#0f9b0f",
                        font=("Arial", 14, "bold"), command=english_voice)
button_voice_us.place(x=700, y=154, width=150, height=30)

#botones para que poli nos escuche

button_listen = Button(main_window, text ="Escuchar", fg="white", bg="#CF8BF3",
                        font=("Arial", 14, "bold"), width= 20, height=2, command=run_poli)
button_listen.pack(pady=10)

#botones para que nos hable

button_speak = Button(main_window, text ="Hablar", fg="white", bg="#41295a",
                        font=("Arial", 14, "bold"), command=read_and_talk)
button_speak.place(x=700, y=240, width=150, height=30)

#Botones para agregar y ver lo que se a agregado

button_add_pages = Button(main_window, text ="Agregar páginas", fg="white", bg="#41295a",
                        font=("Arial", 12, "bold"), command=open_w_pages)
button_add_pages.place(x=700, y=360, width=150, height=30)

button_add_contacts = Button(main_window, text ="Agregar contactos", fg="white", bg="#41295a",
                        font=("Arial", 11, "bold"), command=open_w_contacts)
button_add_contacts.place(x=700, y=400, width=150, height=30)

button_tell_page = Button(main_window, text ="Páginas agregadas", fg="white", bg="#41295a",
                        font=("Arial", 10, "bold"), command=talk_pages)
button_tell_page.place(x=700, y=440, width=150, height=30)

button_speak = Button(main_window, text ="Contactos agregados", fg="white", bg="#41295a",
                        font=("Arial", 10, "bold"), command=talk_contacts)
button_speak.place(x=700, y=480, width=150, height=30)

main_window.mainloop()
