# 💻 Developer Tech Showcase Ecosystem

![Ecosystem Status](https://img.shields.io/badge/status-active-emerald?style=flat-mono)
![Architecture](<https://img.shields.io/badge/architecture-Decoupled%20(Monorepo/Multi--repo)-blue?style=flat-mono>)

Selamat datang di **Developer Tech Showcase**, sebuah platform portofolio interaktif terenkripsi ala terminal tempat para pengembang dapat memamerkan proyek biner, mengelola repositori, dan memperbarui konfigurasi sistem profil secara _real-time_.

Proyek ini dibangun menggunakan arsitektur _decoupled_ yang memisahkan antara Core Kernel (Backend API) dan User Interface (Frontend Dashboard).

---

## 🔗 REPOSITORY_NODES (Tautan Repositori)

Untuk melihat detail kode sumber, silakan akses node repositori spesifik di bawah ini:

- **⚙️ Core Engine Backend:** [developer_tech_showcase_api](https://github.com/fajhrinazgul/developer_tech_showcase_api)
- **🎨 User Interface Frontend:** [developer_tech_showcase](https://github.com/fajhrinazgul/developer_tech_showcase)

---

## 🛠️ TECH_STACK_MATRIX

### [Backend API Node]

- **Kernel:** Django REST Framework (DRF) / Python
- **Database:** PostgreSQL
- **Authentication:** JWT (JSON Web Tokens) Bearer Secure Protocol

### [Frontend UI Node]

- **Framework:** Next.js (App Router) & TypeScript
- **Styling:** Tailwind CSS
- **Components System:** shadcn/ui
- **Notifications:** Sonner Toast

---

## 🚀 QUICK_START_UP_GUIDE

Jika Anda ingin mereplikasi ekosistem ini di mesin lokal, ikuti instruksi kompilasi berikut:

### 1. Inisialisasi Backend Engine

Akses repositori [developer_tech_showcase_api](https://github.com/fajhrinazgul/developer_tech_showcase_api), lalu jalankan perintah:

```bash
cd developer_tech_showcase_api
python -m venv venv
source venv/bin/activate  # Untuk Windows: venv\Scripts\activate

# Create DB
createdb -U your_username developer_tech_showcase

pip install -r requirements.txt
python manage.py makemigrations users projects notifications
python manage.py migrate
daphne developer_tech_showcase_api.asgi:application
```

### 2. Inisialisasi Client Engine

Akses repositori [developer_tech_showcase](https://github.com/fajhrinazgul/developer_tech_showcase), lalu jalankan perintah:

```bash
npm install
npm run build && npm run start
```
