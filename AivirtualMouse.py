import cv2
import time,  math, numpy as np
import HandTrackingModule as htm
import pyautogui, autopy
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# 웹캠 화면 크기 설정 (640X480)
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3,wCam) # 가로
cap.set(4,hCam) # 세로
pTime = 0
#cTime = 0

# detectionCon을 낮추면 (값을 작게 하면):
# 낮은 신뢰도의 손도 감지되기 시작합니다.
# 더 많은 손이 감지될 수 있으나, 그 중 일부는 정확하지 않을 수 있습니다.

# detectionCon을 높이면 (값을 크게 하면):
# 높은 신뢰도를 갖는 손만이 감지됩니다.
# 낮은 신뢰도의 손은 감지되지 않을 수 있습니다.

# trackCon을 낮추면 (값을 작게 하면):
# 손의 추적이 더 관대해집니다.
# 빠르게 움직이는 손도 일부 추적될 수 있지만, 정확성이 떨어질 수 있습니다.

# trackCon을 높이면 (값을 크게 하면):
# 정확한 손 추적이 이루어집니다.
# 빠르게 움직이는 손도 더 정확하게 추적됩니다.
detector = htm.handDetector(maxHands=1, detectionCon=0.85, trackCon=0.9)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()   #(-63.5, 0.0, 0.5) min max

minVol = -63
maxVol = volRange[1]
print(volRange)
hmin = 50
hmax = 200
volBar = 400
volPer = 0
vol = 0
color = (0,215,255)

# lmList는 손가락 관절의 리스트이고, tipIds는 손가락 끝 부분에 해당하는 관절의 인덱스를 나타냄
tipIds = [4, 8, 12, 16, 20]
mode = ''
active = 0

# 마우스 커서가 화면의 왼쪽 상단으로 이동해도 프로그램이 중단되지 않도록 하는 역할
pyautogui.FAILSAFE = False
while True:
    success, img = cap.read()

    # 좌우 반전
    img = cv2.flip(img, 1)

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
   # print(lmList)
    fingers = []

    if len(lmList) != 0:

        #Thumb
        # tipIds[0]은 엄지 손가락 끝 부분에 해당하는 관절의 인덱스
        # lmList[tipIds[0]][1]은 엄지 손가락 끝 부분의 x 좌표를 나타냅니다.
        # lmList[tipIds[0 - 1]][1]은 엄지 손가락 그 다음 관절의 x 좌표를 나타냅니다.
        # 왼손일 때
        if lmList[tipIds[0]][1] > lmList[tipIds[0 -1]][1]:
            # 왼손 엄지를 폈을 때 1, 접었을 때 0
            if lmList[tipIds[0]][1] >= lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        # 오른손일 때
        elif lmList[tipIds[0]][1] < lmList[tipIds[0 -1]][1]:
            # 오른 손 엄지를 폈을 때 1, 접었을 때 0
            if lmList[tipIds[0]][1] <= lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        # 검지부터 새끼 손까락은 y 좌표를 이용해서 펴졌으면 1 접혔으면 0
        for id in range(1,5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)


      #  print(fingers)
        # 모든 손가락이 접혔을 때
        if (fingers == [0,0,0,0,0]) & (active == 0 ):
            mode='N'
        # 검지손가락만 폈을 때 또는 검지와 중지만 폈을 때
        elif (fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]) & (active == 0 ):
            mode = 'Scroll'
            active = 1
        # 엄지와 검지가 펴졌을 때
        elif (fingers == [1, 1, 0, 0, 0] ) & (active == 0 ):
             mode = 'Volume'
             active = 1
        # 모든 손가락을 폈을 때
        elif (fingers == [1 ,1 , 1, 1, 1] ) & (active == 0 ):
             mode = 'Cursor'
             active = 1

############# Scroll 👇👇👇👇##############
    if mode == 'Scroll':
        active = 1
     #   print(mode)
        putText(mode)
        cv2.rectangle(img, (200, 410), (245, 460), (255, 255, 255), cv2.FILLED)
        if len(lmList) != 0:
            if fingers == [0,1,0,0,0]:
              #print('up')
              #time.sleep(0.1)
                putText(mode = 'U', loc=(200, 455), color = (0, 255, 0))
                pyautogui.scroll(300)

            if fingers == [0,1,1,0,0]:
                #print('down')
              #  time.sleep(0.1)
                putText(mode = 'D', loc =  (200, 455), color = (0, 0, 255))
                pyautogui.scroll(-300)
            elif fingers == [0, 0, 0, 0, 0]:
                active = 0
                mode = 'N'
