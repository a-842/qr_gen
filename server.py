from flask import Flask, render_template, jsonify, send_file, request, Response, make_response, redirect, url_for
from qr_gen_class import QR_Code_String
from PIL import Image
import io
import base64
from icecream import ic
import traceback
import numpy as np

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
    return image.resize((width*8, height*8),resample=Image.BOX)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/help')
def helper():
    return render_template('help.html')

# Error Handling

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

@app.route('/error')
def error_page():
    error_log = request.args.get("error_log", "")
    return render_template("error.html", error_log=error_log)

@app.errorhandler(Exception)
def handle_exception(e):
    error_trace = traceback.format_exc()
    print(error_trace)
    return redirect(url_for("error_page", error_log=error_trace))




@app.route('/input')
def take_input():
    return render_template('input.html')

@app.route('/result', methods=["POST"])
def result():
    print("Generating a", request.form["form_type"], "QR Code")
    if request.form["form_type"] == "string":
        data_type = request.form['data_type']
        data = request.form['data']
        eclevel = request.form['eclevel']

        qr = QR_Code_String(data_type, data, eclevel)
        qr.build()

    elif request.form["form_type"] == "wifi":
        data_type = "bytes"
        data = request.form['data']

    elif request.form["form_type"] == "contact":
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
        full_binary=qr.full_binary.replace("o", "0").replace("i", "1"),
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
    img_data = base64.b64decode(cookie)
    return Response(img_data, mimetype="image/WEBP")


@app.route('/quick-download')
def quick_download():
    cookie = request.cookies.get("8")

    img_data = base64.b64decode(cookie)
    img_io = io.BytesIO(img_data)
    img_io.seek(0)

    return send_file(
        img_io,
        mimetype="image/png",
        as_attachment=True,
        download_name=f"QR.png"
    )


def is_contrasting(color1, color2):
    def luminance(rgb):
        return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
    return abs(luminance(color1) - luminance(color2)) > 125

@app.route('/advanced-download', methods=['POST'])
def advanced_download():
    data = request.json
    fg_color = tuple(int(data['foreground'][i:i+2], 16) for i in (1, 3, 5))
    bg_color = tuple(int(data['background'][i:i+2], 16) for i in (1, 3, 5))
    file_format = data['format']

    cookie = request.cookies.get("8")

    img_data = base64.b64decode(cookie)
    img_io = io.BytesIO(img_data)
    img = Image.open(img_io).convert("RGB")
    img = img.resize((int(img.size[0]/8), int(img.size[1]/8)), resample=Image.BOX)

    width, height = img.size
    img_io = io.BytesIO()  # Reset img_io to avoid conflicts

    if file_format == "txt":
        img = img.convert("1")
        qr_array = np.array(img)
        text_output = "\n".join(["".join(["  " if bit else "██" for bit in row]) for row in qr_array])
        img_io.write(text_output.encode())
        img_io.seek(0)

        return send_file(
            img_io,
            mimetype="text/plain",
            as_attachment=True,
            download_name="QR.txt"
        )

    else:
        if not is_contrasting(fg_color, bg_color):
            return jsonify({'error': 'Please select contrasting colors'}), 400
        if sum(fg_color) > sum(bg_color):
            return jsonify({'error': 'Foreground must be darker than background'}), 400
        pixels = img.load()
        pixel_list = []

        for y in range(height):
            for x in range(width):
                if sum(pixels[x, y]) < 150:
                    pixel_list.append(fg_color)
                elif sum(pixels[x, y]) > 600:
                    pixel_list.append(bg_color)
                else:
                    pixel_list.append(pixels[x, y])

        new_img = Image.new("RGB", img.size)
        new_img.putdata(pixel_list)

        new_img = new_img.resize((new_img.size[0] * 80, new_img.size[1] * 80), resample=Image.BOX)

        if file_format == "gif":
            new_img = new_img.convert("P")
        elif file_format == "jpeg":
            new_img = new_img.convert("RGB")

        new_img.save(img_io, format=file_format.upper())
        img_io.seek(0)

    return send_file(
        img_io,
        mimetype=f"image/{file_format.lower()}",
        as_attachment=True,
        download_name=f"QR.{file_format.lower()}"
    )




if __name__ == '__main__':
    app.run(debug=True)
