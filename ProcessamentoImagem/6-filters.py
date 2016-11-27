import cv2
from matplotlib import pyplot as plt


img_file_path = "./img/Lenna.png"


#open image
img = cv2.imread(img_file_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # para converter para GRAY <<<<<<<<<<<<<<<<<<


## 1) blur (uniform)
img_blur = cv2.blur(img, (3,3))

# fig, subs = plt.subplots(1,2)
## plt.gray()
# subs[0].imshow(img)
# subs[1].imshow(img_blur) 
# plt.show()


## 2) gaussian blur (normalized)
img_gauss = cv2.GaussianBlur(img,(11,11), 1)
# fig, subs = plt.subplots(1,2)
# subs[0].imshow(img)
# subs[1].imshow(img_gauss)
# plt.show()

## 3) sobel filter
##x: [[-1,0,1],[-2,0,2],[-1,0,1]]
##y: [[1,2,1],[0,0,0],[-1,-2,-1]]
sobelx = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=5)
sobely = cv2.Sobel(img,cv2.CV_64F,0,1,ksize=5)
# fig, subs = plt.subplots(1,3)
# plt.gray()
# subs[0].imshow(img)
# subs[1].imshow(sobelx)
# subs[2].imshow(sobely)

# plt.show()


## 4) laplacian filter
## kernel1 [[0, 1, 0],[1, -4, 1],[0, 1, 0]]
## kernel2 [[0, 1, 0],[1, -8, 1],[0, 1, 0]]
img_laplacian = cv2.Laplacian(img,cv2.CV_64F)
# fig, subs = plt.subplots(1,2)
# plt.gray()
# subs[0].imshow(img)
# subs[1].imshow(img_laplacian)
# plt.show()



## 5) diff of blur
dob = img - img_blur
# fig, subs = plt.subplots(1,2)
# plt.gray()
# subs[0].imshow(img)
# subs[1].imshow(dob)
# plt.show()


## 6) DoG
img_gauss1 = cv2.GaussianBlur(img,(5,5), 1)
img_gauss2 = cv2.GaussianBlur(img_gauss1,(5,5), 1)

dog = img - img_gauss1
fig, subs = plt.subplots(1,2)
plt.gray()
subs[0].imshow(img)
subs[1].imshow(dog)
plt.show()