################# Volume 👇👇👇####################
    if mode == 'Volume':
        active = 1
       #print(mode)
        putText(mode)
        if len(lmList) != 0:
            if fingers[-1] == 1:
                active = 0
                mode = 'N'
                print(mode)

            else:

                 #   print(lmList[4], lmList[8])
                    x1, y1 = lmList[4][1], lmList[4][2]
                    x2, y2 = lmList[8][1], lmList[8][2]
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    cv2.circle(img, (x1, y1), 10, color, cv2.FILLED)
                    cv2.circle(img, (x2, y2), 10, color, cv2.FILLED)
                    cv2.line(img, (x1, y1), (x2, y2), color, 3)
                    cv2.circle(img, (cx, cy), 8, color, cv2.FILLED)

                    # 엄지와 검지의 거리 구하기
                    length = math.hypot(x2 - x1, y2 - y1)
                    # print(length)

                    # hand Range 50-300
                    # Volume Range -65 - 0
                    # length 값이 [hmin, hmax] 범위에서 어디에 위치하는지에 따라, 그 값을 [minVol, maxVol] 범위에서의 값으로 선형 보간한다
                    vol = np.interp(length, [hmin, hmax], [minVol, maxVol])
                    volBar = np.interp(vol, [minVol, maxVol], [400, 150])
                    volPer = np.interp(vol, [minVol, maxVol], [0, 100])
                    print(vol)
                    volN = int(vol)
                    if volN % 4 != 0:
                        volN = volN - volN % 4
                        # 최대 볼륨 = 0
                        if volN >= 0:
                            volN = 0
                        # 최소 볼륨 = -64
                        elif volN <= -64:
                            volN = -64
                        elif vol >= -11:
                            volN = vol

                #    print(int(length), volN)
                    volume.SetMasterVolumeLevel(vol, None)
                    if length < 50:
                        cv2.circle(img, (cx, cy), 11, (0, 0, 255), cv2.FILLED)

                    cv2.rectangle(img, (30, 150), (55, 400), (209, 206, 0), 3)
                    cv2.rectangle(img, (30, int(volBar)), (55, 400), (215, 255, 127), cv2.FILLED)
                    cv2.putText(img, f'{int(volPer)}%', (25, 430), cv2.FONT_HERSHEY_COMPLEX, 0.9, (209, 206, 0), 3)


#######################################################################
    if mode == 'Cursor':
        active = 1
        #print(mode)
        putText(mode)
        cv2.rectangle(img, (110, 20), (620, 350), (255, 255, 255), 3)

        # 엄지를 제외한 나머지가 접혀있으면
        if fingers[1:] == [0,0,0,0]:
            active = 0
            mode = 'N'
            print(mode)
        else:
            if len(lmList) != 0:
                x1, y1 = lmList[8][1], lmList[8][2]
                w, h = autopy.screen.size()
                X = int(np.interp(x1, [110, 620], [0, w - 1]))
                Y = int(np.interp(y1, [20, 350], [0, h - 1]))
                cv2.circle(img, (lmList[8][1], lmList[8][2]), 7, (255, 255, 255), cv2.FILLED)
                cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 255, 0), cv2.FILLED)  #thumb

                # 일부 시스템에서는 홀수 좌표에서의 마우스 이동이 정확하지 않을 수 있기 때문에 짝수 만들어주기
                if X%2 !=0:
                    X = X - X%2
                if Y%2 !=0:
                    Y = Y - Y%2
                # print(X,Y)
                # 검지 끝부분으로 마우스 이동
                autopy.mouse.move(X,Y)
              #  pyautogui.moveTo(X,Y)
                # 엄지가 접히면 클릭
                if fingers[0] == 0:
                    cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 0, 255), cv2.FILLED)  # thumb
                    pyautogui.click()

    cTime = time.time()
    fps = 1/((cTime + 0.01)-pTime)
    pTime = cTime

    cv2.putText(img,f'FPS:{int(fps)}',(480,50), cv2.FONT_ITALIC,1,(255,0,0),2)
    cv2.imshow('Hand LiveFeed',img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    def putText(mode,loc = (250, 450), color = (0, 255, 255)):
        cv2.putText(img, str(mode), loc, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                    3, color, 3)