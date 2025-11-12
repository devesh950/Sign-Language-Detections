import cv2, os

label = input("Enter label for sign (e.g., A): ").upper()
save_path = f'dataset/{label}'
os.makedirs(save_path, exist_ok=True)

cap = cv2.VideoCapture(0)
count = 0
print("Press 's' to save image, 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('Capture', frame)
    key = cv2.waitKey(1)

    if key & 0xFF == ord('s'):
        file_path = os.path.join(save_path, f'{label}_{count}.jpg')
        cv2.imwrite(file_path, frame)
        count += 1
        print(f"Saved {file_path}")

    elif key & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
