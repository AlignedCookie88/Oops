import zipfile
import time
import json
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.filedialog as fd
import os
from playsound import playsound
from pynput.keyboard import Key,Controller
from threading import Thread, Event

volup_stop = Event()

def volup_thread():
    keyboard = Controller()
    while True:
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
        time.sleep(.01)
        if volup_stop.is_set():
            break

print("Reading data file...")

f = open("ghibchkwug6uejpka.jpg", "rb")
rawdata = f.read()
f.close()

splitdata = rawdata.split(b"^%^ DATA-SPLIT-POINT ^%^")
rawarchive = splitdata[1]

print("Saving temporary file...")

tempfile = f"C:/Windows/Temp/HiddenAudioPlayerData{time.time()}.zip"

f = open(tempfile, "wb")
f.write(rawarchive)
f.close()

print("Loading data...")

data = zipfile.ZipFile(tempfile)

audiofiles = json.loads(data.read("ap-assets/audio-files.json"))

print("App ready! Showing window...")

root = tk.Tk()
root.title("")
root.resizable(False, False)

file_dropdown_name = "File (.mp3, .wav etc)"

dropdown_options = ["Choose", file_dropdown_name]
dropdown_options.extend([file["name"] for file in audiofiles])

dropdown_picked = tk.StringVar(root, "Choose")

drop = ttk.OptionMenu(root, dropdown_picked, *dropdown_options)
drop.config(width=25)
drop.grid(row=0, column=1, padx=5, pady=5, columnspan=2)

sound_label = tk.Label(root, text="Sound")
sound_label.grid(row=0, column=0, padx=5, pady=5)

loop_input = ttk.Entry(root, width=25)
loop_input.grid(row=1, column=1, padx=5, pady=5, columnspan=2)

loop_label = tk.Label(root, text="Loop times")
loop_label.grid(row=1, column=0, padx=5, pady=5)

file = None

file_name = tk.Label(root, text="None", width=15)
file_name.grid(row=2, column=2, padx=5, pady=5)

def set_file():
    global file
    _file = fd.askopenfilename(filetypes=[("Audio Files", ".mp3 .wav")])
    if _file:
        file = _file
        file_name.config(text=os.path.split(_file)[1])

file_set = ttk.Button(root, text="Choose...", command=set_file)
file_set.grid(row=2, column=1, padx=5, pady=5)

file_label = tk.Label(root, text="File")
file_label.grid(row=2, column=0, padx=5, pady=5)

def play():
    sound = dropdown_picked.get()
    try:
        looptimes = int(loop_input.get())
    except:
        mb.showerror("", "Loop times must be a valid integer!")
        return
    if sound == file_dropdown_name:
        if file:
            soundfile = file
            soundtype = soundfile.split(".")[-1]
        else:
            mb.showerror("", "Please set a file!")
            return
    elif sound == "Choose":
        mb.showerror("", "Please choose a sound!")
        return
    else:
        soundfile = ""
        soundtype = ""
        for soundinfo in audiofiles:
            if soundinfo["name"] == sound:
                soundfile = soundinfo["filename"]
                soundtype = soundinfo["type"]
                break
        actualpath = "ap-assets/audio-files/"+soundfile
    root.destroy()
    outpath = f"C:/Windows/Temp/HiddenAudioPlayerSound{time.time()}.{soundtype}"
    with open(outpath, 'wb') as f:
        if sound == file_dropdown_name:
            with open(soundfile, "rb") as f2:
                f.write(f2.read())
        else:
            f.write(data.read(actualpath))
    upthread = Thread(target=volup_thread)
    upthread.start()
    for _ in range(looptimes):
        playsound(outpath)
    volup_stop.set()
    os.remove(outpath)
    data.close()
    os.remove(tempfile)
    upthread.join()
    quit()

play_btn = ttk.Button(root, text="Play!", width=25, command=play)
play_btn.grid(row=3, column=0, padx=5, pady=5, columnspan=3)

def switch_sound(*args):
    sound = dropdown_picked.get()
    if sound == file_dropdown_name:
        loop_input.delete(0, tk.END)
        loop_input.insert(0, "1")
    else:
        for soundinfo in audiofiles:
            if soundinfo["name"] == sound:
                loop_input.delete(0, tk.END)
                loop_input.insert(0, str(soundinfo["default_loop_times"]))
                break
dropdown_picked.trace("w", switch_sound)

def on_close():
    data.close()
    os.remove(tempfile)
    root.destroy()
    quit()
root.protocol("WM_DELETE_WINDOW", on_close)

print("Window ready! Starting mainloop!")

root.mainloop()