import cv2              # OpenCV 라이브러리로, 비디오 처리 및 컴퓨터 비전 작업에 사용
import mediapipe as mp  # Google에서 제공하는 라이브러리로, 손 인식 및 다양한 인체 관련 작업을 수행하는 데 사용
import time

# 클래스는 손을 감지하고 추적하는데 사용
class handDetector():
    # maxHands는 감지할 손의 최대 개수, detectionCon은 감지 신뢰도, trackCon은 추적 신뢰도를 나타냅니다.
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        # self.mpHands와 self.mpDraw는 mediapipe의 손 모델과 랜드마크를 시각적으로 표시하는 도구를 초기화합니다
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    # findHands 메서드는 이미지에서 손을 감지하고, draw 매개변수에 따라 감지된 손을 시각적으로 표시할지 여부를 결정합니다.
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True, color =  (255, 0, 255), z_axis=False):

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
             #   print(id, lm)
                h, w, c = img.shape
                if z_axis == False:
                   cx, cy = int(lm.x * w), int(lm.y * h)
                    # print(id, cx, cy)
                   lmList.append([id, cx, cy])
                elif z_axis:
                    cx, cy, cz = int(lm.x * w), int(lm.y * h), round(lm.z,3)
                    # print(id, cx, cy, cz)
                    lmList.append([id, cx, cy, cz])

                if draw:
                    cv2.circle(img, (cx, cy),5,color, cv2.FILLED)

        return lmList


def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(1)
    detector = handDetector(maxHands=1)
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img,z_axis=True,draw=False)
        if len(lmList) != 0:
            print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()