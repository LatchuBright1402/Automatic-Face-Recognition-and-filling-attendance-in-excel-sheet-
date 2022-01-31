import cv2
import numpy as np
import requests
import json
import argparse
import signal
import logging
import datetime,time
face_api ="http://localhost:5000/inferImage?retuenFaceId=true"
compare_api ="http://localhost:5000/compareFaces"
#initialize logger
logger = logging.getLogger('Attendance')
logger.setLevel(logging.DEBUG)
#create console handler with higher log level
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)
#attendance register
att_reg=[]
try:
    att_reg=json.loads(open('att_reg').read())
except:
    pass
#initialize database
db = {}
try:
    db=json.loads(open('att_db').read())
except:
    pass
#parse arguments
parser = argparse.ArgumentParser(description='Awesome Attendance System')
parser.add_argument('--enroll',action='store_true',help='Enable enrollment of unknown faces')
parser.add_argument('--src', action='store', default=0, nargs='?', help='Set video source; default is usb webcam')
parser.add_argument('--w', action='store', default=320, nargs='?', help='Set video width')
parser.add_argument('--h', action='store', default=240, nargs='?', help='Set video height')
args = parser.parse_args()
# start the camera
cap = cv2.VideoCapture(args.src)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.h)
ret, frame = cap.read()
# catch exit signal
def signal_handler(signal, frame):
    if args.enroll:
        logger.info("Saving Attendance DB")
        with open('att_db','w') as att:
            att.write(json.dumps(db,2))

            logger.info("Saving attendance")
            with open('att_log','w') as att:
                att.write(json.dumps(att_reg))

    exit(0)
signal.signal(signal.SIGINT, signal_handler)
# enroll a new face into db
def enroll(embedding):
    name = input("New face detected, enter name\n")
    if name != "x":
        db[name] = embedding
        print("Enrolled %s into db!"%name)
# search for a face in the db
def identify_face(embedding):
    for name, emb in db.items():
        face_pair = {"faceA":emb, "faceB":embedding}
        cmp_r = requests.post(compare_api, data=json.dumps(face_pair))
        cmp_r = cmp_r.json()
        logger.debug(cmp_r)
        if cmp_r["same"]:
            return name

return None
# last attendance
def mins_since_last_log():
    return ((datetime.datetime.now() - datetime.datetime.strptime(att_reg[-1]['time'], '%Y-%m-%d %H:%M:%S')).seconds/60)
# mark attendance
def mark_present(name):
    if len(att_reg) == 0:
        logger.info("Detected %s"%name)
        stime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        att = {'name':name,'time':stime}
        att_reg.append(att)
        return
        if att_reg[-1]['name'] != name or mins_since_last_log() & amp;amp;amp;amp;amp;amp;amp;gt; 1:
            logger.info("Detected %s"%name)
            stime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            att = {'name':name,'time':stime}
            att_reg.append(att)
# start processing
while True:
_, framex = cap.read()
key = cv2.waitKey(50) &amp;amp;amp;amp;amp;amp;amp;amp; 0xFF

frame = cv2.resize(framex, (args.w,args.h))

r, imgbuf = cv2.imencode(".jpg", frame)
image = {'pic':bytearray(imgbuf)}

r = requests.post(face_api, files=image)
result = r.json()

if len(result) &amp;amp;amp;amp;amp;amp;amp;gt; 1:
faces = result[:-1]
diag = result[-1]['diagnostics']

for face in faces:
rect, embedding = [face[i] for i in ['faceRectangle','faceEmbeddings']]
x,y,w,h = [rect[i] for i in ['left', 'top', 'width', 'height']]
cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0),1,8)
name = identify_face(embedding)
if not name is None:
cv2.putText(frame, name, (x,y+22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255))
mark_present(name)
break
else:
if args.enroll:
enroll(embedding)

cv2.putText(frame, diag['elapsedTime'], (0,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255))

cv2.imshow("frame", frame)
if key == ord('q'):
break;

print("Exit")
