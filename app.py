import cv2
import time
import numpy as np
import serial
from handgesture import HandTracker

# Device state tracking
global_state = {
    "LIGHT1": False,
    "LIGHT2": False,
    "FAN": False,
    "TV": False,
    "LOCK": False,
    "CURTAINS": False
}

def send_command(cmd):
    # arduino.write((cmd + "\n").encode())
    # print(f"Sent: {cmd}")
    return

def toggle_main_lights():
    any_on = any(global_state.values())
    for device, state in global_state.items():
        if any_on and state:
            send_command(device)
            global_state[device] = False
        elif not any_on and not state:
            send_command(device)
            global_state[device] = True
    return "Main Lights: ALL ON" if not any_on else "Main Lights: ALL OFF"

def handle_gesture_command(fingers, states):
    msg = ""

    if not states["unlocked"]:
        return msg, states

    if fingers == [0, 1, 0, 0, 0]:  # Index finger
        send_command("LIGHT1")
        global_state["LIGHT1"] = not global_state["LIGHT1"]
        msg = f"Light 1 {'ON' if global_state['LIGHT1'] else 'OFF'}"

    elif fingers == [0, 1, 1, 0, 0]:  # Index + Middle
        send_command("LIGHT2")
        global_state["LIGHT2"] = not global_state["LIGHT2"]
        msg = f"Light 2 {'ON' if global_state['LIGHT2'] else 'OFF'}"

    elif fingers == [0, 1, 1, 1, 0]:  # Index + Middle + Ring
        send_command("TV")
        global_state["TV"] = not global_state["TV"]
        msg = f"TV {'ON' if global_state['TV'] else 'OFF'}"

    elif fingers == [0, 1, 1, 1, 1]:  # Index to Pinky
        send_command("CURTAINS")
        global_state["CURTAINS"] = not global_state["CURTAINS"]
        msg = f"Curtains {'Opened' if global_state['CURTAINS'] else 'Closed'}"

    elif fingers == [1, 1, 1, 1, 1]:  # All fingers
        if global_state["FAN"]:
            send_command("FAN_OFF")
        else:
            send_command("FAN_ON")
        global_state["FAN"] = not global_state["FAN"]
        msg = f"Fan {'ON' if global_state['FAN'] else 'OFF'}"

    elif fingers == [0, 0, 0, 0, 0]:  # Fist
        send_command("LOCK")
        global_state["LOCK"] = not global_state["LOCK"]
        msg = f"Door {'Locked' if global_state['LOCK'] else 'Unlocked'}"
    return msg, states

def draw_status_panel(image, states, status_msg):
    panel_width = 400
    height = image.shape[0]
    panel = np.zeros((height, panel_width, 3), dtype=np.uint8)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    line_height = 34
    y_start = 70

    cv2.putText(panel, "SMART HOME STATUS", (20, 40),
                cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2)

    devices = ["LIGHT1", "LIGHT2", "TV", "CURTAINS", "FAN"]
    for i, device in enumerate(devices):
        state = global_state[device]
        label = device.capitalize()
        color = (0, 255, 0) if state else (0, 0, 255)
        text = "ON" if state else "OFF"
        cv2.putText(panel, f"- {label}", (20, y_start + i * line_height),
                    font, font_scale, (255, 255, 255), 1)
        cv2.putText(panel, text, (280, y_start + i * line_height),
                    font, font_scale, color, 2)

    door_text = "LOCKED" if global_state["LOCK"] else "UNLOCKED"
    door_color = (0, 0, 255) if global_state["LOCK"] else (0, 255, 0)
    cv2.putText(panel, "- Door Lock", (20, y_start + len(devices) * line_height),
                font, font_scale, (255, 255, 255), 1)
    cv2.putText(panel, door_text, (280, y_start + len(devices) * line_height),
                font, font_scale, door_color, 2)

    security_text = "UNLOCKED" if states["unlocked"] else "LOCKED"
    security_color = (255, 219, 88) if states["unlocked"] else (93, 60, 100)
    cv2.putText(panel, "- Security System", (20, y_start + (len(devices)+1) * line_height),
                font, font_scale, (255, 255, 255), 1)
    cv2.putText(panel, security_text, (280, y_start + (len(devices)+1) * line_height),
                font, font_scale, security_color, 2)

    if status_msg:
        cv2.putText(panel, f"> {status_msg}", (20, height - 60),
                    font, 0.6, (255, 255, 120), 1)

    return np.hstack((image, panel))

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()

    states = {
        "unlocked": False
    }

    prev_x = 0
    move_counter = 0
    wave_threshold = 20
    wave_motion_detected = False
    wave_timer_start = 0

    last_command_time = 0
    cooldown = 2
    no_hand_timeout = 5
    status_msg = ""

    while True:
        success, image = cap.read()
        image = cv2.flip(image, 1)
        image = tracker.handsFinder(image)
        lmList = tracker.positionFinder(image, draw=False)

        current_time = time.time()

        if lmList:
            fingers = tracker.fingersUp(lmList)

            if fingers == [0, 1, 0, 0, 1] and not states["unlocked"]:
                states["unlocked"] = True
                status_msg = "System UNLOCKED by gesture 🤘🏻✌🏻🤘🏻"
                print(status_msg)
                last_command_time = current_time

            current_x = lmList[0][1]
            if abs(current_x - prev_x) > wave_threshold:
                if not wave_motion_detected:
                    wave_timer_start = current_time
                    wave_motion_detected = True
                move_counter += 1
                prev_x = current_x

            if wave_motion_detected and (current_time - wave_timer_start > 0.6):
                if move_counter >= 4 and states["unlocked"]:
                    status_msg = toggle_main_lights()
                    print(status_msg)
                    last_command_time = current_time
                move_counter = 0
                wave_motion_detected = False

            elif current_time - last_command_time > cooldown:
                msg, states = handle_gesture_command(fingers, states)
                if msg:
                    status_msg = msg
                    print(status_msg)
                    last_command_time = current_time

        else:
            if states["unlocked"] and current_time - last_command_time > no_hand_timeout:
                states["unlocked"] = False
                print("System LOCKED due to inactivity.")
                status_msg = "System LOCKED due to inactivity"

        combined_image = draw_status_panel(image, states, status_msg)
        cv2.imshow("Smart Home Control", combined_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    arduino.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
