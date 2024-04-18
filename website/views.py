from flask import Blueprint, render_template, request, flash, Response
import cv2

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        prevFEN = request.form.get('prevFEN')

        if len(prevFEN) < 16:
            flash('too short', category="error")
        else:
            flash('worked!', category="success")
    global video  # Access the global video capture object
    return Response(gen(video),  # Return a response with the video feed generator
                    mimetype='multipart/x-mixed-replace; boundary=frame')  # Set the response MIME type

    return render_template("template.html", text = "FEN test")


video = cv2.VideoCapture(0)  # Initialize the video capture object with webcam (0)

def gen(video):
    while True:
        success, image = video.read()  # Read a frame from the video capture
        ret, jpeg = cv2.imencode('.jpg', image)  # Encode the frame as a JPEG image

        frame = jpeg.tobytes()  # Convert the JPEG image to bytes
        
        yield (b'--frame\r\n'  # Yield a frame as part of a multipart HTTP response
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


    