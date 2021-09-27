import cv2
import csv
from cvzone.HandTrackingModule import HandDetector
import cvzone
import time

#video for opening webcam
cap = cv2.VideoCapture(0)

#detecting the hand by giving detecting confidence 
detector = HandDetector(detectionCon=0.8)

#each MCQ will be treated as an object and defining variables to store data from CSV file
class MCQ():
    def __init__(self,data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])

        self.userAns = None         #this variable is to store the user answer

    # method to check we clicked any option or not
    def update(self, cursor, bboxs):

        for x, bbox in enumerate(bboxs):
            x1,y1,x2,y2 = bbox
            # checking wheather cursor is inside box 
            if x1<cursor[0]<x2 and y1<cursor[1]<y2:
                 self.userAns = x+1
                 cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),cv2.FILLED)  #marking the answer as green
                  

# import csv file data
pathCSV = "mcqs.csv"
with open(pathCSV,newline='\n') as f:
    reader = csv.reader(f)
    dataALL = list(reader)[1:]   # converting data into list and we don't want the heading 
# print(dataALL)

# Create object for each MCQ
mcqList = []
for q in dataALL:
    # creating an object and storing it into list
    mcqList.append(MCQ(q))
#print(len(mcqList))

qNo = 0
qTotal = len(dataALL)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img,flipType=False)
    if qNo<qTotal:
        mcq = mcqList[qNo]

        #bounding box variable is to determine the size of rectangle dynamically that is containing the question
        img, bbox = cvzone.putTextRect(img,mcq.question,[100,100],2,2, offset=20, border=2) # giving position,scale and thickness
        img, bbox1 = cvzone.putTextRect(img,mcq.choice1,[100,250],2,2, offset=20, border=2)
        img, bbox2 = cvzone.putTextRect(img,mcq.choice2,[400,250],2,2, offset=20, border=2)
        img, bbox3 = cvzone.putTextRect(img,mcq.choice3,[100,400],2,2, offset=20, border=2)
        img, bbox4 = cvzone.putTextRect(img,mcq.choice4,[400,400],2,2, offset=20, border=2)

        if hands:
            lmList = hands[0]['lmList']
            cursor = lmList[8]  # 8 is provided by mediapipe module which means tip of index finger and 12 is for middle finger
            length, info = detector.findDistance(lmList[8],lmList[12])
            #print(length)
            if length<60:
                #print("clicked")
                mcq.update(cursor,[bbox1,bbox2,bbox3,bbox4])
                #print(mcq.userAns)
                # to make a click only once
                if mcq.userAns is not None:
                    time.sleep(0.3)
                    qNo += 1  
    else:
        score =0
        #to check if the answer is correct or not
        for mcq in mcqList:
            if mcq.answer ==  mcq.userAns: 
                score += 1
        score = round((score/qTotal)*100,2)
        img, _ = cvzone.putTextRect(img,"Quiz Completed",[250,300],2,2, offset=15, border=2)
        img, _ = cvzone.putTextRect(img,f'Your Score: {score}%',[700,300],2,2, offset=15, border=2)

    # draw progress bar
    barValue = 150 + (950//qTotal)*qNo
    cv2.rectangle(img,(150,600),(barValue,650),(0,255,0),cv2.FILLED)
    cv2.rectangle(img,(150,600),(1100,650),(255,0,255),5)

    #putting box for percentage
    img, _ = cvzone.putTextRect(img,f'{round((qNo/qTotal)*100)}%',[1130,635],2,2, offset=15, border=2)

    cv2.imshow("Img",img)
    cv2.waitKey(1) # delay of 1 millisecond
    