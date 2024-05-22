import qrcode
import os

url = os.environ.get('WEB_URL')

if url == None:
    url = 'localhost:8000/'

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=50,
    border=0,
)

full_url = url + 'room/economication'
qr.add_data(full_url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("_static/Pictures/qrcode.png")

