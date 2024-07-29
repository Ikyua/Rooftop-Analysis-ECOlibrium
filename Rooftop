from PIL import Image

def get_average_pixel_brightness(image_path):
    image = Image.open(image_path)
    pixels = list(image.getdata())

    # Ensure pixels are in RGB format
    if image.mode != 'RGB':
        image = image.convert('RGB')
        pixels = list(image.getdata())

    # Calculate normalized brightness for each pixel
    normalized_brightness = [
        (0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]) / 255
        for pixel in pixels
    ]

    # Calculate the average brightness of all pixels
    average_brightness = sum(normalized_brightness) / len(normalized_brightness)

    return average_brightness

image_path = 'rooftop.png'
average_brightness = get_average_pixel_brightness(image_path)
print("Average Brightness:", average_brightness)
