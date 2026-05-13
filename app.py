"""
Smart Certificate Verification System Using QR Code
====================================================
A secure web application for institutions to digitally create,
manage, and verify certificates using QR codes.

Author: Smart Cert System
Version: 1.0.0
"""

import os
import io
import uuid
import qrcode
import hashlib
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, send_file, jsonify, abort)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont
import base64

# ─── App Configuration ─────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'smartcert-secret-key-2026-secure')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['QR_CODE_FOLDER'] = os.path.join(BASE_DIR, 'static', 'qr_codes')
app.config['CERT_FOLDER'] = os.path.join(BASE_DIR, 'static', 'certificates')

db = SQLAlchemy(app)

# ─── Database Models ────────────────────────────────────────────────────────────

class Admin(db.Model):
    """Admin user model for authentication."""
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Certificate(db.Model):
    """Certificate model storing all certificate information."""
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    student_name = db.Column(db.String(200), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(200), nullable=False)
    institution_name = db.Column(db.String(300), nullable=False)
    issue_date = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    qr_code_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'student_name': self.student_name,
            'course_name': self.course_name,
            'department': self.department,
            'institution_name': self.institution_name,
            'issue_date': self.issue_date,
            'grade': self.grade,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


# ─── Helper Functions ───────────────────────────────────────────────────────────

