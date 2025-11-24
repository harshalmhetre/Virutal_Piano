import cv2
import mediapipe as mp
import pygame
import numpy as np

wCam, hCam = 640, 480
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

SOUND_FOLDER = "tones"

NOTES = ['C4', 'Cs4', 'D4', 'Ds4', 'E4', 'F4', 'Fs4', 'G4', 'Gs4', 'A4', 'As4', 'B4']

SOUNDS = []
for note in NOTES:
    try:
        SOUNDS.append(pygame.mixer.Sound(f"{SOUND_FOLDER}/{note}.mp3"))
    except:
        try:
            SOUNDS.append(pygame.mixer.Sound(f"{SOUND_FOLDER}/{note}.wav"))
        except:
            print(f"Warning: Could not load sound for {note}")
            SOUNDS.append(None)


WHITE_X = [100, 180, 260, 340, 420, 500, 580]  
BLACK_X = [140, 220, 380, 460, 540]            

WHITE_INDICES = [0, 2, 4, 5, 7, 9, 11]   # C, D, E, F, G, A, B
BLACK_INDICES = [1, 3, 6, 8, 10]         # C#, D#, F#, G#, A#

WHITE_W, WHITE_H = 75, 280
BLACK_W, BLACK_H = 50, 180


COOLDOWN = 0.08  

last_played = {}
key_was_pressed = {}  
for i in range(12):
    last_played[i] = -100
    key_was_pressed[i] = False

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

def is_inside_key(x, y, key_x, key_y, key_w, key_h):
    """Check if point (x,y) is inside a key rectangle"""
    return (key_x < x < key_x + key_w) and (key_y < y < key_y + key_h)

def draw_keys(img, highlighted_keys):
    """Draw piano keys with transparency effect"""
    
    overlay = img.copy()
    
    
    for i, idx in enumerate(WHITE_INDICES):
        x = WHITE_X[i] - WHITE_W//2
        y = 150
        
        
        if idx in highlighted_keys:
            color = (100, 255, 100)  
        else:
            color = (255, 255, 255)  
        
        cv2.rectangle(overlay, (x, y), (x + WHITE_W, y + WHITE_H), color, -1)
        cv2.rectangle(overlay, (x, y), (x + WHITE_W, y + WHITE_H), (0, 0, 0), 3)
        
        
        label = NOTES[idx].replace('s', '#')[:-1]  
        cv2.putText(overlay, label, (x + 20, y + WHITE_H - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    for i, idx in enumerate(BLACK_INDICES):
        x = BLACK_X[i] - BLACK_W//2
        y = 100
        
        if idx in highlighted_keys:
            color = (100, 255, 255)  
        else:
            color = (0, 0, 0)  
        
        cv2.rectangle(overlay, (x, y), (x + BLACK_W, y + BLACK_H), color, -1)
        cv2.rectangle(overlay, (x, y), (x + BLACK_W, y + BLACK_H), (255, 255, 255), 2)
        
       
        label = NOTES[idx].replace('s', '#')[:-1]
        cv2.putText(overlay, label, (x + 10, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    alpha = 0.7  
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    cv2.putText(img, "Virtual Piano - C D E F G A B Octave", (80, 50), 
                cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)

print("Virtual Piano Started!")
print("- Piano layout: C D E F G A B (with sharps)")
print("- Use your INDEX and MIDDLE fingers to play")
print("- Keys can be played repeatedly!")
print("- Press 'q' to quit")

while True:
    success, img = cap.read()
    if not success:
        break
    
    img = cv2.flip(img, 1)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    current_time = pygame.time.get_ticks() / 1000.0
    highlighted_keys = []
    keys_currently_pressed = set()  

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = hand_landmarks.landmark
            fingers = [8, 12] 
            
            for finger_id in fingers:
                x = int(landmarks[finger_id].x * wCam)
                y = int(landmarks[finger_id].y * hCam)
                
                cv2.circle(img, (x, y), 12, (0, 0, 255), -1)
                cv2.circle(img, (x, y), 12, (255, 255, 255), 3)

                triggered = False
                for i, idx in enumerate(BLACK_INDICES):
                    key_x = BLACK_X[i] - BLACK_W//2
                    key_y = 100
                    
                    if is_inside_key(x, y, key_x, key_y, BLACK_W, BLACK_H):
                        keys_currently_pressed.add(idx)
                        
                        time_since_last = current_time - last_played[idx]
                        is_new_press = not key_was_pressed[idx]
                        
                        if time_since_last > COOLDOWN or is_new_press:
                            if SOUNDS[idx]:
                                SOUNDS[idx].stop()  
                                SOUNDS[idx].play()
                            last_played[idx] = current_time
                            print(f"Played: {NOTES[idx]}")
                        
                        triggered = True
                        break
                
                
                if not triggered:
                    for i, idx in enumerate(WHITE_INDICES):
                        key_x = WHITE_X[i] - WHITE_W//2
                        key_y = 150
                        
                        if is_inside_key(x, y, key_x, key_y, WHITE_W, WHITE_H):
                            keys_currently_pressed.add(idx)
                            
                            
                            time_since_last = current_time - last_played[idx]
                            is_new_press = not key_was_pressed[idx]
                            
                            if time_since_last > COOLDOWN or is_new_press:
                                if SOUNDS[idx]:
                                    SOUNDS[idx].stop()  
                                    SOUNDS[idx].play()
                                last_played[idx] = current_time
                                print(f"Played: {NOTES[idx]}")
                            
                            break
    
    for i in range(12):
        time_since_played = current_time - last_played[i]
        if i in keys_currently_pressed or (time_since_played < 0.1 and time_since_played > 0):
            highlighted_keys.append(i)
    
    for i in range(12):
        key_was_pressed[i] = (i in keys_currently_pressed)
    
    draw_keys(img, highlighted_keys)

    cv2.imshow("Virtual Piano - C D E F G A B Octave", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
print("Piano closed!")