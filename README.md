# 🎓 Smart Certificate Verification System Using QR Code

A secure, modern web application that helps institutions digitally issue and verify certificates using unique IDs and QR codes — eliminating fake certificates forever.

---

## 🚀 Features

- 🔐 **Secure Admin Login** — Password hashing, session management
- 📄 **Certificate Creation** — Rich form with auto-generated Certificate ID
- 🔲 **QR Code Generation** — Each certificate gets a unique QR code
- ✅ **Instant Verification** — Verify by Certificate ID or QR scan
- 📥 **Download Certificate** — Download as PNG image
- 🔍 **Search & Manage** — Full dashboard with search and pagination
- 📱 **Responsive Design** — Works on mobile, tablet, desktop

---

## 🛠️ Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Frontend  | HTML5, CSS3, Bootstrap 5, JS      |
| Backend   | Python Flask                      |
| Database  | SQLite (via Flask-SQLAlchemy)     |
| QR Code   | qrcode + Pillow                   |
| Auth      | Werkzeug password hashing         |

---

## 📁 Project Structure

```
SmartCertVerify/
├── app.py                  ← Main Flask application
├── requirements.txt        ← Python dependencies
├── database.db             ← SQLite database (auto-created)
├── static/
│   ├── css/style.css       ← Custom styles
│   ├── js/main.js          ← Custom scripts
│   ├── qr_codes/           ← Generated QR code images
│   └── certificates/       ← Generated certificate images
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── dashboard.html
    ├── add_certificate.html
    ├── manage_certificates.html
    ├── certificate_preview.html
    ├── verify.html
    └── error.html
```

---

## ⚙️ Installation & Setup

### Step 1 — Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- VS Code (recommended)

### Step 2 — Extract the ZIP
Extract `SmartCertVerify.zip` to a folder of your choice.

### Step 3 — Open in VS Code
```
File → Open Folder → Select the extracted SmartCertVerify folder
```

### Step 4 — Create Virtual Environment (Recommended)
Open the VS Code terminal (`Ctrl + \``) and run:
```bash
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### Step 5 — Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Flask
pip install Flask-SQLAlchemy
pip install Werkzeug
pip install qrcode
pip install Pillow
```

### Step 6 — Run the Application
```bash
python app.py
```

### Step 7 — Open in Browser
```
http://127.0.0.1:5000
```

---

## � Push to GitHub

To publish this project on GitHub:

1. Create a GitHub repository.
2. Initialize git locally and add files:
   ```bash
git init
git add .
git commit -m "Initial commit"
   ```
3. Add the GitHub remote and push:
   ```bash
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
   ```

Once your project is on GitHub, connect it to Render or another hosting provider.
### Automatic GitHub → Render Deployments

To deploy automatically on every push to `main`, add these GitHub Secrets:

- `RENDER_API_KEY` — your Render API key
- `RENDER_SERVICE_ID` — the ID of your Render web service

Then push to `main` and GitHub Actions will trigger Render deployment using `.github/workflows/render-deploy.yml`.

If you prefer, you can also use Render's built-in GitHub integration instead of this action.
---

## �🔑 Default Admin Credentials

| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `admin123` |

> ⚠️ Change the password after first login in production.

---

## 📖 How to Use

### As Admin:
1. Go to `http://127.0.0.1:5000/admin/login`
2. Login with `admin` / `admin123`
3. Click **Add New Certificate**
4. Fill in student details and click **Generate Certificate**
5. Preview, download, or share the Certificate ID

### As Verifier:
1. Go to `http://127.0.0.1:5000/verify`
2. Enter the Certificate ID (e.g. `CERT-2026-001`)
3. Click **Verify** — see instant VALID or INVALID result

### Via QR Code:
- Scan the QR code on any certificate with your phone camera
- It opens the verification page automatically

---

## � Deploying to Render

This project includes a `render.yaml` deployment manifest. To deploy on Render:

1. Push your repo to GitHub.
2. Sign in to Render and create a new **Web Service**.
3. Connect your GitHub repository.
4. Use the existing `render.yaml` configuration.

Render will use:
- build command: `pip install -r requirements.txt`
- start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

Recommended environment variables:
- `SECRET_KEY` — a secure random string
- `ADMIN_USERNAME` — default `admin`
- `ADMIN_PASSWORD` — default `admin123`

> Note: The app uses SQLite and local file storage. This works for simple deployments, but for production you should eventually migrate to a managed database and durable storage.

---

## �🗄️ Database Schema

**Table: certificates**

| Column           | Type    | Description              |
|-----------------|---------|--------------------------|
| id              | Integer | Primary key              |
| certificate_id  | String  | Unique (e.g. CERT-2026-001) |
| student_name    | String  | Full name                |
| course_name     | String  | Course title             |
| department      | String  | Department name          |
| institution_name| String  | Issuing institution      |
| issue_date      | String  | Date of issue            |
| grade           | String  | Grade/score              |
| description     | Text    | Optional notes           |
| qr_code_path    | String  | Path to QR image         |
| created_at      | DateTime| Auto timestamp           |

---

## 🌐 Routes

| Route                        | Method   | Description              |
|-----------------------------|----------|--------------------------|
| `/`                         | GET      | Home page                |
| `/verify`                   | GET/POST | Verify by ID             |
| `/verify/<id>`              | GET      | Direct verify (QR scan)  |
| `/certificate/<id>`         | GET      | Certificate preview      |
| `/download/<id>`            | GET      | Download certificate     |
| `/admin/login`              | GET/POST | Admin login              |
| `/admin/logout`             | GET      | Admin logout             |
| `/admin/dashboard`          | GET      | Admin dashboard          |
| `/admin/certificates`       | GET      | Manage certificates      |
| `/admin/add`                | GET/POST | Add certificate          |
| `/admin/delete/<id>`        | POST     | Delete certificate       |
| `/api/verify/<id>`          | GET      | JSON API verification    |

---

## 🔒 Security Features

- Passwords hashed using Werkzeug `generate_password_hash`
- Session-based authentication
- Admin routes protected with `@login_required` decorator
- Input validation on all forms
- Duplicate Certificate ID prevention

---

## 📝 License

This project is for educational and portfolio purposes.

---

## 👨‍💻 Author

Built with ❤️ using Python Flask & Bootstrap 5.
