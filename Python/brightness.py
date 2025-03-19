import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def calculate_brightness_histogram(region):
    """Analyze brightness distribution using histograms."""
    hist = cv2.calcHist([region], [0], None, [256], [0, 256])
    total_pixels = region.size
    bright_pixels = np.sum(hist[200:])  # Pixels with brightness >= 200
    dim_pixels = np.sum(hist[:100])    # Pixels with brightness <= 100
    
    bright_ratio = bright_pixels / total_pixels
    dim_ratio = dim_pixels / total_pixels
    
    return bright_ratio, dim_ratio

def classify_brightness(bright_ratio, dim_ratio):
    """Classify brightness based on ratios."""
    if bright_ratio > 0.4:
        return "Bright"
    elif dim_ratio > 0.4:
        return "Dim"
    else:
        return "Normal"

# Initialize video capture
cap = cv2.VideoCapture(0)

with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Perform face detection
        results = face_detection.process(rgb_frame)
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        face_light = "Not Detected"
        background_light = "Not Detected"

        if results.detections:
            for detection in results.detections:
                # Extract face bounding box
                bboxC = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                x_min = int(bboxC.xmin * w)
                y_min = int(bboxC.ymin * h)
                box_width = int(bboxC.width * w)
                box_height = int(bboxC.height * h)

                # Extract face region
                face_roi = gray_frame[y_min:y_min + box_height, x_min:x_min + box_width]
                face_bright_ratio, face_dim_ratio = calculate_brightness_histogram(face_roi)
                face_light = classify_brightness(face_bright_ratio, face_dim_ratio)

                # Mask out face region for background calculation
                mask = np.ones_like(gray_frame, dtype=np.uint8)
                mask[y_min:y_min + box_height, x_min:x_min + box_width] = 0
                background_roi = gray_frame[mask == 1]
                bg_bright_ratio, bg_dim_ratio = calculate_brightness_histogram(background_roi)
                background_light = classify_brightness(bg_bright_ratio, bg_dim_ratio)

        # Display results
        cv2.putText(frame, f"Face Light: {face_light}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Background Light: {background_light}", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(frame, detection)

        # Show the frame
        cv2.imshow("Proctoring System", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
