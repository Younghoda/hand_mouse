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

    # findPosition 메서드는 감지한 손의 랜드마크(특징점)를 추출합니다.
    def findPosition(self, img, handNo=0, draw=True, color =  (255, 0, 255), z_axis=False):

        lmList = []
        # 손이 감지된 경우에만 랜드마크 추출 및 그리기를 수행
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
             #   print(id, lm)
                h, w, c = img.shape
                # 2차원
                if z_axis == False:
                   cx, cy = int(lm.x * w), int(lm.y * h)
                    # print(id, cx, cy)
                   lmList.append([id, cx, cy])
                # 3차원
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

        # FPS 출력
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        # 카메라 보여주고 'q'를 누르면 종료
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def overlayPNG(imgBack, imgFront, pos=[0, 0]):
    """
     PNG 이미지를 투명도와 알파 블렌딩을 사용하여 다른 이미지 위에 오버레이합니다.
     함수는 포함된 위치, 음수 좌표를 포함한 경계를 처리하며 오버레이 이미지를 잘라내어 사용합니다. 가장자리는 알파 블렌딩을 사용하여 부드럽게 처리됩니다.

     :param imgBack: 배경 이미지로, (높이, 너비, 3) 또는 (높이, 너비, 4) 모양의 NumPy 배열입니다. 3채널 또는 4채널 이미지를 지원합니다.
     :param imgFront: 오버레이할 PNG 이미지로, (높이, 너비, 4) 모양의 NumPy 배열입니다. RGBA 형식의 이미지를 기대합니다.
     :param pos: 이미지를 오버레이 할 x 및 y 좌표를 나타내는 리스트입니다. 음수일 수 있고 이미지를 벗어날 수 있습니다.
     :return: 오버레이가 적용된 새로운 이미지로, `imgBack`과 같은 모양의 NumPy 배열입니다.
     """
    hf, wf, cf = imgFront.shape
    hb, wb, cb = imgBack.shape

    x1, y1 = max(pos[0], 0), max(pos[1], 0)
    x2, y2 = min(pos[0] + wf, wb), min(pos[1] + hf, hb)

    # 음수 위치의 경우 오버레이 이미지의 시작 위치를 변경합니다.
    x1_overlay = 0 if pos[0] >= 0 else -pos[0]
    y1_overlay = 0 if pos[1] >= 0 else -pos[1]

    # 오버레이할 슬라이스의 차원을 계산합니다.
    wf, hf = x2 - x1, y2 - y1

    # 오버레이가 배경 완전히 벗어나면 원래 배경을 반환합니다.
    if wf <= 0 or hf <= 0:
        return imgBack

    # 오버레이 이미지에서 알파 채널을 추출하고 역 마스크를 만듭니다.
    alpha = imgFront[y1_overlay:y1_overlay + hf, x1_overlay:x1_overlay + wf, 3] / 255.0
    inv_alpha = 1.0 - alpha

    # 오버레이 이미지에서 RGB 채널을 추출합니다.
    imgRGB = imgFront[y1_overlay:y1_overlay + hf, x1_overlay:x1_overlay + wf, 0:3]

    # 알파 블렌딩을 사용하여 전경과 배경을 결합합니다.
    for c in range(0, 3):
        imgBack[y1:y2, x1:x2, c] = imgBack[y1:y2, x1:x2, c] * inv_alpha + imgRGB[:, :, c] * alpha

    return imgBack

if __name__ == "__main__":
    main()