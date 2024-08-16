from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from PIL import Image
import cv2

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads/'
PROCESSED_FOLDER = 'processed-images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Creates these folders incase user doesn't have them.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# Function to check if proper file is inserted
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the image and get albedo/brightness
            albedo = get_average_pixel_brightness(file_path)

            # Process the image using your OpenCV functions
            process_image(file_path, app.config['PROCESSED_FOLDER'])

            # Render the template with the albedo value and filename
            return render_template('index.html', processed=True, filename=filename, albedo=albedo)

    return render_template('index.html', processed=False)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


def get_average_pixel_brightness(image_path) -> float:
    # Open the image
    image = Image.open(image_path)

    # Convert image to RGB if it's not already in that mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Get the pixel data and calculate the average brightness (albedo)
    pixels = image.getdata()
    total_brightness = 0
    num_pixels = len(pixels)

    for pixel in pixels:
        # Calculate brightness using the luminance formula
        brightness = (0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]) / 255
        total_brightness += brightness

    # Calculate the average brightness
    average_brightness_value = total_brightness / num_pixels

    return round(average_brightness_value, 2)


def process_image(image_path, save_directory) -> None:
    # Load the image
    original_image = cv2.imread(image_path)

    if original_image is None:
        print(f"Error: Image not found at {image_path}")
        return

    # Resize the image
    resized_image = resize_image(original_image, 300)

    # Convert to grayscale and save
    gray_image = convert_to_grayscale(resized_image)
    save_image(save_directory, 'GrayImage', gray_image)

    # Detect edges and save
    edge_image = detect_edges(resized_image)
    save_image(save_directory, 'EdgeImage', edge_image)

    # Apply contrast and save
    contrasted_image = apply_contrast(resized_image)
    save_image(save_directory, 'ContrastedImage', contrasted_image)


def save_image(directory, file_name, image) -> None:
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Unique names for all images
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_file_name = f"{file_name}_{timestamp}.png"
        save_path = os.path.join(directory, unique_file_name)

        cv2.imwrite(save_path, image)
        print(f"Image saved: {save_path}")
    except Exception as e:
        print(f"Error saving image: {e}")


def resize_image(image, width):
    (h, w) = image.shape[:2]
    aspect_ratio = h / w
    new_height = int(width * aspect_ratio)
    return cv2.resize(image, (width, new_height))


def convert_to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def detect_edges(image, threshold1=150, threshold2=200):
    return cv2.Canny(image, threshold1, threshold2)


def apply_contrast(image, alpha=3.0, beta=2):
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


if __name__ == '__main__':
    app.run(debug=True)
