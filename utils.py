import cv2
import mediapipe as mp

# class HandDetector():
    # def __init__(self, mode=False, max_Hands=2, mcomplexity = 1, detectionCon=0.5, trackCon=0.5):
    #     self.mode = mode
    #     self.max_Hands = max_Hands
    #     self.mcomplexity = mcomplexity
    #     self.detectionCon = detectionCon
    #     self.trackCon = trackCon
    #     self.mpHands = mp.solutions.hands
    #     self.hands = self.mpHands.Hands(self.mode, self.max_Hands,self.mcomplexity,
    #                                     self.detectionCon, self.trackCon)
    #     self.mpDraw = mp.solutions.drawing_utils
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
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handlms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img,handlms, self.mpHands.HAND_CONNECTIONS)

        return img
    def findPosition(self, img, draw=True, flipType=False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        lmList = []
        xList = []
        yList = []
        allHands=[]
        if self.results.multi_hand_landmarks:
            for handType, handLMS in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHands={}
                if draw:
                    self.mpDraw.draw_landmarks(img, handLMS, self.mpHands.HAND_CONNECTIONS)
                for id, lm in enumerate(handLMS.landmark):
                    h, w, _ = img.shape
                    px, py, pz = int(lm.x*w), int(lm.y*h), int(lm.z*w)
                    lmList.append([px, py, pz])
                    xList.append(px)
                    yList.append(py)
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                bboxW, bboxH = xmax - xmin, ymax - ymin
                bbox = xmin, ymin, bboxW, bboxH
                cx, cy = bbox[0] + (bbox[2] // 2), bbox[1] + (bbox[3] // 2)

                myHands["lmList"] = lmList
                myHands["bbox"] = bbox
                myHands["center"] = cx, cy
                if flipType:
                    if handType.classificattion[0].label == "Right":
                        myHands["type"] = "Left"
                    if handType.classificattion[0].label == "Left":
                        myHands["type"] = "Right"
                else:
                    myHands["type"] = handType.classification[0].label

                allHands.append(myHands)
        return img, allHands

def overlayPNG(imgBack, imgFront, pos=[0, 0]):
    """
     Overlay a PNG image with transparency onto another image using alpha blending.
     The function handles out-of-bound positions, including negative coordinates, by cropping
     the overlay image accordingly. Edges are smoothed using alpha blending.

     :param imgBack: The background image, a NumPy array of shape (height, width, 3) or (height, width, 4).
     :param imgFront: The foreground PNG image to overlay, a NumPy array of shape (height, width, 4).
     :param pos: A list specifying the x and y coordinates (in pixels) at which to overlay the image.
                 Can be negative or cause the overlay image to go out-of-bounds.
     :return: A new image with the overlay applied, a NumPy array of shape like `imgBack`.
     """
    hf, wf, cf = imgFront.shape
    hb, wb, cb = imgBack.shape

    x1, y1 = max(pos[0], 0), max(pos[1], 0)
    x2, y2 = min(pos[0] + wf, wb), min(pos[1] + hf, hb)

    # For negative positions, change the starting position in the overlay image
    x1_overlay = 0 if pos[0] >= 0 else -pos[0]
    y1_overlay = 0 if pos[1] >= 0 else -pos[1]

    # Calculate the dimensions of the slice to overlay
    wf, hf = x2 - x1, y2 - y1

    # If overlay is completely outside background, return original background
    if wf <= 0 or hf <= 0:
        return imgBack

    # Extract the alpha channel from the foreground and create the inverse mask
    alpha = imgFront[y1_overlay:y1_overlay + hf, x1_overlay:x1_overlay + wf, 3] / 255.0
    inv_alpha = 1.0 - alpha

    # Extract the RGB channels from the foreground
    imgRGB = imgFront[y1_overlay:y1_overlay + hf, x1_overlay:x1_overlay + wf, 0:3]

    # Alpha blend the foreground and background
    for c in range(0, 3):
        imgBack[y1:y2, x1:x2, c] = imgBack[y1:y2, x1:x2, c] * inv_alpha + imgRGB[:, :, c] * alpha

    return imgBack