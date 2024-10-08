import qrcode

# Define the URL you want to encode in the QR code
url = "https://www.example.com"

# Create a QR code instance
qr = qrcode.QRCode(
    version=1,  # QR code version (1-40, higher is denser)
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
    box_size=10,  # Size of each box in the QR code
    border=4,  # Border size around the QR code
)
qr.add_data(url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("qr_code.png")
img.show()