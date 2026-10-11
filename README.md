# 🏨 Grand Ova Hotel - Desktop Management System

A modern desktop hotel management application built with **Python**, **CustomTkinter**, and **SQLite**. Designed with a dark-theme UI, the system simplifies front-desk operations including real-time room tracking, guest check-in/check-out, instant payment logging, and end-of-day financial archiving.

---

## ✨ Features

- **Floor & Room Architecture:** Real-time occupancy tracking across 5 floors (55 rooms categorized as Single, Double, and Suite).
- **Check-in & Guest Management:** Guest registration (Name, National ID/Passport), automatic fee calculation, and payment processing (Cash, Credit Card, Bank Transfer).
- **Live Financial Dashboard:** Real-time revenue metrics and occupancy indicators.
- **End-of-Day (Gün Sonu) Archiving:** Automated cashier closing routine that archives daily transactions into SQLite history and resets the active cash register.
- **Security:** SHA-256 administrative password hashing.

---

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **GUI Framework:** CustomTkinter / Tkinter
- **Database:** SQLite3
- **Security:** Hashlib (SHA-256)

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed, then install the required GUI library:

```bash
pip install customtkinter
