from PIL import Image, ImageDraw

def create_icon():
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []

    for size in sizes:
        width, height = size
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Gradient/Rounded background box
        padding = int(width * 0.05)
        # Draw dark circle/rounded rect background
        draw.ellipse([padding, padding, width - padding, height - padding], fill=(30, 30, 46, 255), outline=(137, 180, 250, 255), width=max(1, int(width * 0.04)))

        # Draw lightning bolt icon in center
        # Points relative to size
        cx, cy = width / 2, height / 2
        w_factor = width / 256.0

        lightning_points = [
            (cx + 10 * w_factor, cy - 80 * w_factor),
            (cx - 60 * w_factor, cy + 10 * w_factor),
            (cx - 5 * w_factor, cy + 10 * w_factor),
            (cx - 20 * w_factor, cy + 80 * w_factor),
            (cx + 60 * w_factor, cy - 10 * w_factor),
            (cx + 5 * w_factor, cy - 10 * w_factor),
        ]

        draw.polygon(lightning_points, fill=(166, 227, 161, 255)) # Success green / energetic lightning
        images.append(img)

    # Save as ICO with multi-resolution
    images[-1].save("app_icon.ico", format="ICO", sizes=[(s[0], s[1]) for s in sizes], append_images=images[:-1])
    images[-1].save("app_icon.png", format="PNG")
    print("Icon generated successfully as app_icon.ico and app_icon.png!")

if __name__ == "__main__":
    create_icon()
