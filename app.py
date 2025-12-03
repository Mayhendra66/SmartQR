from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql
import qrcode
import os

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------- MODEL ----------------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

# ---------------------- QR CONFIG ----------------------
RESULT_FOLDER = "static/result_QR"
os.makedirs(RESULT_FOLDER, exist_ok=True)

# ---------------------- ROUTES ----------------------
@app.route('/')
def index():
    items = Item.query.all()

    qr_image = request.args.get("qr")
    if qr_image:
        qr_image = url_for("static", filename=qr_image)
    else:
        qr_image = url_for("static", filename="invalid_QR.png")

    success = request.args.get("success")

    return render_template("index.html", items=items, qr_image=qr_image, success=success)


# ---------------------- QR GENERATOR ----------------------
@app.route('/generate', methods=['POST'])
def generate_qr():
    text = request.form.get("qr_input")

    if not text:
        return "Input tidak boleh kosong bro", 400

    save_path = os.path.join(RESULT_FOLDER, "valid_QR1.png")

    img = qrcode.make(text)
    img.save(save_path)

    # render ulang index + gambar QR baru
    items = Item.query.all()
    qr_image = url_for("static", filename="result_QR/valid_QR1.png")

    return redirect(url_for("index", success=1, qr="result_QR/valid_QR1.png"))




# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app.run(debug=True)