import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog
import tkinter.messagebox as tkm
import time
from tkinter.scrolledtext import ScrolledText

import threading
import os
import queue
import sounddevice as sd
import vosk
import sys

import json
import unicodedata

import ctypes
import numpy as np

root = tk.Tk()
menubar = tk.Menu(root)

root.title("Kanzo - memopad with a stenographer")
root.config(menu=menubar)
root.geometry("640x480")

iconfile = './favicon.ico'
root.iconbitmap(default=iconfile)

fontStyle = tkFont.Font("", size=15)

label = tk.Label(root,text="",font=fontStyle)
label.pack(side = tk.BOTTOM,anchor = tk.SW,expand=tk.NO)

textbox = ScrolledText(root, font=fontStyle)
textbox.pack(fill=tk.BOTH, expand=tk.YES)

q = queue.Queue()

stopFlag = False

model = tk.StringVar()
paths = os.listdir("models/")
models=[]
#print(models)
for m in paths:
    if os.path.isdir("models/" + m):
        models.append(m)
        print(m)
model.set("models/" + models[0])

device = tk.IntVar()
devices = sd.query_devices()
hostapis = sd.query_hostapis()

def restartThread():
    global stopFlag
    stopFlag=True

def addtext(additive):
    textbox.insert("end",additive)
    if isAutoSc.get():
        textbox.see("end")

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata)

def get_east_asian_width_count(text):
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 2
        else:
            count += 1
    return count

def count_double_byte_str(text, len):
    count = 0
    hcount = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 2
            hcount += 1
        else:
            count += 1
            hcount += 1
        # lenと同じ長さになったときに抽出完了
        if count > len:
            break
    return hcount


def is_japanese(string):
    for ch in string:
        name = unicodedata.name(ch) 
        if "CJK UNIFIED" in name \
        or "HIRAGANA" in name \
        or "KATAKANA" in name:
            return True
    return False

def runVosk():
    #try:
    # args=(model.get(),device.get())
    global stopFlag
    ctypes.windll.ole32.CoInitialize(None)
    while True:
        try:
            label['text']="Being ready to recognize..."
            stopFlag=False
            voskmodel = vosk.Model(model.get())
            device_info = sd.query_devices(device.get())
            samplerate = int(device_info['default_samplerate'])
            channels = int(device_info["max_input_channels"])
            #print("samplerate " + str(samplerate))
            with sd.InputStream(samplerate=samplerate, blocksize = 8000, device=device.get(), dtype='int16',channels=channels, callback=callback):
                print('#' * 80)
                print('Press Ctrl+C to stop the recording')
                print('#' * 80)

                rec = vosk.KaldiRecognizer(voskmodel, samplerate)
                while True:
                    if stopFlag:
                        print("stopflag")
                        break
                    rdata = q.get()
                    #print(rdata)
                    data = np.array(rdata[:,0], dtype='int16')
                    #print(data)
                    bdata = data.tobytes()
                    if rec.AcceptWaveform(bdata):
                        result = rec.Result()
                        #print(type(result))
                        resjson = json.loads(result)
                        #print(resjson["text"])
                        resultText = resjson["text"]
                        if len(resultText) > 0:
                            if is_japanese(resultText):
                                resultText = resultText.replace(' ', '')
                            addtext(resultText + "\r\n" )
                    else:
                        #print(rec.PartialResult())
                        result = rec.PartialResult()
                        resjson = json.loads(result)
                        #print(resjson["partial"])
                        resText = "Recognizing: " + resjson["partial"]
                        strcap = (root.winfo_width() - 100) / fontsize.get() * 2
                        strlen = get_east_asian_width_count(resText)
                        #print(str(strcap) + ", " + str(strlen))
                        if strcap < strlen:
                            cutlen = strlen - strcap
                            cuthlen = count_double_byte_str(resText,cutlen)
                            resText = resText[cuthlen:]
                        label['text']=resText
        except Exception as e:
            print("exception")
            print(e)
            label['text']="ERROR:cannot open device, try other device"
            time.sleep(2)
            pass
"""
    except KeyboardInterrupt:
        print('\nDone')
    except Exception as e:
        print("exception")
        pass
"""



# Model Menu
modelMenu = tk.Menu(menubar, tearoff=0)
for m in models:
    modelMenu.add_radiobutton(label = m, command = restartThread, variable = model, value = "models/" + m)

# Device Menu
deviceMenu = tk.Menu(menubar, tearoff=0)
index = 0
print(hostapis[0])
for d in devices:
    api=""
    #print(d, sd._lib.PaWasapi_IsLoopback(index))
    if d["max_input_channels"] > 0:
        for h in hostapis:
            if index in h["devices"]:
                api = h["name"]
        if index == hostapis[0]["default_input_device"]:
            device.set(index)
        deviceMenu.add_radiobutton(label = d["name"] + " --- " + api, command = restartThread, variable = device, value = index)
    index += 1


#Fontsize Menu
fontsize = tk.IntVar()
fontsize.set(15) #as default
def setFont():
    fontStyle.configure(size=fontsize.get())
    pass
fontMenu = tk.Menu(menubar, tearoff = 0)
fontMenu.add_radiobutton(label = "Small 15pt", command = setFont, variable = fontsize, value = 15)
fontMenu.add_radiobutton(label = "Mid 25pt", command = setFont, variable = fontsize, value = 25)
fontMenu.add_radiobutton(label = "Large 35pt", command = setFont, variable = fontsize, value = 35)


#Other Menu
isTop = tk.BooleanVar() 
isTop.set(False)
isAutoSc =tk.BooleanVar()
isAutoSc.set(False)
def setTop():
    root.attributes("-topmost", isTop.get())
def showAbout():
    #tkm.showinfo('ダイアログのタイトル', '普通のダイアログ')
    dialog = tk.Toplevel()
    dialog.title("About Kanzo")
    dialog.geometry("300x150")
    alabel = tk.Label(dialog,text="Kanzo",font=("",20,"bold"))
    alabel.pack()
    alabel = tk.Label(dialog,text="(c) @memukuge",font=("",12,""))
    alabel.pack()
    alabel = tk.Label(dialog,text="https://github.com/memukuge/kanzo",font=("",9,"bold"))
    alabel.pack()


    pass
def saveAs():
    filename = filedialog.asksaveasfilename(
    title = "Save As",
    filetypes = [("Plain Text", ".txt") ], # ファイルフィルタ
    initialdir = "./", # 自分自身のディレクトリ
    defaultextension = "txt"
    )
    #print(textbox.get("1.0", tk.END))
    text_file = open(filename, "w")
    n = text_file.write(textbox.get("1.0", tk.END))
    text_file.close()
otherMenu = tk.Menu(menubar,tearoff=0)
otherMenu.add_checkbutton(label="Show always", command=setTop, variable = isTop)
otherMenu.add_checkbutton(label="Auto Scroll", variable = isAutoSc)
otherMenu.add_command(label='Save Text As', command=saveAs)
otherMenu.add_separator()
otherMenu.add_command(label='About', command=showAbout)
#otherMenu.add_command(label='Exit', command=quit)

# Add
menubar.add_cascade(label='Model', menu=modelMenu)
menubar.add_cascade(label='Device', menu=deviceMenu)
menubar.add_cascade(label='Font', menu=fontMenu)
menubar.add_cascade(label='Other', menu=otherMenu)


thread = threading.Thread(target=runVosk)
thread.setDaemon(True)
thread.start()

#runThread(model.get(),device.get(),thread)
root.mainloop()




