from flask import Flask, render_template, request, redirect, url_for, session
from qr_gen_class import QR_Code_String

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

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
        qr_history = qr.build()  # Generate the QR code

        # Convert the QR code matrix into a displayable format
        qr_output = repr(qr)

        # Store the result in the session to pass it to the results page

        session['qr_object'] = qr
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
