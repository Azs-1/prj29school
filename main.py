from flask import Flask, Response
import cv2
import threading

app = Flask(__name__)

class VideoStream:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(rtsp_url)
        self.lock = threading.Lock()
        
    def generate_frames(self):
        while True:
            with self.lock:
                success, frame = self.cap.read()
                if not success:
                    # Переподключение при потере соединения
                    self.cap.release()
                    self.cap = cv2.VideoCapture(self.rtsp_url)
                    continue
            
            # Конвертация в JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Инициализация потока
rtsp_url = "rtsp://192.168.0.13:554/stream1"
video_stream = VideoStream(rtsp_url)

@app.route('/video_feed')
def video_feed():
    return Response(video_stream.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>RTSP Stream</title>
        </head>
        <body>
            <h1>RTSP Camera Stream</h1>
            <img src="/video_feed" width="640" height="480">
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)