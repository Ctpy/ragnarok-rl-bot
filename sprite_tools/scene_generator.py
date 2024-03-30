import cv2
import numpy as np
from PIL import Image
import os
import random


def apply_transformation_and_paste(sprite_path, background, max_width, max_height, label):
    """Apply transformations to the sprite, paste it, and return bounding box."""
    sprite = cv2.imread(sprite_path, cv2.IMREAD_UNCHANGED)
    original_height, original_width = sprite.shape[:2]

    mirrored = random.choice([True, False])
    transparency = random.uniform(0.5, 1.0)

    if not os.path.exists(background):
        os.makedirs(background)

    if mirrored:
        sprite = cv2.flip(sprite, 1)

    alpha_channel = sprite[:, :, 3] * transparency
    sprite[:, :, 3] = alpha_channel.astype(np.uint8)

    sprite_pil = Image.fromarray(cv2.cvtColor(sprite, cv2.COLOR_BGRA2RGBA))

    x_offset = random.randint(0, max(0, max_width - original_width))
    y_offset = random.randint(0, max(0, max_height - original_height))

    background.paste(sprite_pil, (x_offset, y_offset), sprite_pil)

    # Return bounding box [x_center, y_center, width, height] normalized
    bbox = [((2 * x_offset + original_width) / 2) / max_width,
            ((2 * y_offset + original_height) / 2) / max_height,
            original_width / max_width,
            original_height / max_height,
            label]

    return bbox


def create_solid_color_background(width, height, color=(255, 255, 255)):
    """Create a solid color background."""
    background = Image.new('RGB', (width, height), color=color)
    return background


def select_random_background(background_folder, bg_width, bg_height):
    """Select a random background and resize it to the desired dimensions."""
    background_paths = [os.path.join(background_folder, f) for f in os.listdir(background_folder)]
    background_path = random.choice(background_paths)
    background = Image.open(background_path).convert("RGBA").resize((bg_width, bg_height))
    return background


def generate_scenes_and_annotations(width, height, sprite_folder, output_folder, num_images, max_sprites=5):
    sprite_paths = [os.path.join(sprite_folder, f) for f in os.listdir(sprite_folder) if f.endswith('.png')]

    annotations = []

    for i in range(num_images):
        background = create_solid_color_background(width, height)
        bg_width, bg_height = background.size

        num_sprites = random.randint(1, max_sprites)
        image_annotations = []

        for _ in range(num_sprites):
            sprite_path = random.choice(sprite_paths)
            label = os.path.splitext(os.path.basename(sprite_path))[0]  # Use file name as label
            bbox = apply_transformation_and_paste(sprite_path, background, bg_width, bg_height, label)
            image_annotations.append(bbox)

        output_path = os.path.join(output_folder, f"scene_{i + 1}.png")
        background.save(output_path)

        annotations.append({
            "image_path": output_path,
            "bboxes": image_annotations
        })

        print(f"Generated {output_path}")

    # Save annotations to a JSON file
    with open(os.path.join(output_folder, 'annotations.json'), 'w') as file:
        import json
        json.dump(annotations, file, indent=4)


sprite_folder = 'sprites'
output_folder = 'data/populated_scenes'
num_images = 100

generate_scenes_and_annotations(1920, 1080, sprite_folder, output_folder, num_images)
