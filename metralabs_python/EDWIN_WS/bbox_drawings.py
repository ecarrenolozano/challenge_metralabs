import json 
import os
import cv2 

from matplotlib import pyplot as plt


# Information and absolute paths for the images, label and metadata

base_path = "/home/egcarren/Downloads/metralabs"
datasets_main_folder = "datasets_1_2"
dataset = "dataset_1"
camera = "cam3"
type_data = "ColorImage"
image_filename = "1716461403948342000.PNG"

label_filename = image_filename.split(".")[0] + "_label.json"
metadata_filename =  image_filename.split(".")[0] + "_meta.json" 

path_image = os.path.join(base_path, \
                             datasets_main_folder, \
                             dataset, \
                             camera, \
                             type_data,
                             image_filename                             
                             )

# Load the image using OpenCV

img = cv2.imread(path_image)
print(img.shape)


plt.imshow(img[:,:,::-1])

