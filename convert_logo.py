from PIL import Image

img = Image.open("static/logo.png")
img.save("static/logo.ico", sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
