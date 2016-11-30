import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
from skimage.feature import hog
from skimage import color, exposure

# retorna uma image com apenas um dos canais
def get_img_channel(img, channel):

	img_copy = np.copy(img) 

	if channel == "r":	
		img_copy[:,:,1] = 0
		img_copy[:,:,2] = 0

	elif channel == "g":
		img_copy[:,:,0] = 0
		img_copy[:,:,2] = 0

	elif channel == "b":
		img_copy[:,:,0] = 0
		img_copy[:,:,1] = 0

	return img_copy


# generate histogram as a np.array
def hist(img):	

	R = get_img_channel(img, "r").flatten()
	G = get_img_channel(img, "g").flatten()
	B = get_img_channel(img, "b").flatten()
	
	hist_R,_ = np.histogram(R, bins=256)
	hist_G,_ = np.histogram(G, bins=256)	
	hist_B,_ = np.histogram(B, bins=256)

	return hist_R, hist_G, hist_B

# plot images
def draw_hist(img):
	
	fig, subs = plt.subplots(4,2)
	subs[0][0].imshow(img)
	subs[0][1].axis('off')

	R = get_img_channel(img,'r')
	G = get_img_channel(img,'g')
	B = get_img_channel(img,'b')

	subs[1][0].imshow(R)
	subs[1][1].hist(img[:,:,0].flatten(),np.arange(0,256))
	subs[1][1].set_xlim([0,256])


	subs[2][0].imshow(G)
	subs[2][1].hist(img[:,:,1].flatten(),np.arange(0,256))
	subs[2][1].set_xlim([0,256])


	subs[3][0].imshow(B)
	subs[3][1].hist(img[:,:,2].flatten(),np.arange(0,256))
	subs[3][1].set_xlim([0,256])


	plt.show()

# standardize a list
def standardize(data):
#	data[0] = 0  #<<<<<< PROBLEMAS AQUI
	mean = np.mean(data)
	std = np.std(data)
	return (data - mean)/std

# create a feature vector concatenating each image
def generate_vector(img_path):
	img = cv2.imread(img_path)	
	image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	hog_image = hog(image, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(1, 1), visualise=False)
	hog_image = standardize(hog_image)
	
	return hog_image.flatten()	
	#hist_R, hist_G, hist_B = hist(img)
	#feature_vec = np.hstack( [standardize(hist_R), standardize(hist_G), standardize(hist_B)])
#	return feature_vec

def retrieve_data():

	# img_file_path = "./img/Lenna.png"
	# img = cv2.imread(img_file_path)
	# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # covert to RGB

	# 1)
	#draw_hist(img)

	# 2) 
	#print a histogram as a vector
	# hist_R, hist_G, hist_B = hist(img)
	# print hist_R 
	# print hist_G 
	# print hist_B 

	# 3)
	# standardizing the vectors
	# hist_R, hist_G, hist_B = hist(img)
	# print standardize(hist_R)

	# 4) creating a feature vector
	# hist_R, hist_G, hist_B = hist(img)
	# feature_vec = np.hstack( [standardize(hist_R), standardize(hist_G), standardize(hist_B)])
	# print feature_vec


	# 5) processing image dataset to generate a feature vec
	test_folder = "./img/cifar-10/test"
	class_names = os.listdir(test_folder) # there are a folde for each class
		
	# processing train folder
	print "PROCESSING TEST FOLDER: "

	count  = 0
	vec_size = None
	for name in class_names:
		files = os.listdir(test_folder+"/"+name)
		
		# transform each file into a feature vector
		for file_name in files:
			if count == 0:
				vec = generate_vector(test_folder+"/"+name+"/"+file_name)
				vec_size = vec.shape[0]

			count += 1

	X = np.empty(shape=(count,vec_size))
	y = np.zeros(shape=(count, len(class_names)))

        count2 = 0
	for name in class_names:
		files = os.listdir(test_folder+"/"+name)
		
		# transform each file into a feature vector
		for file_name in files:
			vec = generate_vector(test_folder+"/"+name+"/"+file_name)
			X[count2] = vec
                        y[count2, class_names.index(name)] = 1
			#y_vec = [0] * len(class_names) # <<<<<<<<<<<<<< HOT ENCODING REPRESENTATION <<<<<
			#y_vec[class_names.index(name)] = 1
			#y.append(y_vec)

			count2 += 1

			if count2 % 1000 == 0:
				print count2, " images processed"
	# randomizing positions 
	np.random.seed(42)
	np.random.shuffle(X)
	np.random.seed(42)
	np.random.shuffle(y)


	# spliting the dataset in thee groups
	X_train = X[:8000]
	y_train = y[:8000]

	X_validation = X_test = X[8000: 9000]
	y_validation = y_test = y[8000: 9000]

	X_test = X[9000: ]
	y_test = y[9000: ]

	return (X_train, y_train), (X_validation, y_validation), (X_test, y_test)
