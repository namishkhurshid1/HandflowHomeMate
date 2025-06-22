import cv2
import mediapipe as mp
import math

class HandTracker():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, modelComplexity=1, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def handsFinder(self, image, draw=True):
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(image, handLms, self.mpHands.HAND_CONNECTIONS)
        return image
    def positionFinder(self, image, handNo=0, draw=True):
        lmlist = []
        if self.results.multi_hand_landmarks:
            Hand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(Hand.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmlist.append([id, cx, cy])
            if draw:
                cv2.circle(image, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmlist

    def fingersUp(self, lmList):
        fingers = []
        tipIds = [4, 8, 12, 16, 20]

        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def findDistance(self, p1, p2, lmList, image, draw=True):
        x1, y1 = lmList[p1][1], lmList[p1][2]
        x2, y2 = lmList[p2][1], lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        length = math.hypot(x2 - x1, y2 - y1)

        if draw:
            cv2.circle(image, (x1, y1), 8, (255, 0, 0), cv2.FILLED)
            cv2.circle(image, (x2, y2), 8, (255, 0, 0), cv2.FILLED)
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(image, (cx, cy), 8, (0, 0, 255), cv2.FILLED)

        return length

# def main():
#     cap = cv2.VideoCapture(0)
#     tracker = HandTracker()

#     while True:
#         success, image = cap.read()
#         image = tracker.handsFinder(image)
#         lmList = tracker.positionFinder(image, draw=False)

#         if len(lmList) != 0:
#             fingers = tracker.fingersUp(lmList)
#             totalFingers = fingers.count(1)
#             print(f"Fingers Up: {totalFingers}")

#             if totalFingers == 2:
#                 print("Adjusting fan speed...")

#             if totalFingers == 5:
#                 print("Fan turning ON...")

#             if totalFingers == 0:
#                 print("Fan turning OFF...")

#         cv2.imshow("Video", image)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
