from flask import Flask, render_template, request, jsonify
from qr_gen_class import QR_Code_String

app = Flask(__name__)

@app.route('/')
def index():
    # Render the main page with a form for user input
    return render_template('index.html')

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

        # Convert the QR code matrix into a displayable format
        qr_output = repr(qr)

        return jsonify({'success': True, 'qr_output': qr_output})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)