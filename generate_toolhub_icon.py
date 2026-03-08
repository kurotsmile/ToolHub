from PIL import Image, ImageDraw

size = 1024
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Background gradient approximation with layered circles
bg1 = (14, 37, 60, 255)
bg2 = (19, 111, 99, 255)
for i in range(520, 0, -1):
    t = i / 520
    r = int(bg1[0] * t + bg2[0] * (1 - t))
    g = int(bg1[1] * t + bg2[1] * (1 - t))
    b = int(bg1[2] * t + bg2[2] * (1 - t))
    draw.ellipse((size/2-i, size/2-i, size/2+i, size/2+i), fill=(r, g, b, 255))

# Outer ring
ring_color = (96, 220, 200, 255)
draw.ellipse((140, 140, 884, 884), outline=ring_color, width=52)

# Hub center
center_color = (230, 255, 248, 255)
draw.ellipse((412, 412, 612, 612), fill=center_color)

# Satellite nodes
node_fill = (156, 242, 226, 255)
node_outline = (17, 70, 78, 255)
nodes = [
    (512, 220), (760, 360), (760, 664), (512, 804), (264, 664), (264, 360)
]
for x, y in nodes:
    draw.ellipse((x-58, y-58, x+58, y+58), fill=node_fill, outline=node_outline, width=12)
    draw.line((512, 512, x, y), fill=(120, 235, 218, 255), width=24)

# Subtle inner glow
for i in range(95, 0, -1):
    alpha = int(70 * (1 - i / 95))
    draw.ellipse((512-i, 512-i, 512+i, 512+i), fill=(255, 255, 255, alpha))

img.save('toolhub_icon_new.png')
img.save('toolhub.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
print('Generated toolhub.ico and toolhub_icon_new.png')
