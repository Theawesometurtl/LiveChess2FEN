from flask import Blueprint, Flask, render_template, request, flash, Response
import cv2
import datetime, time
import os, sys
import numpy as np
from threading import Thread
from .lc2fen import main

views = Blueprint('views', __name__)

@views.route('/')
def home():
    


    return render_template("template.html", text = "FEN test")


global capture,rec_frame, grey, switch, neg, rec, out 
capture=0
grey=0
neg=0
switch=1
rec=0





camera = cv2.VideoCapture(0)

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)


def gen_frames():  # generate frame by frame from camera
    global out, capture,rec_frame
    while True:
        success, frame = camera.read() 
        if success:
            if(grey):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if(neg):
                frame=cv2.bitwise_not(frame)    
            if(capture):
                capture=0
                now = datetime.datetime.now()
                p = os.path.sep.join(['website\shots', "shot_{}.png".format(str(now).replace(":",''))])
                cv2.imwrite(p, frame)
                script_arguments = ["-h","./website\shots/shot_{}.png".format(str(now).replace(":",'')), "BL", prevFEN, ]
                sys.argv = script_arguments
                main()

            
            if(rec):
                rec_frame=frame
                frame= cv2.putText(cv2.flip(frame,1),"Recording...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                frame=cv2.flip(frame,1)
            
                
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass

    
    
@views.route('/video_feed')
def video_feed():
    print("video")
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@views.route('/requests',methods=['POST','GET'])
def tasks():
    print("capture")
    global switch,camera, prevFEN
    if request.method == 'POST':
        prevFEN = request.form.get('prevFEN')

        if len(prevFEN) < 16:
            flash('too short', category="error")
        else:
            flash('worked!', category="success")
        global capture
        capture=1
        
        # if request.form.get('click') == 'Capture':
        if  request.form.get('grey') == 'Grey':
            global grey
            grey=not grey
        elif  request.form.get('neg') == 'Negative':
            global neg
            neg=not neg
        elif  request.form.get('face') == 'Face Only':
            global face
            face=not face 
            if(face):
                time.sleep(4)   
        elif  request.form.get('stop') == 'Stop/Start':
            
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
                
            else:
                camera = cv2.VideoCapture(0)
                switch=1
        elif  request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec= not rec
            if(rec):
                now=datetime.datetime.now() 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
                #Start new thread for recording the video
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()
                          
                 
    elif request.method=='GET':
        return render_template('template.html')
    return render_template('template.html')

    
# camera.release()
# cv2.destroyAllWindows()     