def login_required(f):
    """Decorator to protect admin routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please login to access the admin panel.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def generate_certificate_id():
    """Generate a unique certificate ID in format CERT-YYYY-NNN."""
    year = datetime.now().year
    # Count existing certs this year
    prefix = f"CERT-{year}-"
    count = Certificate.query.filter(
        Certificate.certificate_id.like(f"{prefix}%")
    ).count()
    seq = str(count + 1).zfill(3)
    cert_id = f"{prefix}{seq}"
    # Ensure uniqueness
    while Certificate.query.filter_by(certificate_id=cert_id).first():
        count += 1
        seq = str(count + 1).zfill(3)
        cert_id = f"{prefix}{seq}"
    return cert_id


def generate_qr_code(certificate_id):
    """Generate a QR code for the given certificate ID and save it."""
    verify_url = f"http://127.0.0.1:5000/verify/{certificate_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="#1a1a2e", back_color="white")
    filename = f"{certificate_id}.png"
    filepath = os.path.join(app.config['QR_CODE_FOLDER'], filename)
    qr_img.save(filepath)

    return f"qr_codes/{filename}"


def get_qr_base64(certificate_id):
    """Return the QR code as a base64 string for embedding in HTML."""
    filepath = os.path.join(app.config['QR_CODE_FOLDER'], f"{certificate_id}.png")
    if not os.path.exists(filepath):
        generate_qr_code(certificate_id)
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def generate_certificate_image(cert):
    """Generate a professional certificate image using Pillow."""
    width, height = 1123, 794  # A4 landscape @ 96dpi

    # Background
    img = Image.new('RGB', (width, height), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    # ─ Decorative border ─
    border_color = '#1a1a2e'
    gold_color = '#c9a84c'

    # Outer border
    draw.rectangle([15, 15, width - 15, height - 15],
                   outline=border_color, width=4)
    # Inner gold border
    draw.rectangle([30, 30, width - 30, height - 30],
                   outline=gold_color, width=2)

    # Top color band
    draw.rectangle([15, 15, width - 15, 100], fill='#1a1a2e')

    # Bottom color band
    draw.rectangle([15, height - 100, width - 15, height - 15], fill='#1a1a2e')

    # Header text
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 36)
        sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 20)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf", 44)
    except Exception:
        title_font = sub_font = body_font = small_font = name_font = ImageFont.load_default()

    # Institution name (top band)
    inst = cert.institution_name.upper()
    draw.text((width // 2, 57), inst, fill='white', font=sub_font, anchor='mm')

    # "CERTIFICATE OF COMPLETION"
    draw.text((width // 2, 140), "CERTIFICATE", fill='#1a1a2e', font=title_font, anchor='mm')
    draw.text((width // 2, 185), "OF COMPLETION", fill=gold_color, font=sub_font, anchor='mm')

    # Horizontal divider
    draw.line([(100, 210), (width - 100, 210)], fill=gold_color, width=1)

    # "This is to certify that"
    draw.text((width // 2, 240), "This is to certify that", fill='#555555', font=body_font, anchor='mm')

    # Student name
    draw.text((width // 2, 290), cert.student_name, fill='#1a1a2e', font=name_font, anchor='mm')

    # Underline for name
    name_bbox = draw.textbbox((width // 2, 290), cert.student_name, font=name_font, anchor='mm')
    draw.line([(name_bbox[0], name_bbox[3] + 5), (name_bbox[2], name_bbox[3] + 5)], fill=gold_color, width=1)

    # Course text
    draw.text((width // 2, 355),
              f"has successfully completed the course",
              fill='#555555', font=body_font, anchor='mm')
    draw.text((width // 2, 390),
              f'"{cert.course_name}"',
              fill='#1a1a2e', font=sub_font, anchor='mm')

    # Department
    draw.text((width // 2, 430),
              f"Department of {cert.department}",
              fill='#777777', font=small_font, anchor='mm')

    # Details row
    details_y = 480
    draw.text((220, details_y), "Date of Issue", fill='#999999', font=small_font, anchor='mm')
    draw.text((220, details_y + 22), cert.issue_date, fill='#1a1a2e', font=body_font, anchor='mm')

    draw.text((width // 2, details_y), "Grade", fill='#999999', font=small_font, anchor='mm')
    draw.text((width // 2, details_y + 22), cert.grade, fill='#1a1a2e', font=body_font, anchor='mm')

    draw.text((width - 220, details_y), "Certificate ID", fill='#999999', font=small_font, anchor='mm')
    draw.text((width - 220, details_y + 22), cert.certificate_id, fill='#1a1a2e', font=small_font, anchor='mm')

    # Horizontal divider
    draw.line([(100, 530), (width - 100, 530)], fill='#dddddd', width=1)

    # Signature placeholders
    sig_y = 580
    draw.line([(160, sig_y), (340, sig_y)], fill='#1a1a2e', width=1)
    draw.text((250, sig_y + 12), "Authorized Signatory", fill='#777777', font=small_font, anchor='mm')

    draw.line([(width - 340, sig_y), (width - 160, sig_y)], fill='#1a1a2e', width=1)
    draw.text((width - 250, sig_y + 12), "Institution Seal", fill='#777777', font=small_font, anchor='mm')

    # QR Code (right side)
    qr_path = os.path.join(app.config['QR_CODE_FOLDER'], f"{cert.certificate_id}.png")
    if os.path.exists(qr_path):
        qr_img = Image.open(qr_path).resize((120, 120))
        img.paste(qr_img, (width // 2 - 60, 600))
        draw.text((width // 2, 732), "Scan to verify", fill='white', font=small_font, anchor='mm')

    # Bottom band text
    draw.text((width // 2, height - 57), "Verify at: http://127.0.0.1:5000/verify/" + cert.certificate_id,
              fill='#aaaaaa', font=small_font, anchor='mm')

    # Save
    filename = f"{cert.certificate_id}.png"
    filepath = os.path.join(app.config['CERT_FOLDER'], filename)
    img.save(filepath, 'PNG', quality=95)
    return f"certificates/{filename}"


# ─── Routes: Public ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Landing/Home page."""
    total_certs = Certificate.query.count()
    return render_template('index.html', total_certs=total_certs)


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """Public certificate verification page."""
    cert_data = None
    status = None
    searched_id = ''

    if request.method == 'POST':
        cert_id = request.form.get('certificate_id', '').strip().upper()
        searched_id = cert_id

        if cert_id:
            cert = Certificate.query.filter_by(certificate_id=cert_id).first()
            if cert:
                status = 'valid'
                cert_data = cert
            else:
                status = 'invalid'
        else:
            flash('Please enter a Certificate ID.', 'warning')

    return render_template('verify.html', cert=cert_data, status=status, searched_id=searched_id)


@app.route('/verify/<certificate_id>')
def verify_direct(certificate_id):
    """Direct verification via QR code scan."""
    cert_id = certificate_id.strip().upper()
    cert = Certificate.query.filter_by(certificate_id=cert_id).first()
    if cert:
        return render_template('verify.html', cert=cert, status='valid', searched_id=cert_id)
    return render_template('verify.html', cert=None, status='invalid', searched_id=cert_id)


@app.route('/certificate/<certificate_id>')
def certificate_preview(certificate_id):
    """Certificate preview page."""
    cert = Certificate.query.filter_by(certificate_id=certificate_id.upper()).first()
    if not cert:
        return render_template('error.html', cert_id=certificate_id)

    qr_b64 = get_qr_base64(cert.certificate_id)
    return render_template('certificate_preview.html', cert=cert, qr_b64=qr_b64)


@app.route('/download/<certificate_id>')
def download_certificate(certificate_id):
    """Download certificate as PNG image."""
    cert = Certificate.query.filter_by(certificate_id=certificate_id.upper()).first()
    if not cert:
        return render_template('error.html', cert_id=certificate_id)

    cert_path = os.path.join(app.config['CERT_FOLDER'], f"{cert.certificate_id}.png")
    if not os.path.exists(cert_path):
        generate_certificate_image(cert)

    return send_file(cert_path, as_attachment=True,
                     download_name=f"Certificate_{cert.certificate_id}.png")


