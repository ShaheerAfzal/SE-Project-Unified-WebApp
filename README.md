# 🛠️ Unified Tools App

A centralized web application designed to consolidate multiple standalone utility tools into a single, cohesive interface. This project transforms a fragmented workflow into a unified platform featuring a shared database, consistent navigation, and an upgraded document generation system.

> [!NOTE]
> This project was developed as part of a Software Engineering course to meet specific client requirements for internal tool management.

**Key Deliverables**:

* ✅ **Centralized Dashboard**: A single app with a persistent sidebar for seamless tool switching.
* ✅ **Dynamic HLS Viewer**: Moves away from hardcoded streams to a database-backed URL management system.
* ✅ **Advanced Shipment Engine**: A robust Word-to-PDF generation system with dynamic placeholder extraction.
* ✅ **Shared Infrastructure**: Unified SQLite backend for persistence across all tools.

---

## 📖 Overview

The **Unified Tools App** serves as a Swiss Army knife for the client's technical operations. It integrates four core modules:
1. **HLS Viewer**: For monitoring live camera streams.
2. **Shipment Form**: For generating logistics documents from templates.
3. **HTV Tools**: Configuration and programming utilities for hardware.
4. **Serial Tool**: A terminal-based interface for serial communication.

---

## 🚀 Quick Start

### 1. Prerequisites
* Python 3.10+
* [LibreOffice](https://www.libreoffice.org/) (Required for PDF conversion on Linux servers).
* Microsoft Word (Optional, for local Windows PDF conversion).

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/its-aleezA/unified-tools-app.git
cd unified-tools-app

# Install dependencies
pip install -r requirements.txt

# Run migrations and start server
python manage.py migrate
python manage.py runserver
```

### 3. Usage
Access the application at `http://127.0.0.1:8000/`. Use the sidebar to navigate between tools.

---

## 🛠️ Tools Breakdown

### 📦 Shipment Form (Core Module)

The most significant upgrade in the suite. It moves beyond fixed fields to a flexible "Placeholder System".

* **Template Upload**: Users upload `.docx` files with tags like `[PRODUCT_NAME]` or `{{DATE}}`.
* **Auto-Extraction**: The system parses the file, identifies placeholders, and generates a dynamic web form.
* **Document Management**: Generated data is saved in the database, allowing documents to be re-downloaded as Word or PDF at any time without storing large binary files.

### 📹 HLS Viewer

* **Persistence**: Stream URLs are no longer hardcoded in HTML.
* **Management**: Users can add, remove, and categorize streams via the UI.

### 🔧 HTV & Serial Tools

* **HTV Config**: Manage device configurations including IMEI, APN settings, and PID mappings.
* **Serial Tool**: Integrated into the sidebar for future terminal-based improvements.

---

## 🏗️ Technical Stack

* **Backend**: Django (Python) with Django Rest Framework (DRF).
* **Frontend**: HTML5, CSS3, JavaScript (Vanilla/Tailwind CSS).
* **Database**: SQLite3 (Shared across all apps).
* **Document Processing**: `python-docx` for manipulation and `LibreOffice`/`docx2pdf` for PDF rendering.

---

## 🗂️ Project Structure

```text
├── App_backend/            # Core project settings and URL routing
├── HLS_viewer_backend/     # Stream management and camera viewer logic
├── htv_tools_backend/      # Configuration and programmer utilities
├── shipment_form_backend/  # Word/PDF generation and template engine
├── serial_backend/         # Placeholder for serial communication tools
├── templates/              # Shared UI components (sidebar, index)
└── static/                 # CSS, JS, and asset files
```

---

## 📊 Database Schema

| Table | Key Fields |
| --- | --- |
| **Streams** | <br>`name`, `url`, `is_active` |
| **Templates** | <br>`name`, `file_path`, `fields (JSON)`, `key_field` |
| **Documents** | <br>`template_id`, `field_values (JSON)`, `key_field_value` |
| **HTV Config** | `imei`, `ip_address`, `port`, `pid_mappings` |

---

## 👤 Contributors

- [Aleeza Rizwan](https://github.com/its-aleezA)
- [Ayesha Majid](https://github.com/ayeshamajid3)
- [Muhammad Ibrahim Abdullah](https://github.com/Ibrahim5570)
- [Muhammad Shaheer Afzal](https://github.com/ShaheerAfzal)
