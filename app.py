from flask import Flask, render_template, Response
import cv2
import winsound
import time
import os

app = Flask(__name__)

# Configuration
SOUNDS_DIR = 'static/sounds'
os.makedirs(SOUNDS_DIR, exist_ok=True)

# Load Haar cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    cap = cv2.VideoCapture(1)  # Try secondary camera
if not cap.isOpened():
    raise RuntimeError("Cannot open camera")

# Detection state
eyes_closed = False
beep_playing = False
alert_playing = False
closed_start_time = None
warning_count = 0
EYES_CLOSED_THRESHOLD = 15
EYES_OPEN_RESET_THRESHOLD = 3
last_eyes_open_time = time.time()
event_registered = False

def generate_frames():
    global eyes_closed, beep_playing, alert_playing
    global closed_start_time, warning_count, last_eyes_open_time, event_registered

    # New logic variables
    eyes_were_closed = False
    beep_playing = False

    while True:
        success, frame = cap.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        eyes_detected = False

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 3)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)

            if len(eyes) >= 2:
                eyes_detected = True
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

        current_time = time.time()

        if eyes_detected:
            # Eyes are open
            if eyes_were_closed:
                # Transition: closed -> open, stop beep
                if beep_playing:
                    winsound.PlaySound(None, winsound.SND_ASYNC)
                    beep_playing = False
                eyes_were_closed = False
        else:
            # Eyes are closed
            if not beep_playing:
                # Start continuous beep if not already playing
                winsound.PlaySound(os.path.join(SOUNDS_DIR, "beep.wav"), winsound.SND_ASYNC | winsound.SND_LOOP)
                beep_playing = True
            eyes_were_closed = True

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)