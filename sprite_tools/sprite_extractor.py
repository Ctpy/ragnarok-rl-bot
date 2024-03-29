import cv2
import os
import json
import numpy as np
import pytesseract
from collections import Counter
from logging import getLogger
from tqdm import tqdm

from sprite_tools.monster import load_monster_object

logger = getLogger(__name__)


def find_background_color(image):
    """Find the most common color in the image, assuming it's the background."""
    data = np.reshape(image, (-1, 3))
    most_common_color = Counter(map(tuple, data)).most_common(1)[0][0]
    return most_common_color


def create_mask(image, background_color):
    """Create a binary mask where the background pixels are 0 and all others are 1."""
    mask = cv2.inRange(image, np.array(background_color), np.array(background_color))
    return 1 - mask // 255


def is_mostly_background_or_black(image, background_color_rgb, threshold=0.95):
    """Check if the image mostly contains the background color or black."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = np.reshape(image_rgb, (-1, 3))
    color_counts = Counter(map(tuple, pixels))
    if len(color_counts) > 2:
        return True
    return False


def contains_text(image):
    """Use OCR to detect if the image contains significant text."""
    # Convert the image to a format suitable for OCR
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Use Tesseract to detect text
    text = pytesseract.image_to_string(gray_image, lang='eng')
    # Consider an image to contain text if Tesseract returns non-whitespace characters
    return bool(text.strip())


def crop_and_save_entities(monster_name, monster_id, image_path, min_width=20, min_height=20):
    image = cv2.imread(image_path)
    background_color = find_background_color(image)

    mask = create_mask(image, background_color)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    metadata = []

    save_dir = 'sprites'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    if not os.path.exists(save_dir + f"/{monster_id}"):
        os.makedirs(save_dir + f"/{monster_id}")

    counter = 0
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        if w >= min_width and h >= min_height:
            filename = f"{save_dir}/{monster_id}/sprite_{monster_id}_{counter}.png"
            cropped = image[y - 2:y + h + 2, x - 2:x + w + 2]
            if cropped.size == 0:
                logger.warning(f"Skipping empty image: {filename}")
                continue
            if not is_mostly_background_or_black(cropped, background_color):
                continue
            if contains_text(cropped):
                continue

            filepath = os.path.join(save_dir, str(monster_id), filename)
            counter += 1
            cv2.imwrite(filename, cropped)
            logger.debug(f"Saved: {filename}")
            metadata.append({
                "id": f"{monster_id}_{i}",
                "label": monster_name,
                "file_path": filepath,
                "dimensions": {"width": w, "height": h}
            })

    with open(os.path.join(save_dir + f"/{monster_id}", 'metadata.json'), 'w') as json_file:
        json.dump(metadata, json_file, indent=4)


sprite_dir = 'images'
for file in tqdm(os.listdir(sprite_dir)):
    if file.endswith('.png'):
        monster_id = file.split('_')[-1].split('.')[0]
        monster_raw_object_path = os.path.join('monster_raw_objects', f'monster_raw_{monster_id}.pkl')
        monster_raw_object = load_monster_object(monster_raw_object_path)
        crop_and_save_entities(monster_raw_object.name, monster_id, os.path.join(sprite_dir, file))
