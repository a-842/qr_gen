from qr_gen_class import QR_Code_String
import datetime
import os
from PIL import Image
import qr_raw_data as raw
from icecream import ic


generator = QR_Code_String(
    "bytes", "Hello", "L")
this = generator.build()
these = []
for qr in this:
    print(qr)
    these.append(qr)

ic(these)
if False:

    # Create a folder with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"snapshots_{timestamp}"
    os.makedirs(folder_name, exist_ok=True)

    # Convert each matrix to an image and save it as a PNG
    for idx, matrix in enumerate(these):
        height = len(matrix)
        width = len(matrix[0]) if height > 0 else 0
        image = Image.new("RGB", (width, height))

        # Set pixel colors based on the matrix and the color_mapping
        for y in range(height):
            for x in range(width):
                element = matrix[y][x]
                rgb = raw.color_mapping.get(element, (255, 255, 255))  # Default to white if not found
                image.putpixel((x, y), rgb)

        # Save the image as a PNG file
        image.save(os.path.join(folder_name, f"snapshot_{idx + 1}.png"))