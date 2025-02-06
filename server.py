from flask import Flask, render_template, request, Response, make_response
from qr_gen_class import QR_Code_String
from PIL import Image
import io
import base64
from icecream import ic

app = Flask(__name__)
app.secret_key = 'guess'

def split_data(data, chunk_size=4000):
    return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

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
    return image#.resize((200, 200),resample=Image.BOX)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/help')
def helper():
    return render_template('help.html')

@app.route('/input')
def take_input():
    return render_template('input.html')

@app.route('/result', methods=["POST"])
def result():
    if request.form["qr_type"] == "string":
        data_type = request.form['data_type']
        data = request.form['data']
        eclevel = request.form['eclevel']

        qr = QR_Code_String(data_type, data, eclevel)
        qr.build()

    if request.form["qr_type"] == "wifi":
        data_type = "bytes"
        data = request.form['data']

    elif request.form["qr_type"] == "contact":
        data_type = "bytes"


    # Save images in session for serving later
    imagedata = []
    for step in qr.history:
        img = create_image_from_pattern(step)
        img_io = io.BytesIO()
        img.save(img_io, "WEBP")
        img_io.seek(0)
        imagedata.append(base64.b64encode(img_io.getvalue()).decode('utf-8'))
    eval_list = []
    for step in qr.masks:
        img = create_image_from_pattern(step[0])
        img_io = io.BytesIO()

        img.save(img_io, "WEBP")
        img_io.seek(0)
        eval_list.append(step[1])
        imagedata.append(

                base64.b64encode(img_io.getvalue()).decode('utf-8'),
        )
    ic(eval_list)

    resp = make_response(render_template(
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
        eval_list=eval_list,
        mask_id=qr.mask_id,
        format_strip_combined_bits=qr.format_strip_combined_bits,
        format_strip=qr.format_strip,


    ))
    for idx, image in enumerate(imagedata):
        ic(image)
        resp.set_cookie(str(idx), image)

    return resp

@app.route('/image/<int:image_index>')
def serve_image(image_index):
    cookie = request.cookies.get(str(image_index))
    img_data = base64.b64decode(cookie)#.resize((200, 200),resample=Image.BOX)
    return Response(img_data, mimetype="image/WEBP")


if __name__ == "__main__":
    app.run(debug=True, port=5006)
