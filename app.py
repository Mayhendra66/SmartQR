from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import qrcode
import os

app = Flask(__name__)

# =========================
# FOLDER OUTPUT QR
# =========================
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


# =========================
# ROUTE INDEX
# =========================
@app.route('/')
def index():
    qr_image = request.args.get("qr")
    if qr_image:
        qr_image = url_for("static", filename=qr_image)
    else:
        qr_image = url_for("static", filename="invalid_QR.png")

    success = request.args.get("success")

    return render_template(
        "index.html",
        qr_image=qr_image,
        success=success
    )


# =========================
# GENERATE QR
# =========================
@app.route('/generate', methods=['POST'])
def generate_qr():
    text = request.form.get("qr_input")
    design = request.form.get("design")  # bisa None / ""

    if not text:
        return "Input Can't null", 400

    # =========================
    # GENERATE QR ONLY
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

    # 🚨 JIKA TIDAK PILIH DESAIN
    if not design:
        return redirect(url_for(
            "index",
            success=1,
            qr="result_QR/qr_only.png"
        ))

    # =========================
    # TEMPLATE QR
    # =========================
    template_map = {
        "1": "template1.png",
        "2": "template2.png"
    }

    template_file = template_map.get(design)

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


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
