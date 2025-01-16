from flask import Flask, render_template, request, Response, session
from qr_gen_class import QR_Code_String
from PIL import Image
import io
import base64

app = Flask(__name__)
app.secret_key = 'this is a very secret key that nobody could ever guess'

def create_image_from_pattern(pattern):
    rows = pattern.strip().split("\n")
    height = len(rows)
    width = len(rows[0])
    image = Image.new("RGB", (width, height), "black")
    pixels = image.load()
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char == '-':
                pixels[x, y] = (127, 127, 127)
            elif char == '1':
                pixels[x, y] = (0,0,0)
            elif char == '0':
                pixels[x, y] = (255, 255, 255)
            elif char == 'i':
                pixels[x, y] = (63, 63, 63)
            elif char == 'o':
                pixels[x, y] = (187, 187, 187)
            elif char == 'f':
                pixels[x, y] = (0,255,0)
    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input')
def take_input():
    return render_template('input.html')

@app.route('/result', methods=["POST"])
def result():
    data_type = request.form['data_type']
    data = request.form['data']
    eclevel = request.form['eclevel']

    qr = QR_Code_String(data_type, data, eclevel)
    qr.build()

    # Save images in session for serving later
    session['images'] = []
    for step in qr.history:
        img = create_image_from_pattern(step)
        img_io = io.BytesIO()
        img.save(img_io, "PNG")
        img_io.seek(0)
        session['images'].append(base64.b64encode(img_io.getvalue()).decode('utf-8'))

    return render_template(
        'result.html',
        encoding_type=qr.data_type,
        length=qr.length,
        eclevel=qr.eclevel,
        version=qr.version,
        length_code=qr.message_length_binary,
        encoding_code=qr.encoding_code,
        encoded_data=qr.binary_data,
        padding_needed=qr.padding_needed,
        full_binary=qr.full_binary,
        imgs=range(len(session['images']))
    )

@app.route('/image/<int:index>')
def serve_image(index):
    if 'images' in session and 0 <= index < len(session['images']):
        img_data = base64.b64decode(session['images'][index])
        return Response(img_data, mimetype="image/png")
    return "Image not found", 404

if __name__ == "__main__":
    app.run(debug=True, port=5005)
