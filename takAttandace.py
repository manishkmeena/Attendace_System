import cv2
import tkinter as tk
import os
import math
import statistics as stats
import pickle
import pandas as pd
import numpy as np
import datetime as dt
import face_recognition as fr
from sklearn import neighbors
from PIL import Image
from PIL import ImageTk
import mysql.connector as con
from mysql.connector import errorcode

TRAIN_DIR = os.getcwd()+"/faceData/trained/trainedmodel.clf"
HAARCASSCADE = os.getcwd()+"/"+"haarcascade_frontalface.xml"
DATA_FILE = os.getcwd()+"/faceData/datafile.pkl"
CAMERA_LATENCY = 10
ACCURACY = 11
WIDTH = 0 
HEIGHT = 0

dbs=con.connect(host='localhost',user='root',passwd='')
c=dbs.cursor()
c.execute("USE record")


class FaceCam:
    def __init__(self, video_source = 0):
        self.vid = cv2.VideoCapture(0)
        if not self.vid.isOpened():
            raise ValueError("Unable to open the camera")
        
        self.fd = cv2.CascadeClassifier(HAARCASSCADE)

        # get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        WIDTH = self.width
        HEIGHT = self.height
        
    def get_frame(self):
        if self.vid.isOpened():
            r, img = self.vid.read()
            if r:
                g_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                o_img = img.copy()
                f = self.fd.detectMultiScale(g_img)
                try:
                    (x, y, w, h) = f[0]
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
                    return (r, cv2.cvtColor(img, cv2.COLOR_BGR2RGB), o_img, True, (x, y))
                except IndexError:
                    pass
                except:
                    pass
                return (r, cv2.cvtColor(img, cv2.COLOR_BGR2RGB), o_img, False, (None, None))
            else:
                return (r, None, None, False, (None, None))
        else:
            return (False, None, None, False, (None, None))
        
    def __del__(self):
        if self.vid.isOpened():
            cv2.destroyAllWindows()
            self.vid.release()

class App:
    def __init__(self,window,window_title,video_source):
        self.window=window
        self.window.title(window_title)
        self.dataexists=self.helper_data_exists()
        self.tick=cv2.imread('green_tick.png')

        self.vid=FaceCam(video_source)
        self.name_data=[]

        self.heading=tk.Label(self.window,text='Green check represents attendance marked.',font=22)
        self.heading.pack()

        self.canvas=tk.Canvas(self.window,width=self.vid.width,height=self.vid.height)
        self.canvas.pack()

        self.close=tk.Button(self.window,text='Close',command=self.closeWin,
                             bg='lightgray',font=12,padx=5)
        self.close.pack()

        self.process=True

        self.delay=CAMERA_LATENCY
        self.update()

        self.window.mainloop()
    def closeWin(self):
        self.vid.__del__()
        self.window.destroy()
        
    def helper_data_exists(self):
        if os.path.exists(DATA_FILE) and os.path.isfile(DATA_FILE):
            return True
        return False

    def load_model(self):
        clf=None
        try:
            pickle_in=open(TRAIN_DIR,'rb')
            clf=pickle.load(pickle_in)
            return clf
        except:
            raise ValueError('Trained data not found!')
            exit()

    def run_recognize(self,model,img):
        if self.process:
            self.process=not self.process
            face_bounds=fr.face_locations(img)
            if not len(face_bounds)==1:
                return
            try:
                face_encodings=fr.face_encodings(img,face_bounds)[0]
                res=model.predict([face_encodings])
                return res
            except:
                pass
        else:
            self.process=not self.process
    def fireOnDB(self,name,currdate):

        c.execute("SELECT *FROM attend")
        dbDates=[]
        dbColNames=[]
        for i in c:
            dbDates.append(i[0])
        c.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='attend'")
        for i in c:
            dbColNames.append(i[0])
        
        print('currdate',currdate)
        if not os.path.exists(DATA_FILE) and os.path.isfile(DATA_FILE):
            raise ValueError("Data File not found")
            return
        print('DBCol',dbColNames)
        P = pd.read_pickle(DATA_FILE)
        localColName=P.columns
        for n in localColName:
            if n not in dbColNames:
                c.execute("ALTER TABLE attend ADD {} VARCHAR(11) NOT NULL DEFAULT 'A' AFTER {}".format(name,dbColNames[-1]))

        #checkDate available in db or not,if not then add
        strDates=[]
        for d in dbDates:
            strDates.append(str(d))
        print('STR DATES',strDates)
        if currdate in strDates:
            print('DATE {} in strDates'.format(currdate))
            pass
        else:
            print('DATE {} NOT in strDates'.format(currdate))
            print('Adding new Date')
            enq=''
            for d in dbColNames:
                enq=enq+d+','

            rowVal='DATE'+'('+str("'")+currdate+str("'")+')'

            for i in range(len(dbColNames)-1):
                rowVal=rowVal+','+str("'")+'A'+str("'")

            print("INSERT INTO attend({}) VALUES ({})".format(enq[:-1],rowVal))    
            c.execute("INSERT INTO attend({}) VALUES ({})".format(enq[:-1],rowVal))
            dbs.commit()

        #Get the value of time of present of corresponding person from datafile.pkl
        value=P[name][currdate]
        print('localDBValue',value)
        c.execute("SELECT {} FROM attend WHERE DATE='{}'".format(name,currdate))
        curStatus=None
        for i in c:
            curStatus=i[0]
        print(curStatus)
        if curStatus=='A':
            c.execute("UPDATE attend SET {}={} WHERE DATE={}".format(name,str("'")+value+str("'"),str("'")+currdate+str("'")))
            dbs.commit()
            print('Updated')
    
    def update(self):
        r,frame,o_image,clickable,(fx,fy)=self.vid.get_frame()
        if r:
            self.photo=ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0,0,image=self.photo,anchor=tk.NW)
            x_off=fx
            y_off=fy
            
            if clickable:
                
                ## Todo
                P = None
                todays_date ='2019-11-29'
                #dt.datetime.now().date()
                if not self.dataexists:
                    index = pd.date_range(todays_date, periods=30, freq='D')
                    P = pd.DataFrame(index=index)
                    #print('P',P)
                else:
                    P = pd.read_pickle(DATA_FILE)
                    #print('P',P)
                model = self.load_model()
                name = self.run_recognize(model, o_image)
                
                if not name is None:
                    self.name_data.append(name[0])
                    print('pre name-',self.name_data)
                    print('u1')
                if len(self.name_data) >= ACCURACY:
                    print('u2')
                    name = stats.mode(self.name_data)
                    name = name.replace('.', ' ')
                    print("[INFO] Marking attendance for {} on data {}".format(name, todays_date))
                    self.name_data = []
                    print('P col',P.columns)
                    if not name in P.columns:
                        print('Col',name)
                        P[name] = 'A'
                    if P[name][todays_date] is 'A':
                        P[name][todays_date] = str(dt.datetime.now().time()).split('.')[0]
                        P.to_pickle(DATA_FILE)
                        print('CHECK')
                        self.fireOnDB(name,str(todays_date))
                        try:
                            frame[x_off:x_off+len(self.tick), x_off:x_off+len(self.tick)] = self.tick
                        except:
                            pass
                    else:
                        try:
                            frame[y_off:y_off+len(self.tick), x_off:x_off+len(self.tick)] = self.tick
                        except:
                            pass
                    self.photo = ImageTk.PhotoImage(image = Image.fromarray(frame))
                    self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
                    
        self.window.after(self.delay, self.update)

def begin(vs=0):
    App(tk.Toplevel(),"Attendance",vs)


#fireOnDB('mkm','2019-11-03')
