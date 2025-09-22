import cv2
import face_recognition
import numpy as np
import os
import csv
import datetime
import pywhatkit
import time

DATASET_DIR = "dataset"
ATTENDANCE_DIR = "attendance"

if not os.path.exists(ATTENDANCE_DIR):
    os.makedirs(ATTENDANCE_DIR)

known_face_encodings = []
known_face_names = []

def load_known_faces():
    known_face_encodings.clear()
    known_face_names.clear()
    print("📦 Loading trained faces...")
    for name in os.listdir(DATASET_DIR):
        person_folder = os.path.join(DATASET_DIR, name)
        for filename in os.listdir(person_folder):
            filepath = os.path.join(person_folder, filename)
            image = face_recognition.load_image_file(filepath)
            try:
                encoding = face_recognition.face_encodings(image)[0]
                known_face_encodings.append(encoding)
                known_face_names.append(name)
            except Exception as e:
                print(f"⚠️ Skipping image '{filename}': {e}")
    print(f"✅ Loaded {len(known_face_names)} known faces.")

def send_attendance_as_text(file_path, present_names):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()[1:]  # skip header

        today = datetime.datetime.now().strftime("%d-%m-%Y")
        attendance_table = "🟢 *Present List:*\n"
        for line in lines:
            name, time_str = line.strip().split(",")
            attendance_table += f"{name} at {time_str} on {today}\n"

        # Find absentees
        all_names = set(known_face_names)
        present_names = set(present_names)
        absent_names = all_names - present_names

        if absent_names:
            attendance_table += "\n🔴 *Absent List:*\n"
            for name in absent_names:
                attendance_table += f"{name}\n"
        else:
            attendance_table += "\n✅ All students are present!"

        number = "+916369580858"

        print("📤 Sending WhatsApp message in 10 seconds...")
        time.sleep(20)
        pywhatkit.sendwhatmsg_instantly(number, attendance_table, wait_time=10, tab_close=True)
        print("✅ Attendance message sent!")

    except Exception as e:
        print(f"❌ Failed to send WhatsApp message: {e}")

def mark_attendance(name, attendance_file):
    with open(attendance_file, 'a', newline='') as file:
        writer = csv.writer(file)
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        writer.writerow([name, time_str])

def take_attendance_cycle():
    round_seconds = 20
    rest_seconds = 10
    cycle = 1

    while True:
        print(f"\n▶ Round {cycle}: capturing for {round_seconds}s...")

        load_known_faces()
        video = cv2.VideoCapture(0)
        if not video.isOpened():
            print("❌ Cannot access webcam.")
            return
        print("✅ Webcam opened.")

        attendance = set()
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
        path = os.path.join(ATTENDANCE_DIR, filename)

        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Time"])

        end_time = time.time() + round_seconds

        while time.time() < end_time:
            ret, frame = video.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, faces)

            for encoding, face_loc in zip(encodings, faces):
                matches = face_recognition.compare_faces(known_face_encodings, encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, encoding)
                if len(face_distances) > 0:
                    best_match = np.argmin(face_distances)
                    if matches[best_match]:
                        name = known_face_names[best_match]

                if name != "Unknown" and name not in attendance:
                    attendance.add(name)
                    mark_attendance(name, path)
                    print(f"🟢 Marked: {name}")

            cv2.imshow("Smart Attendance", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                video.release()
                cv2.destroyAllWindows()
                return

        video.release()
        cv2.destroyAllWindows()

        print(f"✅ Saved attendance: {path}")
        print(f"📤 Sending attendance via WhatsApp...")
        send_attendance_as_text(path, attendance)

        print(f"🕒 Waiting for {rest_seconds}s before next round...")
        time.sleep(rest_seconds)
        cycle += 1

if __name__ == "__main__":
    print("🔍 Starting Smart Attendance System (press 'q' to quit)...")
    take_attendance_cycle()
