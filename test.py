from vision import Vision
import cv2

v = Vision()

# Simple test: classify the templates themselves
img1 = cv2.imread("cell_1.png")
print("cell_1 ->", v.classify_cell(img1))

img2 = cv2.imread("flag.png")
print("flag ->", v.classify_cell(img2))

img3 = cv2.imread("hidden.png")
print("hidden ->", v.classify_cell(img3))
