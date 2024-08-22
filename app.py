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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Creates these folders incase user doesn't have them.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# Function to check if proper file is inserted
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Function to get a timestamp string
def get_timestamp():
    return datetime.now().strftime('%Y%m%d_%H%M%S')


# Function to build a unique filename from address parts and a timestamp
def build_filename(street, city, state, zip_code, extension):
    address_filename = f"{street}-{city}-{state}-{zip_code}".replace(' ', '-')
    return secure_filename(f"{address_filename}_{get_timestamp()}.{extension}")


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        # Collect address inputs
        street = request.form.get('street', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        zip_code = request.form.get('zip', '').strip()

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)

        # Generate the filename using address parts and a timestamp
        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = build_filename(street, city, state, zip_code, extension)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the image and get albedo/brightness
        albedo = get_average_pixel_brightness(file_path)
        process_image(file_path, app.config['PROCESSED_FOLDER'])

        return render_template('index.html', processed=True, filename=filename, albedo=albedo)

    return render_template('index.html', processed=False)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


def get_average_pixel_brightness(image_path) -> float:
    # Input: Image Path
    # Output: Albedo value scrapped from the image
    image = Image.open(image_path).convert('RGB')
    pixels = list(image.getdata())
    num_pixels = len(pixels)
    total_brightness = sum((0.299 * r + 0.587 * g + 0.114 * b) / 255 for r, g, b in pixels)
    return round(total_brightness / num_pixels, 2)


def process_image(image_path, save_directory) -> None:
    # Input: Image Path, Directory
    # Output: Images saved to directory with different alterations
    original_image = cv2.imread(image_path)
    if original_image is None:
        print(f"Error: Image not found at {image_path}")
        return

    # Process and save multiple variations of the image
    save_variations(original_image, save_directory)


def save_variations(image, directory) -> None:
    # Input: Image & Directory to Save
    # Output: Images will be saved with their proper names, and variations.
    variations = {
        'GrayImage': convert_to_grayscale(image),
        'EdgeImage': detect_edges(image),
        'ContrastedImage': apply_contrast(image)
    }

    for name, processed_image in variations.items():
        save_image(directory, name, processed_image)


def save_image(directory, file_name, image) -> None:
    # Input: Chosen Directory, File Name, Image
    # Output: Saving a file with unique identifiers to chosen directory
    unique_file_name = f"{file_name}_{get_timestamp()}.png"
    save_path = os.path.join(directory, unique_file_name)
    cv2.imwrite(save_path, image)
    print(f"Image saved: {save_path}")


def resize_image(image, width):
    # Input: Image, Desired Width
    # Output: Resized image
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
