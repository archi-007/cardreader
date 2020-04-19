
from fpt import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils

from PIL import Image
import PIL.Image

from pytesseract import image_to_string
import pytesseract
import re


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
	help = "Path to the image to be scanned")
args = vars(ap.parse_args())

#edge detection
image = cv2.imread(args["image"])
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize(image, height = 500)
 

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)
 

print("STEP 1: Edge Detection")


cv2.imshow("Image", image)
cv2.imshow("Edged", edged)
cv2.waitKey(0)
cv2.destroyAllWindows()


cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
 
# loop over the contours
for c in cnts:
	
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
 
	
	if len(approx) == 4:
		screenCnt = approx
		break
 


print("STEP 2: Find contours of paper")


cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
cv2.imshow("Outline", image)
cv2.waitKey(0)
cv2.destroyAllWindows()


warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
 
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
T = threshold_local(warped, 11, offset = 10, method = "gaussian")
warped = (warped > T).astype("uint8") * 255
 

print("STEP 3: Apply perspective transform")

imS = cv2.resize(warped, (650, 650))
cv2.imshow("output",imS)
cv2.imwrite('out/'+'Output Image.PNG', imS)
cv2.waitKey(0)


output = pytesseract.image_to_string(PIL.Image.open('out/'+ 'Output Image.PNG').convert("RGB"), lang='eng')


f = open('text.json','w')
f.write(output)
f.close()

# regex used are not very efficient
emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", output)
numbers = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', output)
addresses = re.findall(r"\d{1,3}.?\d{0,3}\s[a-zA-Z]{2,30}\s[a-zA-Z]{2,15}", output)
posts = re.findall(r"[A-Z]([a-z]+|\.)(?:\s+[A-Z]([a-z]+|\.))*(?:\s+[a-z][a-z\-]+){0,2}\s+[A-Z]([a-z]+|\.)", output)

print(addresses)
print(numbers)
print(emails)
print(posts)

for email in emails:
	print('\n EMAIL : ' + email)
	F = open('emails.json','a+')
	F.write('EMAIL :-> ' + email)

for number in numbers:
	print('Phone No. : ' + number)
	F = open('emails.json', 'a+')
	F.write('\n Phone No. :-> ' + number)

for address in addresses :
	print('Address : ' + address)
	F = open('emails.json', 'a+')
	F.write('\n Address : ' + address)

for post in posts :
	print('Post : ' + post)
	F = open('emails.json', 'a+')
	F.write('\n Post : ' + post)






