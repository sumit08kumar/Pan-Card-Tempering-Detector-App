# Important imports
from app import app
from flask import request, render_template
import os
from skimage.metrics import structural_similarity
import imutils
import cv2
from PIL import Image

# Adding platform-independent paths using os.path.join
base_dir = os.path.abspath(os.path.dirname(__file__))  # Get the absolute path of the current file's directory

# Fix the directory paths
app.config['INITIAL_FILE_UPLOADS'] = os.path.join(base_dir, 'static', 'uploads')
app.config['EXISTNG_FILE'] = os.path.join(base_dir, 'static', 'original')
app.config['GENERATED_FILE'] = os.path.join(base_dir, 'static', 'generated')

# Route to home page
@app.route("/", methods=["GET", "POST"])
def index():

    # Execute if request is GET
    if request.method == "GET":
        return render_template("index.html")

    # Execute if request is POST
    if request.method == "POST":
        # Get uploaded image
        file_upload = request.files['file_upload']
        filename = file_upload.filename
        
        # Ensure the 'uploads' directory exists before saving the file
        if not os.path.exists(app.config['INITIAL_FILE_UPLOADS']):
            os.makedirs(app.config['INITIAL_FILE_UPLOADS'])
        
        # Resize and save the uploaded image
        uploaded_image = Image.open(file_upload).resize((250, 160))
        uploaded_image.save(os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'image.jpg'))

        # Resize and save the original image to ensure both uploaded and original match in size
        original_image = Image.open(os.path.join(app.config['EXISTNG_FILE'], 'image.jpg')).resize((250, 160))
        original_image.save(os.path.join(app.config['EXISTNG_FILE'], 'image.jpg'))

        # Read uploaded and original image as arrays
        original_image = cv2.imread(os.path.join(app.config['EXISTNG_FILE'], 'image.jpg'))
        uploaded_image = cv2.imread(os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'image.jpg'))

        # Convert images to grayscale
        original_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        uploaded_gray = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2GRAY)

        # Calculate structural similarity
        (score, diff) = structural_similarity(original_gray, uploaded_gray, full=True)
        diff = (diff * 255).astype("uint8")

        # Calculate threshold and contours
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        
        # Draw contours on image
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(original_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(uploaded_image, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Save all output images
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_original.jpg'), original_image)
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_uploaded.jpg'), uploaded_image)
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_diff.jpg'), diff)
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_thresh.jpg'), thresh)
        
        # Return result
        return render_template('index.html', pred=str(round(score * 100, 2)) + '%' + ' correct')

# Main function
if __name__ == '__main__':
    app.run(debug=True)
