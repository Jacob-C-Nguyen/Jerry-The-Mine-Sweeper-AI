import pyautogui
import cv2
import numpy as np
import os
import time

# Make sure we operate in the script’s directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# LOAD ALL TEMPLATES
# ============================================================

TEMPLATE_THRESHOLD = 0.70  # tune as needed
CELL_SIZE = 20             # templates are ~20×20
GRID_ROWS = 9
GRID_COLS = 9

# Load images (None if not present)
def load_gray(path):
    if not os.path.exists(path):
        print(f"[Vision] Missing template: {path}")
        return None
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

templates_gray = {
    "smiley": load_gray("templates/smiley.png"),
    "hidden": load_gray("templates/hidden.png"),
    "flag"  : load_gray("templates/flag.png"),
    "cell_1": load_gray("templates/cell_1.png"),
    "cell_2": load_gray("templates/cell_2.png"),
    "cell_3": load_gray("templates/cell_3.png")
}

# Load digits
#for i in range(9):
#    templates_gray[f"cell_{i}"] = load_gray(f"cell_{i}.png")

# ============================================================
# TEMPLATE MATCHING
# ============================================================

def match_template(cell_gray, template_gray):
    """
    Resize the sampled cell to the template size so matchTemplate works reliably.
    """
    th, tw = template_gray.shape
    resized = cv2.resize(cell_gray, (tw, th), interpolation=cv2.INTER_LINEAR)
    result = cv2.matchTemplate(resized, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val


def locate_template(screen_gray, template_gray, threshold=TEMPLATE_THRESHOLD):
    """
    Return top-left (x, y) of template in screenshot or None.
    """
    result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)

    for pt in zip(*loc[::-1]):
        return pt  # first match

    return None


# ============================================================
# SMILEY LOCATOR → BOARD ORIGIN
# ============================================================

def locate_smiley(screen_gray):
    temp = templates_gray["smiley"]
    if temp is None:
        raise RuntimeError("Smiley template not loaded.")

    pt = locate_template(screen_gray, temp)
    if pt is None:
        raise RuntimeError("Smiley not found on screen.")

    return pt  # (x, y)


def get_board_origin(screen_gray):
    sx, sy = locate_smiley(screen_gray)

    # Offsets tuned for minesweeperonline.com (100% zoom)
    origin_x = sx - 120
    origin_y = sy + 60

    return origin_x, origin_y


# ============================================================
# EXTRACT & CLASSIFY CELLS
# ============================================================

def get_cell(screen_gray, origin, row, col):
    x = origin[0] + col * CELL_SIZE
    y = origin[1] + row * CELL_SIZE
    return screen_gray[y:y+CELL_SIZE, x:x+CELL_SIZE]


def classify_cell(cell_gray):
    # Hidden
    temp = templates_gray["hidden"]
    if temp is not None:
        if match_template(cell_gray, temp) >= TEMPLATE_THRESHOLD:
            return "H"

    # Flag
    temp = templates_gray["flag"]
    if temp is not None:
        if match_template(cell_gray, temp) >= TEMPLATE_THRESHOLD:
            return "F"

    # Numbers 0–8
    best_digit = None
    best_val = 0.0

    for i in range(9):
        temp = templates_gray[f"cell_{i}"]
        if temp is None:
            continue

        val = match_template(cell_gray, temp)
        if val > best_val:
            best_val = val
            best_digit = str(i)

    if best_digit is not None and best_val >= TEMPLATE_THRESHOLD:
        return best_digit

    return "?"


# ============================================================
# READ FULL 9×9 BOARD
# ============================================================

def read_board():
    screenshot = pyautogui.screenshot()
    screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

    origin = get_board_origin(screen)

    board = []
    for r in range(GRID_ROWS):
        row_vals = []
        for c in range(GRID_COLS):
            cell_img = get_cell(screen, origin, r, c)
            row_vals.append(classify_cell(cell_img))
        board.append(row_vals)

    return board


# ============================================================
# DEBUG TEST
# ============================================================

if __name__ == "__main__":
    time.sleep(5)
    board = read_board()
    for row in board:
        print(row)
