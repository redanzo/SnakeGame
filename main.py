import math
import random

import cvzone
import cv2
import numpy
import numpy as np
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)


class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = []  # points of the snake
        self.lengths = []  # distance between each point of the snake
        self.currentLength = 0  # total length of the snake
        self.allowedLength = 150  # total allowed length (keeps same length as moving, until snake eats food)
        self.previousHead = 0, 0  # previous head point

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()

        self.score = 0
        self.gameOver = False

    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    def update(self, imgMain, currentHead):

        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", [300, 400], scale=7, thickness=5, offset=20)
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [300, 550], scale=7, thickness=5, offset=20)

        else:

            px, py = self.previousHead
            cx, cy = currentHead

            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy

            # Length Reduction
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # Check Snake ate Food
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1
                print(self.score)
                if self.score == 15:
                    print("You Win")
                    self.gameOver = True
                    self.points = []  # points of the snake
                    self.lengths = []  # distance between each point of the snake
                    self.currentLength = 0  # total length of the snake
                    self.allowedLength = 150  # total allowed length (keeps same length as moving, until snake eats food)
                    self.previousHead = 0, 0  # previous head point
                    self.randomFoodLocation()


            # Draw Snake
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 175, 239), 20)
                cv2.circle(imgMain, self.points[-1], 20, (0, 175, 239), cv2.FILLED)

            # Draw Food
            rx, ry = self.foodPoint
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood, (rx - self.wFood // 2, ry - self.hFood // 2))

            # Draw Score so far
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [50, 80], scale=3, thickness=3, offset=20)

            # Check for Collision
            pts = numpy.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (0, 102, 0), 3)
            minDist = cv2.pointPolygonTest(pts, (cx, cy), True)

            if -1 <= minDist <= 1:
                print("Hit")
                self.gameOver = True
                self.points = []  # points of the snake
                self.lengths = []  # distance between each point of the snake
                self.currentLength = 0  # total length of the snake
                self.allowedLength = 150  # total allowed length (keeps same length as moving, until snake eats food)
                self.previousHead = 0, 0  # previous head point
                self.randomFoodLocation()

        return imgMain


game = SnakeGameClass("apple.png")

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if hands:
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]
        img = game.update(img, pointIndex)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
    key = cv2.waitKey(1)
    if key == ord('r'):
        game.gameOver = False
        game.score = 0
