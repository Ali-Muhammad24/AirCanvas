import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands           # loading the hand detection module
mp_draw = mp.solutions.drawing_utils    # to draw landmarks (lines between the points) on the detected hand

hands = mp_hands.Hands(
    max_num_hands=1,                # Detect only one hand
    min_detection_confidence=0.7,   # Confidence threshold for detection
    min_tracking_confidence=0.7     # Confidence threshold for tracking
)

cam = cv2.VideoCapture(0)           # Initialize webcam
'''
create a blank canvas with the same dimensions as the webcam. A virtual canvas that will
stay on the screen and does not disappear when the new image from the webcam feed is displayed
'''
canvas = None
prev_x, prev_y = 0, 0               # to store the previous position of the index finger tip

# color palette for drawing. 
draw_color = (255, 0, 255)  # Purple default
colors = [
    (255,0,255),  # Purple
    (0,0,255),    # Red
    (0,255,255),  # Yellow
    (255,0,0),    # Blue
    (255,255,255) # White
]
circle_positions = []               # to store the positions of the color circles in the colorbar for later detection of touch interactions

# thickness levels for drawing.
draw_thickness = 2                  # default thickness
thickness_list = [2, 4, 6, 10, 15]
thickness_positions = []            # to store the positions of the thickness circles in the toolbar for later detection of touch interactions

# Clear button variables 
last_clear_time = 0
clear_delay = 1                     # 1 second delay means if the button is pressed then it wont clear again for 1 second even if the finger is still on the button.

save_counter = 1                    # to keep track of the number of saved canvases
save_triggered = False              # flag to prevent multiple saves from a single gesture

