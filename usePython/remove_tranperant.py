import os
from PIL import Image

img_path = 'tt.png'

img = Image.open(img_path)

if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
  orig_image = img.convert('RGBA')
  background = Image.new('RGBA', img.size)
  img = Image.alpha_composite(background, img)
  img = img.convert("RGB")
  img.save('fooo', "PNG")
else:
  img.save('bar', "PNG")

# # If image has an alpha channel
# if image.mode == 'RGBA':
#   # Create a blank background image
#   bg = Image.new('RGB', image.size, (255, 255, 255))
#   # Paste image to background image
#   bg.paste(image, (0, 0), image)
#   # Save pasted image as image
#   bg.save('fooo', "PNG")