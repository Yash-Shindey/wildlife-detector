import cv2
import sys
import json
import base64
import time
import select
from PIL import Image
from transformers import pipeline
from PytorchWildlife.models.detection import MegaDetectorV6
import supervision as sv
import numpy as np
from datetime import datetime
import os

def ensure_directories():
    for directory in ['screenshots', 'recordings']:
        if not os.path.exists(directory):
            os.makedirs(directory)

class WildlifeDetector:
    def __init__(self):
        ensure_directories()
        
        print(json.dumps({"status": "Loading MegaDetector..."}))
        self.detector = MegaDetectorV6(device="cpu", pretrained=True)
        
        print(json.dumps({"status": "Loading classifier..."}))
        self.classifier = pipeline("image-classification", 
                                 model="Bazaar/cv_level1_protected_animals_classification")
        
        self.box_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        
        self.camera_index = 0
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_AVFOUNDATION)
        
        if not self.cap.isOpened():
            print(json.dumps({"error": "Failed to open camera"}))
            sys.exit(1)
        
        self.recording = False
        self.video_writer = None
        
        self.frame_count = 0
        self.fps = 0
        self.last_time = time.time()
        self.confidence_threshold = 0.5
        
        print(json.dumps({"status": "Detector running"}))

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, []
            
        current_time = time.time()
        self.frame_count += 1
        if current_time - self.last_time > 1:
            self.fps = self.frame_count / (current_time - self.last_time)
            self.frame_count = 0
            self.last_time = current_time

        try:
            # Run MegaDetector
            results = self.detector.single_image_detection(frame)
            detections = results['detections']
            valid_detections = []
            labels = []

            if hasattr(detections, 'confidence'):
                # Filter by confidence and process each detection
                for idx, (class_id, conf, bbox) in enumerate(zip(
                    detections.class_id, 
                    detections.confidence, 
                    detections.xyxy
                )):
                    if conf >= self.confidence_threshold:
                        x1, y1, x2, y2 = map(int, bbox)
                        roi = frame[y1:y2, x1:x2]
                        
                        if roi.size == 0:
                            continue

                        # Keep track of valid detections
                        valid_detections.append(idx)
                        
                        if class_id == 1:  # Human
                            labels.append("Human")
                        elif class_id == 0:  # Animal
                            try:
                                cropped_img = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
                                predictions = self.classifier(cropped_img)
                                animal_label = predictions[0]['label']
                                animal_confidence = predictions[0]['score']
                                labels.append(f"{animal_label} ({animal_confidence:.2f})")
                            except Exception:
                                labels.append("Animal")
                        elif class_id == 2:  # Vehicle
                            labels.append("Vehicle")
                        else:
                            labels.append("Unknown")

            # Create new detections object with only valid detections
            if valid_detections:
                filtered_detections = sv.Detections(
                    xyxy=detections.xyxy[valid_detections],
                    confidence=detections.confidence[valid_detections],
                    class_id=detections.class_id[valid_detections]
                )
                
                # Annotate frame only if we have valid detections
                frame = self.box_annotator.annotate(scene=frame, detections=filtered_detections)
                frame = self.label_annotator.annotate(
                    scene=frame, 
                    detections=filtered_detections,
                    labels=labels
                )
            
            if self.recording and self.video_writer:
                self.video_writer.write(frame)
            
            return frame, labels

        except Exception as e:
            print(json.dumps({"error": f"Frame processing error: {str(e)}"}), file=sys.stderr)
            return frame, []

    def send_frame(self, frame, labels):
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            data = {
                "frame": f"data:image/jpeg;base64,{frame_base64}",
                "fps": self.fps,
                "detections": labels,
                "recording": self.recording
            }
            
            print(json.dumps(data))
            sys.stdout.flush()
            
        except Exception as e:
            print(json.dumps({"error": f"Frame error: {str(e)}"}), file=sys.stderr)

    def capture_screenshot(self, frame, labels):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/detection_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(json.dumps({"status": f"Screenshot saved: {filename}"}))
        except Exception as e:
            print(json.dumps({"error": f"Screenshot error: {str(e)}"}), file=sys.stderr)

    def toggle_recording(self, frame):
        try:
            if not self.recording:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recordings/detection_{timestamp}.mp4"
                height, width = frame.shape[:2]
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(
                    filename,
                    fourcc,
                    20.0,
                    (width, height)
                )
                self.recording = True
                print(json.dumps({"status": "Recording started"}))
            else:
                if self.video_writer:
                    self.video_writer.release()
                self.recording = False
                self.video_writer = None
                print(json.dumps({"status": "Recording stopped"}))
        except Exception as e:
            print(json.dumps({"error": f"Recording error: {str(e)}"}), file=sys.stderr)

    def switch_camera(self):
        try:
            self.camera_index = (self.camera_index + 1) % 2
            self.cap.release()
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_AVFOUNDATION)
            print(json.dumps({"status": f"Switched to camera {self.camera_index}"}))
        except Exception as e:
            print(json.dumps({"error": f"Camera switch error: {str(e)}"}), file=sys.stderr)

    def run(self):
        while True:
            try:
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    cmd = sys.stdin.readline().strip()
                    if cmd == "switch_camera":
                        self.switch_camera()
                    elif cmd == "screenshot":
                        frame, labels = self.process_frame()
                        if frame is not None:
                            self.capture_screenshot(frame, labels)
                    elif cmd == "toggle_recording":
                        frame, _ = self.process_frame()
                        if frame is not None:
                            self.toggle_recording(frame)
                    elif cmd == "quit":
                        break

                frame, labels = self.process_frame()
                if frame is not None:
                    self.send_frame(frame, labels)
                
                time.sleep(0.01)
                
            except Exception as e:
                print(json.dumps({"error": f"Main loop error: {str(e)}"}), file=sys.stderr)
                time.sleep(0.1)

if __name__ == "__main__":
    try:
        detector = WildlifeDetector()
        detector.run()
    except Exception as e:
        print(json.dumps({"error": f"Fatal error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
