import os
import cv2
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("image")
        if not file or file.filename == "":
            return render_template("index.html", message="❌ No image selected!")

        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_filename = "output_" + filename
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        file.save(upload_path)

        return render_template("index.html", uploaded=True, filename=filename)

    return render_template("index.html")

@app.route("/detect/<filename>")
def detect(filename):
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_filename = "output_" + filename
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    img_bgr = cv2.imread(upload_path)
    if img_bgr is None:
        return f"Could not read image: {filename}"

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    start = time.time()
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    end = time.time()

    for (x, y, w, h) in faces:
        cv2.rectangle(img_bgr, (x, y), (x + w, y + h), (0, 0, 255), 3)

    cv2.imwrite(output_path, img_bgr)

    summary = f"✅ Detected {len(faces)} face(s) in {round(end - start, 2)} seconds."
    reason = ""
    if len(faces) == 0:
        reason = "❌ No faces detected. Possible reasons:<br>- Blurry or dark image<br>- Faces turned or hidden<br>- Low image quality"

    return render_template("output.html",
                           original=filename,
                           result=output_filename,
                           summary=summary,
                           reason=reason)

@app.route('/static/<path:filename>')
def serve_static_file(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(debug=True)
