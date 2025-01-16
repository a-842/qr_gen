from flask import Flask, render_template, request, redirect, url_for, session
from qr_gen_class import QR_Code_String
from icecream import ic

app = Flask(__name__)
app.secret_key = 'thgis is a very secret key that nobody could ever guess'  # Required for session management

@app.route('/')
def index():
    # Render the main page with a form for user input
    return render_template('input.html')

@app.route('/generate', methods=['POST'])
def generate_qr():
    try:
        # Get data from the form submission
        data_type = request.form['data_type']
        data = request.form['data']
        eclevel = request.form['eclevel']

        # Create a QR_Code_String instance
        qr = QR_Code_String(data_type, data, eclevel)
        qr.build()  # Generate the QR code

        # Generate the QR code image (assuming it's a PIL image)
        qr_image = qr.get_string()  # Ensure you have a method to get the image

        # Store the result in the session to pass it to the results page
        session['qr_image'] = qr_image
        session['error'] = None

        # Redirect to the result page
        return redirect(url_for('result'))
    except Exception as e:
        # Store the error in the session and redirect to the results page
        session['error'] = str(e)
        session['qr_object'] = None
        return redirect(url_for('result'))

@app.route('/result')
def result():
    # Retrieve the QR code or error from the session
    qr_object = session.get('qr_object')
    error = session.get('error')
    return render_template('result.html', qr_output=str(qr_object))

if __name__ == "__main__":
    app.run(debug=True, port=5005)
