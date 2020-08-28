import tkinter as tk
from tkinter import messagebox
import register_face
import imgProcess
import takAttandace
import genExcel

HEIGHT=210
WIDTH=450

class App:
    def __init__(self,window,window_title):
        self.window=window
        self.window.title(window_title)

        canvas=tk.Canvas(self.window,width=WIDTH,height=HEIGHT)
        canvas.pack()

        shutDown=tk.Button(self.window,text="Shut Down",bg='lightgray',command=self.shutDown)
        shutDown.place(anchor='nw',relx=0.75,rely=0.06,relwidth=0.20)
        
        heading=tk.Label(canvas,text="Select on of the options below:",font=8)
        heading.place(anchor='nw',relx=0.2,rely=0.22)

        beginButton=tk.Button(self.window,text="Start Attendance Mode",bg='lightgray',command=self.attendance)
        beginButton.place(anchor='nw',relx=0.025,rely=0.4,relwidth=0.95)

        registerButton=tk.Button(self.window,text="Register The Face",bg='lightgray',command=self.register)
        registerButton.place(anchor='nw',relx=0.025,rely=0.55,relwidth=0.95)

        processButton=tk.Button(self.window,text='Process Face Data',bg='lightgray',command=self.process)
        processButton.place(anchor='nw',relx=0.025,rely=0.7,relwidth=0.95)

        generateButton=tk.Button(self.window,text='Generate Excel File',bg='lightgray',command=self.generate_excel)
        generateButton.place(anchor='nw',relx=0.025,rely=0.85,relwidth=0.95)
        
        window.mainloop()
        
    def attendance(self):
        takAttandace.begin(0)
    def register(self):
        register_face.register(0)
        
    def process(self):
        imgProcess.processdata()
        
    def generate_excel(self):
        genExcel.generate_excel_file()
        
    def shutDown(self):
        messagebox.showwarning("Warning!","System is Shutting Down")
        exit()
App(tk.Tk(),"Facial Biometric Attendance")