# ─── Routes: Admin Auth ─────────────────────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if 'admin_logged_in' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/admin/logout')
def logout():
    """Admin logout."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# ─── Routes: Admin Dashboard ────────────────────────────────────────────────────

@app.route('/admin/dashboard')
@login_required
def dashboard():
    """Admin dashboard with stats and recent certificates."""
    total = Certificate.query.count()
    recent = Certificate.query.order_by(Certificate.created_at.desc()).limit(10).all()
    this_month = Certificate.query.filter(
        db.extract('month', Certificate.created_at) == datetime.now().month,
        db.extract('year', Certificate.created_at) == datetime.now().year
    ).count()
    return render_template('dashboard.html', total=total, recent=recent,
                           this_month=this_month, now=datetime.now())


@app.route('/admin/certificates')
@login_required
def manage_certificates():
    """View and manage all certificates."""
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Certificate.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Certificate.student_name.ilike(like),
                Certificate.certificate_id.ilike(like),
                Certificate.course_name.ilike(like),
                Certificate.department.ilike(like)
            )
        )

    certs = query.order_by(Certificate.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False)
    return render_template('manage_certificates.html', certs=certs, search=search)


@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_certificate():
    """Add a new certificate."""
    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip()
        course_name = request.form.get('course_name', '').strip()
        department = request.form.get('department', '').strip()
        institution_name = request.form.get('institution_name', '').strip()
        issue_date = request.form.get('issue_date', '').strip()
        grade = request.form.get('grade', '').strip()
        description = request.form.get('description', '').strip()

        # Validation
        errors = []
        if not student_name:
            errors.append('Student name is required.')
        if not course_name:
            errors.append('Course name is required.')
        if not department:
            errors.append('Department is required.')
        if not institution_name:
            errors.append('Institution name is required.')
        if not issue_date:
            errors.append('Issue date is required.')
        if not grade:
            errors.append('Grade is required.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('add_certificate.html',
                                   form_data=request.form)

        # Generate unique ID and QR
        cert_id = generate_certificate_id()
        qr_path = generate_qr_code(cert_id)

        # Save to DB
        cert = Certificate(
            certificate_id=cert_id,
            student_name=student_name,
            course_name=course_name,
            department=department,
            institution_name=institution_name,
            issue_date=issue_date,
            grade=grade,
            description=description,
            qr_code_path=qr_path
        )
        db.session.add(cert)
        db.session.commit()

        # Generate certificate image
        generate_certificate_image(cert)

        flash(f'Certificate {cert_id} created successfully!', 'success')
        return redirect(url_for('certificate_preview', certificate_id=cert_id))

    return render_template('add_certificate.html', form_data={})


@app.route('/admin/delete/<int:cert_id>', methods=['POST'])
@login_required
def delete_certificate(cert_id):
    """Delete a certificate."""
    cert = Certificate.query.get_or_404(cert_id)
    cert_display_id = cert.certificate_id

    # Remove files
    for folder, ext in [(app.config['QR_CODE_FOLDER'], '.png'),
                        (app.config['CERT_FOLDER'], '.png')]:
        fpath = os.path.join(folder, f"{cert_display_id}{ext}")
        if os.path.exists(fpath):
            os.remove(fpath)

    db.session.delete(cert)
    db.session.commit()
    flash(f'Certificate {cert_display_id} deleted.', 'info')
    return redirect(url_for('manage_certificates'))


# ─── API Routes ─────────────────────────────────────────────────────────────────

@app.route('/api/verify/<certificate_id>')
def api_verify(certificate_id):
    """JSON API endpoint for certificate verification."""
    cert = Certificate.query.filter_by(
        certificate_id=certificate_id.upper().strip()).first()
    if cert:
        return jsonify({'valid': True, 'certificate': cert.to_dict()})
    return jsonify({'valid': False, 'message': 'Certificate not found'}), 404


# ─── Error Handlers ─────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', cert_id=''), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', cert_id='', error='Server error'), 500


# ─── Init ───────────────────────────────────────────────────────────────────────

def init_db():
    """Initialize database and create default admin."""
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin = Admin(username=admin_user)
            admin.set_password(admin_pass)
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Default admin created: {admin_user}")

if __name__ == '__main__':
    init_db()
    print("🚀 Smart Certificate Verification System")
    print("   Running at http://127.0.0.1:5000")
    print("   Admin: http://127.0.0.1:5000/admin/login")
    app.run(debug=True, host='0.0.0.0', port=5000)
