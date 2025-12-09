from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
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

def merge_qr_with_template(qr_path, template_path, output_path):
    bg = Image.open(template_path).convert("RGBA")   # template background
    qr = Image.open(qr_path).convert("RGBA")         # QR hasil generate

    # Resize QR agar muat (sesuaikan dengan template)
    qr = qr.resize((300, 300))  # ubah sesuai kebutuhan

    # Center-kan QR
    pos = (
        (bg.width - qr.width) // 2,
        (bg.height - qr.height) // 2
    )

    # Tempel QR ke template
    bg.paste(qr, pos, qr)

    bg.save(output_path)
    return output_path


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
        return "Input Can't null", 400

    # Path QR awal (sementara)
    qr_raw_path = os.path.join(RESULT_FOLDER, "qr_raw.png")
    
    # Generate QR dulu
    img = qrcode.make(text)
    img.save(qr_raw_path)

    # Path template
    template_path = "static/template/template1.png"

    # Path final (QR + template)
    final_path = os.path.join(RESULT_FOLDER, "valid_QR1.png")

    # Merge
    merge_qr_with_template(qr_raw_path, template_path, final_path)

    # Redirect bawa gambar final
    return redirect(url_for("index", success=1, qr="result_QR/valid_QR1.png"))


# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app.run(debug=True)