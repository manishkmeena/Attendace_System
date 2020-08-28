import tkinter as tk
from tkinter import messagebox
import cv2
import PIL
import os
from time import sleep
from PIL import Image
from PIL import ImageTk
import face_recognition as fr

SHOT_COUNT=5
CAMERA_LATENCY=5
HAARCASSCADE=os.getcwd()+"/"+"haarcascade_frontalface.xml"
DIRNAME=os.getcwd()+"/rawImages/"
chk=0

class FaceCam:
    def __init__(self,video_source):
    #open the video source
        self.vid=cv2.VideoCapture(video_source)
        
        if not self.vid.isOpened():
            raise ValueError("Unable to open Camera")
            #messagebox.showwarning('Warning!',"Unable to open Video Source")

        self.fd=cv2.CascadeClassifier(HAARCASSCADE)

        #Get video source width and height
        self.width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            r,img=self.vid.read()
            
            if r:
                g_img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                o_img=img.copy()
                f=self.fd.detectMultiScale(g_img)
                try:
                    (x,y,w,h)=f[0]
                    cv2.rectangle(img,(x,y),(x+w,y+h),(87,168,227),1)
                    return(r,cv2.cvtColor(img,cv2.COLOR_BGR2RGB),o_img,True)
                except IndexError:
                    pass
                except:
                    pass
                return(r,cv2.cvtColor(img,cv2.COLOR_BGR2RGB),o_img,False)
            else:
                return(r,None,None,False)
        else:
            return(False,None,None,False)

    def __del__(self):
        if self.vid.isOpened():
            cv2.destroyAllWindows()
            self.vid.release()
            
class App:
    def __init__(self,window,window_title,video_source=0):
        self.window=window
        self.window.title(window_title)
        self.cnt=0
        self.name=""

        #open video source
        self.vid=FaceCam(video_source)

        #lable text
        self.heading=tk.Label(window,text="Capture atleast {} pictures of your face.".format(SHOT_COUNT),font=22)
        self.heading.pack()

        #id entry
        self.nameFrame=tk.Frame(window)
        self.nameFrame.pack()
        self.idLabel=tk.Label(self.nameFrame,text="ID/Name:",font=12)
        self.idLabel.grid(row=0,column=0)
        self.idEntry=tk.Entry(self.nameFrame,font=12)
        self.idEntry.grid(row=0,column=1)
        self.count=tk.Label(window,text="Count={}".format(self.cnt))
        self.count.pack()

        #create a canvas
        self.canvas=tk.Canvas(window,width=self.vid.width,height=self.vid.height)
        self.canvas.pack()

        #button to capture the shot
        self.buttonFrame=tk.Frame(window)
        self.buttonFrame.pack()
        self.capture=tk.Button(self.buttonFrame,text='Capture',command=self.shot,
                               bg='lightgray',font=12,padx=50)
        self.capture.grid(row=0,column=0)

        self.reset=tk.Button(self.buttonFrame,text="Reset",command=self.reset,
                             bg='lightgray',font=12,padx=5)
        self.reset.grid(row=0,column=1)
        self.close=tk.Button(self.buttonFrame,text='Close',command=self.closeWin,
                             bg='lightgray',font=12,padx=5)
        self.close.grid(row=0,column=2)

        #call update after every delay
        self.delay=CAMERA_LATENCY
        self.update()
        
        self.window.mainloop()
    def closeWin(self):
        self.vid.__del__()
        self.window.destroy()

    def helper_create_directory(self,name):
        #first create outer direcory
        try:
            if((os.path.isdir(DIRNAME))==True):
                print("Raw directory exist")
                pass
            else:
                os.mkdir(DIRNAME)
                print("Raw Directory Created")

        except FileExistsError:
            print("Something Wrong")
            pass

        #check for inner directory
        try:
            if((os.path.isdir(DIRNAME+"/"+name+"/"))==True):
                print("Already Name exists")
                return
            else:
                os.mkdir(DIRNAME+"/"+name+"/")
                print('directory created')
        except FileExistsError:
            print('Something Wrong')
            pass

    def shot(self):
        if self.idEntry.get().strip()=="":
            print("Please enter ID/Name")
            messagebox.showinfo("Error!","Must enter ID/Name")
            return
        global chk
        if(chk==0):
            dirList=os.listdir(DIRNAME)
            if(self.idEntry.get().strip() in dirList):
                messagebox.showinfo("Error!","Already Exist,Use a different Name")
                return
            else:
                chk=1
                
        self.name=self.idEntry.get().strip().replace(' ','.')
        directory=DIRNAME+"/"+self.name+"/"
        self.helper_create_directory(self.name)
        r,img,o_img,clickable=self.vid.get_frame()
        if not clickable:
            messagebox.showinfo("Error!","Face not found")
            return
        if r:
            print("Capured")
            self.idEntry.config(state='disabled')
            self.count.config(text="Count={}".format(self.cnt+1))
            saveDir=directory+self.name+"."+str(self.cnt)+".jpg"
            cv2.imwrite(saveDir,o_img)
            self.cnt+=1
        else:
            raise ValueError('Camera not working')
            return

    def reset(self):
        global chk
        self.idEntry.config(state='normal')
        self.idEntry.delete(0,len(self.idEntry.get()))
        self.cnt=0
        chk=0
        self.count.config(text="Count={}".format(0))
        messagebox.showinfo("Alert!","Reset Done")

    def update(self):
        #retrieve frame from video source
        r,frame,o_img,clickable=self.vid.get_frame()

        if r:
            self.photo=ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0,0,image=self.photo,anchor=tk.NW)

        self.window.after(self.delay,self.update)
        
def register(video_source):
    App(tk.Toplevel(),"Register Face",video_source)
#register(0)
