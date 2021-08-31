import cv2
import numpy as np 
from tensorflow.keras.models import load_model
from PIL import Image
import imutils
import argparse
from warning_sound import play_sound
from email_alert import email_alert 
#import datetime
import time
from flask import Flask, render_template, Response

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

def mean_squared_loss(x1,x2):
  difference=x1-x2
  a,b,c,d,e=difference.shape
  n_samples=a*b*c*d*e
  sq_difference=difference**2
  Sum=sq_difference.sum()
  distance=np.sqrt(Sum)
  mean_distance=distance/n_samples
  return mean_distance

model=load_model("saved_model.h5")
cap = cv2.VideoCapture("fight.mp4")
print(cap.isOpened())

def process():
    while cap.isOpened():
      imagedump=[]
      ret,frame=cap.read()
    
      for i in range(10):
        try:
          ret, frame = cap.read()
          image = imutils.resize(frame, width=1000, height=1000, inter=cv2.INTER_AREA)
          frame=cv2.resize(frame, (227,227), interpolation = cv2.INTER_AREA)
          frame1=cv2.resize(frame, (500,500), interpolation = cv2.INTER_AREA)
          gray=0.2989*frame[:,:,0]+0.5870*frame[:,:,1]+0.1140*frame[:,:,2]
          gray=(gray-gray.mean())/gray.std()
          gray=np.clip(gray,0,1)
          imagedump.append(gray)
        except AttributeError:
          continue
            
      imagedump=np.array(imagedump)
      imagedump.resize(227,227,10)
      imagedump=np.expand_dims(imagedump,axis=0)
      imagedump=np.expand_dims(imagedump,axis=4)
    
      output=model.predict(imagedump)
      loss=mean_squared_loss(imagedump,output)
      print(loss)
      try:
        if frame.any()==None:
            print("none")
      
        if loss>0.00068:
            print('Abnormal Event Detected')  
            play_sound()
            
      #     x=datetime.datetime.now()
            #localtime = time.asctime( time.localtime(time.time()) )
            #message ="WARNING!!! Violence detected \n Local current time :"+str(localtime)
            #email_alert("Video Surveillance",message,"violencedetected123@gmail.com")
            cv2.putText(frame1,"Abnormal Event",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2,cv2.LINE_AA)
        if cv2.waitKey(10)& 0xFF==ord('q'):
            break
      except AttributeError:
        break
    
      #cv2.imshow('test',image)
     
      ret, buffer = cv2.imencode('.jpg',frame1) #compress and store image to memory buffer
      frame1 = buffer.tobytes()
      yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame1 + b'\r\n') #concat frame one by one and return frame 

    cap.release()
    cv2.destroyAllWindows()

@app.route('/video_feed')
def video_feed():
    #Video streaming route
    return Response(process(),mimetype='multipart/x-mixed-replace; boundary=frame')
        
if __name__ == "__main__":
    app.run()
