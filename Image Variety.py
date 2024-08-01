#This file will create different variations of an image given by the user (currently manually inputted).

#Input: Image file, png, jpg, etc
#Output: Original Image, Grey-scaled image, Edged Image, Contrasted Image
# Kyle Silvestre

import cv2
import os

def saveImage(file_name, image_to_save, directory) -> None:
    os.chdir(directory)
    cv2.imwrite(file_name, image_to_save)
    return None

# Manually choosing the directory to save the created image (End-Game: Choose directory to save images)
users_chosen_directory = 'C:/Users/k1m4s/Loisaida/Loisaida_internship/created_images' #change path for different directory

# Manually loading the selected image (End-Game: Input an image and would change the imagw)
users_original_image = cv2.imread('../original_images/building_with_solar_panels.png') #change path for different images

#Displaying original image
cv2.imshow('Original Image', users_original_image)


gray_image = cv2.cvtColor(users_original_image, cv2.COLOR_BGR2GRAY)
cv2.imshow('Gray-scale-image', gray_image)
saveImage('GreyImage.png', gray_image, users_chosen_directory)

#Edge's of the image
edge_image = cv2.Canny(users_original_image, 150, 200)
cv2.imshow('Edge-image', edge_image)
saveImage('Edge-Image.png', edge_image, users_chosen_directory)

#Contrasting an Image & Saving it
#Alpha ranges from 1.0 - 3.0 | x > 1 increases contrast, x < 1 decreases contrast
#Beta ranges from 0 - 100 | x > 0 increases brightness, x < 0 decreases brightness

constrastedImage= cv2.convertScaleAbs(users_original_image, 3.0, 2)
cv2.imshow('Contrasted Image', constrastedImage)
saveImage('ContrastedImage.png', constrastedImage, users_chosen_directory)

cv2.waitKey(0)
cv2.destroyAllWindows()