# --------------- Main loop --------------- 
while True:
    success, img = cam.read()       # Capture frame from webcam
    if not success:
        break
    
    img = cv2.flip(img, 1)          # Flip the image for mirror view
    '''
    OpenCV captures images in BGR format, while MediaPipe expects RGB format.
    Therefore, we need to convert the image from BGR to RGB before processing it with Media
    '''
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)              # Convert BGR to RGB for MediaPipe
    results = hands.process(img_rgb)                            # process the RGB image to detect hand landmarks and store the results in the 'results' variable

    if canvas is None:
        canvas = np.zeros_like(img)                             # initializing the canvas with zeros (black image)
        
    img = cv2.addWeighted(img, 0.5, canvas, 0.5, 0)             # Blends the live camera and the drawing canvas together with 50% transparency each.
        
    # --------------- UI Elements ---------------
    # Draw the colorbar background rectangle
    toolbar_top = 10
    toolbar_left = 10
    toolbar_height, toolbar_width = 50, 240

    overlay = img.copy()                                        # Create a copy of the image to draw the semi-transparent rectangle on

    # background rectangle for colorbar
    cv2.rectangle(
        overlay,
        (toolbar_left, toolbar_top),
        (toolbar_left + toolbar_width, toolbar_top + toolbar_height),
        (0,0,0),
        -1
    )

    img = cv2.addWeighted(overlay, 0.25, img, 0.75, 0)          # Blend the overlay with the original image to create a semi-transparent effect for rectangle

    # Adding the color circles to the toolbar
    circle_positions = [] 
    spacing = 45
    start_x = 35
    center_y = 35

    # loop to draw the color circles and store their positions for touch detection
    for i,color in enumerate(colors):
        cx = start_x + i*spacing                                # maths to calculate the x-coordinate of each circle 
        cy = center_y

        circle_positions.append((cx,cy))                        # store the center coordinates of each color circle in the colorbar for later use in touch detection

        cv2.circle(img, (cx,cy), 12, color, -1)                 # filled circle 
        cv2.circle(img, (cx,cy), 14, (255,255,255), 2)          # white border circle
        
    # Draw the thickness bar background rectangle
    thick_top = 10
    thick_left = toolbar_left + toolbar_width + 15
    thick_height = 50
    thick_width = 240

    overlay_thick = img.copy()

    cv2.rectangle(
        overlay_thick,
        (thick_left, thick_top),
        (thick_left + thick_width, thick_top + thick_height),
        (0,0,0),
        -1
    )

    img = cv2.addWeighted(overlay_thick, 0.25, img, 0.75, 0)

    # Draw thickness circles
    thickness_positions = []
    spacing = 45
    start_x = toolbar_left + toolbar_width + 40
    center_y = thick_top + 25

    for i, t in enumerate(thickness_list):
        cx = start_x + i*spacing
        cy = center_y

        thickness_positions.append((cx, cy))

        cv2.circle(img, (cx, cy), t, (200,200,200), -1) 
        
    # Clear button (top-right)
    btn_width, btn_height = 110, 50
    btn_x1 = toolbar_left + toolbar_width + thick_width + 30
    btn_y1 = 10
    btn_x2 = img.shape[1] - 10
    btn_y2 = btn_y1 + btn_height
    
    overlay_btn = img.copy()

    cv2.rectangle(
        overlay_btn,
        (btn_x1, btn_y1),
        (btn_x2, btn_y2),
        (0,0,0),
        -1
    )

    img = cv2.addWeighted(overlay_btn, 0.25, img, 0.75, 0)

    cv2.putText(img, "CLEAR ALL", (btn_x1 + 15, btn_y1 + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)  # Draw "CLEAR ALL" text on the button

    # --------------------------------------
    # Draw hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):     # for each detected hand (in this case, only one hand)
            mp_draw.draw_landmarks(                             # draw the hand landmarks on the image (kid that draws the hand)
                img,
                hand_landmarks,                                 # landmarks (dots) on the hand
                mp_hands.HAND_CONNECTIONS                       # lines between the landmarks on the hand
            )
            
            '''
            MediaPipe gives coordinates in a range of 0 to 1 (Normalized), and OpenCV uses pixel coordinates. To convert the normalized coordinates to pixel coordinates,
            we multiply the x-coordinate of the index finger tip (landmark 8) by the image width (shape[1]) and the y-coordinate by the image height (shape[0]) to get the 
            exact pixel location.
            '''
            index_x = int(hand_landmarks.landmark[8].x * img.shape[1])
            index_y = int(hand_landmarks.landmark[8].y * img.shape[0])
            
            # Finger states
            index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[7].y
            middle_up = hand_landmarks.landmark[12].y < hand_landmarks.landmark[11].y
            ring_up = hand_landmarks.landmark[16].y < hand_landmarks.landmark[15].y
            pinky_up = hand_landmarks.landmark[20].y < hand_landmarks.landmark[19].y

            fingers_up = sum([index_up, middle_up, ring_up, pinky_up])      # Count fingers

            # --------------- Interaction Detection ---------------
            # Detect clear button touch 
            current_time = time.time()                          # to get the current time of the system
            on_clear_button = False                             # flag to check if the finger is currently on the clear button

            if btn_x1 < index_x < btn_x2 and btn_y1 < index_y < btn_y2:     # if the index finger is on the clear button
                on_clear_button = True

                if current_time - last_clear_time > clear_delay:            # if the required delay time has passed since the last clear action, then clear the canvas
                    canvas = np.zeros_like(canvas)
                    last_clear_time = current_time
                    
            # Detect color selection
            for i,(cx,cy) in enumerate(circle_positions):
                distance = ((index_x-cx)**2 + (index_y-cy)**2)**0.5         # Calculate the distance between the fingertip and the center of each color circle

                if distance < 11:
                    draw_color = colors[i]                                  # if finger is touching that color circle then set the draw_color to that color
                    
            # Detect thickness selection
            for i,(cx,cy) in enumerate(thickness_positions):
                distance = ((index_x-cx)**2 + (index_y-cy)**2)**0.5         

                if distance < thickness_list[i] + 5:
                    draw_thickness = thickness_list[i]
                    
            # --------------- Drawing and Erasing Conditions ---------------        
            # For Pen Drawing
            is_drawing = index_up and fingers_up == 1
            
            # For Eraser
            is_erasing = index_up and middle_up and fingers_up == 2 
                        
            '''
            Create vectors from wrist to index/pinky bases and use their Cross Product to find the 'Normal' (perpendicular) vector. If the z-component of this normal 
            vector is positive (normal[2] > 0), then it means palm is facing towards the camera. 
            '''
            wrist = np.array([hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y, hand_landmarks.landmark[0].z])
            index_base = np.array([hand_landmarks.landmark[5].x, hand_landmarks.landmark[5].y, hand_landmarks.landmark[5].z])
            pinky_base = np.array([hand_landmarks.landmark[17].x, hand_landmarks.landmark[17].y, hand_landmarks.landmark[17].z])

            v1 = index_base - wrist                             # vector from wrist to index base
            v2 = pinky_base - wrist                             # vector from wrist to pinky base
            normal = np.cross(v1, v2)                           # Cross product to find the normal vector of the plane.

            # Determine palm facing direction based on handedness (left or right hand) and the sign of the z-component of the normal vector
            if handedness.classification[0].label == 'Left':
                palm_facing = normal[2] < 0
            else:
                palm_facing = normal[2] > 0
            
            # --------------- Save Canvas ---------------
            if palm_facing and fingers_up == 4:
                # Display "Saved!" in the middle
                text = "Saved!"
                (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 3)
                text_x = int((img.shape[1] - w) / 2)
                text_y = int((img.shape[0] + h) / 2)
                cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                
                if not save_triggered:                                              # only save once per gesture
                    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)                 # Convert the canvas to grayscale for better saving
                    _, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)     # binary threshold to create a binary image (black and white) of the canvas
                    signature = 255 - thresh

                    filename = f"canvas_{save_counter}.png"
                    cv2.imwrite(filename, signature)
                    save_counter += 1

                    save_triggered = True                       # prevent multiple saves while fingers stay up
            else: save_triggered = False                        # Reset flag when 4 fingers are not up

            # ------------- Drawing and Erasing Logic -----------
            # only draw or erase if the palm is facing the camera and finger isnt on the clear button and not all fingers are up 
            if palm_facing and not on_clear_button and fingers_up != 4:
                # ERASER MODE (priority)
                if is_erasing:
                    if prev_x == 0 and prev_y == 0:                 
                        prev_x, prev_y = index_x, index_y       # Initialize starting coordinates to avoid drawing a line from the top-left corner (0,0)

                    cv2.line(canvas, (prev_x, prev_y), (index_x, index_y), (0,0,0), draw_thickness*3)           # thick black line = eraser
                    cv2.circle(img, (index_x, index_y), 15, (255,255,255), 2)                                   # eraser cursor
                    
                    prev_x, prev_y = index_x, index_y           # Update previous fingertip position to the new (current) position for the next line segment

                # DRAW MODE
                elif is_drawing:
                    if prev_x == 0 and prev_y == 0:
                        prev_x, prev_y = index_x, index_y

                    cv2.line(canvas, (prev_x, prev_y), (index_x, index_y), draw_color, draw_thickness)          # coloured line = drawing 

                    prev_x, prev_y = index_x, index_y                           
                else:
                    prev_x, prev_y = 0, 0                       # Reset previous coordinates when not drawing to avoid unwanted lines when the hand moves without drawing

            else:
                prev_x, prev_y = 0, 0
                
    else:                                                       # If no hand is detected or hand is removed, reset the previous coordinates to avoid drawing lines from the last position to the new position when the hand reappears.
        prev_x, prev_y = 0, 0

    cv2.imshow("AirCanvas - Hand Tracking", img)                # Display the image

    key = cv2.waitKey(1) & 0xFF                                 # Wait for a key press and mask it to get the last 8 bits (to handle special keys)

    # Clear canvas on pressing 'c'
    if key == ord('c'):
        canvas = np.zeros_like(img)

    # Exit on pressing ESC
    if key == 27: 
        break
    
# Release resources
cam.release()
cv2.destroyAllWindows()