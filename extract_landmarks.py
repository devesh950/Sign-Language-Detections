import mediapipe as mp
import cv2, os, csv, numpy as np

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)
header = ['label'] + [f'{coord}{i}' for i in range(21) for coord in ('x','y','z')]

with open('landmarks_dataset.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)

    dataset_path = 'Gesture Image Data'
    for label in sorted(os.listdir(dataset_path)):
        folder = os.path.join(dataset_path, label)
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            img = cv2.imread(path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            res = hands.process(img_rgb)

            if res.multi_hand_landmarks:
                lm = res.multi_hand_landmarks[0]
                data = [label]
                for p in lm.landmark:
                    data += [p.x, p.y, p.z]
                writer.writerow(data)

print("✅ Landmark CSV saved as landmarks_dataset.csv")
