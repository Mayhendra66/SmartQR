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

class Item(db.Model):
    __tablename__ = "item"   # pastikan sama persis dengan tabel MySQL

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))


RESULT_FOLDER = "static/result_QR"
os.makedirs(RESULT_FOLDER, exist_ok=True)

# ----------------------------------------------------------
# FIX QR MERGE — Versi HD dan valid ketika besar
# ----------------------------------------------------------
def merge_qr_with_template(qr_path, template_path, output_path, design_id):
    bg = Image.open(template_path).convert("RGBA")
    bg = bg.resize((1024, 1024), Image.LANCZOS)

    qr = Image.open(qr_path).convert("RGBA")

    qr_size = 720
    qr = qr.resize((qr_size, qr_size), Image.NEAREST)

    # 🎯 CONFIG DESAIN
    design_config = {
        "1": {"offset_y": 130},
        "2": {"offset_y": 10},
    }

    offset_y = design_config.get(design_id, {"offset_y": 130})["offset_y"]

    pos = (
        (1024 - qr_size) // 2,
        (1024 - qr_size) // 2 + offset_y
    )

    bg.paste(qr, pos, qr)
    bg.save(output_path)

    return output_path




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

@app.route('/generate', methods=['POST'])
def generate_qr():
    text = request.form.get("qr_input")
    design = request.form.get("design")  # bisa None / ""

    if not text:
        return "Input Can't null", 400

    # =========================
    # GENERATE QR ONLY (BASE)
    # =========================
    qr_raw_path = os.path.join(RESULT_FOLDER, "qr_only.png")

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4
    )

    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGBA")

    img.save(qr_raw_path)

    # 🚨 JIKA USER TIDAK PILIH DESAIN → QR SAJA
    if not design:
        return redirect(url_for(
            "index",
            success=1,
            qr="result_QR/qr_only.png"
        ))

    # =========================
    # JIKA PAKAI TEMPLATE
    # =========================
    template_map = {
        "1": "template1.png",
        "2": "template2.png"
    }

    template_file = template_map.get(design)

    # design tidak valid → fallback QR only
    if not template_file:
        return redirect(url_for(
            "index",
            success=1,
            qr="result_QR/qr_only.png"
        ))

    template_path = f"static/template/{template_file}"
    final_path = os.path.join(RESULT_FOLDER, f"valid_QR_{design}.png")

    merge_qr_with_template(
        qr_raw_path,
        template_path,
        final_path,
        design
    )

    return redirect(url_for(
        "index",
        success=1,
        qr=f"result_QR/valid_QR_{design}.png"
    ))





# RUN APLIKASI
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

