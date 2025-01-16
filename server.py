from flask import Flask, render_template, request, redirect, url_for, session
from qr_gen_class import QR_Code_String
from icecream import ic

app = Flask(__name__)
app.secret_key = 'thgis is a very secret key that nobody could ever guess'  # Required for session management

@app.route('/')
def index():
    # Render the main page with a form for user input
    return render_template('index.html')

@app.route('/input', methods=['POST'])
def generate_qr():
    # Get data from the form submission
        data_type = request.form['data_type']
        data = request.form['data']
        eclevel = request.form['eclevel']
    #save the user input in the session
        session["data_type"] = data_type
        session["data"] = data
        session["eclevel"] = ecevel


@app.route('/result')
def result():
    # Retrieve the QR code or error from the session
    data_type = session.get("data_type")
    data = session.get("data")
    eclevel = session.get("eclevel")

    # Create a QR_Code_String instance
    qr = QR_Code_String(data_type, data, eclevel)
    qr.build()  # Generate the QR code


    return render_template('result.html', 
                           encoding_type=qr.encoding,
                           length=qr.length,
                           eclevel=qr.eclevel,
                           version=qr.version,
                           
    
                          )

if __name__ == "__main__":
    app.run(debug=True, port=5005)














