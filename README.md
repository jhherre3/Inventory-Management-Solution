# 🧰 Inventory Management Solution

A clean, responsive **Flask-based tool tracking app** for makers, engineers, workshops, and small teams.  
Easily manage tools, storage locations, tags, and images — with built-in QR code generation for fast access from mobile devices.

---

## ✨ Features

- 📋 **Add & manage tools** with custom names, tags, and locations
- 📎 **Auto-generate QR codes** to link each tool to its detail page
- 📷 **Upload & view images** for each tool — supports phone camera uploads
- 🧠 **Persistent location system** — reuse saved locations easily
- 🔍 **Searchable interface** — filter tools by name, tag, location, or serial
- 🧾 **Edit or delete entries** with a clean Bootstrap UI
- 📱 **Mobile-friendly UI** — scan a QR code to access tool data from your phone
- 🔐 **Secure LAN or VPN hosting** — or deploy to the cloud (AWS, etc.)

---

## 📁 Folder Structure
```
inventory_app/
├── static/
│   ├── qrcodes/
│   └── images/
├── templates/
│   ├── index.html
│   ├── add_tool.html
│   ├── edit_tool.html
│   └── tool_detail.html
├── inventory.db
├── app.py
├── update_db.py
├── requirements.txt
└── README.md
