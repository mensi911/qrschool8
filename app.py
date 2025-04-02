import os
from io import BytesIO
from flask import Flask, render_template, request, send_file, flash
import qrcode
from PIL import Image
from waitress import serve

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')  # Лучше через переменные окружения

# Конфигурация
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def generate_qr():
    if request.method == 'POST':
        text = request.form.get('text')
        if not text:
            flash('Введите текст или URL для генерации QR-кода')
            return render_template('index.html')

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#000000", back_color="#FFFFFF").convert('RGB')

        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and allowed_file(logo_file.filename):
                try:
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_file.filename)
                    logo_file.save(logo_path)

                    logo = Image.open(logo_path).convert('RGBA')
                    background = Image.new('RGBA', logo.size, (255, 255, 255))
                    logo = Image.alpha_composite(background, logo).convert('RGB')

                    qr_size = qr_img.size[0]
                    logo_size = int(qr_size * 0.25)
                    logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

                    position = ((qr_size - logo.size[0]) // 2, (qr_size - logo.size[1]) // 2)
                    qr_img.paste(logo, position)

                    os.remove(logo_path)
                except Exception as e:
                    flash(f'Ошибка при обработке логотипа: {str(e)}')

        img_io = BytesIO()
        qr_img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', download_name='qr_code.png')

    return render_template('index.html')
    app = Flask(__name__, template_folder='templates')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Берём PORT из переменных окружения
    serve(app, host="0.0.0.0", port=port)
