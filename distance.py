import cv2 as cv
import mediapipe as mp

class DistanceChecker:
    def __init__(self, threshold_distance=20):
        self.threshold_distance = threshold_distance
        self.mp_face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5)
    def process_frame(self, frame):
        frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = self.mp_face_detection.process(frame_rgb)
        warning_message = None
        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                face_width = w
                distance = 5000 / face_width  
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv.putText(frame, f"Distance: {int(distance)} cm", (x, y - 10),
                            cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                if distance < self.threshold_distance:
                    warning_message = f"Distance < {self.threshold_distance} cm"
        if warning_message:
            cv.putText(frame, warning_message, (30, 30),
                        cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        return frame, warning_message

if __name__=="__main__":
    dist=DistanceChecker()
    cap=cv.VideoCapture(0, cv.CAP_DSHOW)
    while True:
        ret, frame=cap.read()
        cv.imshow("camera", frame)
        dist.process_frame(frame)
        cv.imshow("camera", frame)
        key=cv.waitKey(1)
        if key==13:
            cv.imshow("DistanceFrame", frame)
            cv.waitKey(1000)
            break
        elif key==27:
            print('Exiting')
            break
        cap.release()
        cv.destroyAllWindows()
        