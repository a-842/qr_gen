from flask import Flask, render_template, request, redirect, url_for, session
from qr_gen_class import QR_Code_String
from icecream import ic

app = Flask(__name__)
app.secret_key = 'thgis is a very secret key that nobody could ever guess'  # Required for session management

@app.route('/')
def index():
    # Render the main page with a form for user input
    return render_template('index.html')

@app.route('/input')
def take_input():

        return render_template('input.html')



@app.route('/result', methods=["post"])
def result():
    # Get data from the form submission
    data_type = request.form['data_type']
    data = request.form['data']
    eclevel = request.form['eclevel']


    # Create a QR_Code_String instance
    qr = QR_Code_String(data_type, data, eclevel)
    qr.build()  # Generate the QR code


    return render_template('result.html', 
                           encoding_type=qr.data_type,
                           length=qr.length,
                           eclevel=qr.eclevel,
                           version=qr.version,
                           length_code=qr.message_length_binary,
                           encoding_code=qr.encoding_code,
                           encoded_data=qr.binary_data,
                           padding_needed=qr.padding_needed,
                           full_binary=qr.full_binary,
                           imgs=qr.history,

                           i='image palceholder'
                           
    
                          )

if __name__ == "__main__":
    app.run(debug=True, port=5005)














