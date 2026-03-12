import os
import cv2
import datetime
import pyqrcode
import smtplib
import time
import random
import string
import base64
from email.message import EmailMessage
from fpdf import FPDF
from resemblyzer import VoiceEncoder, preprocess_wav
import sounddevice as sd
import wavio
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
from Cryptodome.Cipher import AES

from Cryptodome.Random import get_random_bytes

# --- Firebase Setup ---
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- AES Encryption Setup ---
AES_KEY = b'ThisIsASecretKey'

def pad(data):
    pad_len = 16 - len(data) % 16
    return data + chr(pad_len) * pad_len

def unpad(data):
    return data[:-ord(data[-1])]

def encrypt_aes(data, key=AES_KEY):
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data)
    encrypted = cipher.encrypt(padded_data.encode())
    return base64.b64encode(iv + encrypted).decode()

def decrypt_aes(encrypted_data, key=AES_KEY):
    raw = base64.b64decode(encrypted_data)
    iv = raw[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(raw[16:])
    return unpad(decrypted.decode())

# --- Paths ---
os.makedirs("voice_samples", exist_ok=True)
os.makedirs("qr_codes", exist_ok=True)
os.makedirs("captured", exist_ok=True)

# --- Email Settings ---
EMAIL_ADDRESS = "sunriseseditsoffical249@gmail.com"
EMAIL_PASSWORD = "lucymqnpdsvfdmyy"

def send_email(receiver, subject, body, attachment_path=None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver
    msg.set_content(body)
    if attachment_path:
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=os.path.basename(attachment_path))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def generate_qr(content, filename):
    encrypted_content = encrypt_aes(content)
    qr = pyqrcode.create(encrypted_content)
    qr_path = f"qr_codes/{filename}.png"
    qr.png(qr_path, scale=6)
    return qr_path

def record_voice(filename, duration=5):
    fs = 16000
    print("🔴 Recording Reference Voice...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    wavio.write(filename, recording, fs, sampwidth=2)
    print("✅ Voice Recorded")

def get_voice_embedding(filepath):
    wav = preprocess_wav(filepath)
    encoder = VoiceEncoder()
    embed = encoder.embed_utterance(wav)
    return embed

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def capture_intruder():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    filename = f"captured/intruder_{int(time.time())}.jpg"
    if ret:
        cv2.imwrite(filename, frame)
        print("📸 Intruder Captured")
    cap.release()
    return filename

def register_member():
    print("👤 Name:")
    name = input()
    print("📧 Email:")
    email = input()
    print("📱 Phone:")
    phone = input()
    print("👪 Relation:")
    relation = input()
    qr_path = generate_qr(email, email.split("@")[0])
    voice_path = f"voice_samples/{email.split('@')[0]}.wav"
    record_voice(voice_path)
    embed = get_voice_embedding(voice_path).tolist()
    db.collection("family").document(email).set({
        "name": name,
        "email": email,
        "phone": phone,
        "relation": relation,
        "voice_embed": embed,
        "qr": qr_path,
        "timestamp": datetime.datetime.now().isoformat()
    })
    send_email(email, "🔐 Your SmartLock QR", f"Hello {name},\n\nAttached is your Smart Lock QR code.", qr_path)
    print("📩 QR Sent to Email")

def scan_qr():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    print("📷 Point the camera to a QR code...")
    scanned_data = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read from camera.")
            break
        data, bbox, _ = detector.detectAndDecode(frame)
        if data:
            try:
                scanned_data = decrypt_aes(data)
                print(f"✅ QR Code Decrypted: {scanned_data}")
                break
            except:
                print("❌ Invalid or Unencrypted QR Code.")
                break
    cv2.destroyAllWindows()
    return scanned_data

def access_door():
    email = input("📧 Enter Registered Email: ").strip()
    doc = db.collection("family").document(email).get()
    if not doc.exists:
        print("❌ Email not registered.")
        return
    data = doc.to_dict()
    otp = generate_otp()
    send_email(email, "🔐 OTP Verification", f"Your OTP is: {otp}")
    print("📨 OTP sent to your email.")
    entered_otp = input("🔢 Enter OTP: ").strip()
    if entered_otp != otp:
        print("❌ Invalid OTP.")
        capture_intruder()
        db.collection("access_logs").add({
            "email": email,
            "time": datetime.datetime.now().isoformat(),
            "otp_verified": False,
            "voice_verified": False,
            "qr_verified": False,
            "access": "Denied"
        })
        return
    scanned_qr = scan_qr()
    if scanned_qr != email:
        print("❌ QR does not match registered email.")
        capture_intruder()
        db.collection("access_logs").add({
            "email": email,
            "time": datetime.datetime.now().isoformat(),
            "otp_verified": True,
            "qr_verified": False,
            "voice_verified": False,
            "access": "Denied"
        })
        return
    print("🎤 Speak for 5 seconds:")
    voice_file = "temp.wav"
    record_voice(voice_file)
    test_embed = get_voice_embedding(voice_file)
    ref_embed = np.array(data["voice_embed"])
    similarity = cosine_similarity(ref_embed, test_embed)
    print(f"🧠 Cosine Similarity: {similarity:.2f}")
    if similarity >= 0.75:
        print("✅ Access Granted!")
        db.collection("access_logs").add({
            "email": email,
            "time": datetime.datetime.now().isoformat(),
            "otp_verified": True,
            "qr_verified": True,
            "voice_verified": True,
            "access": "Granted"
        })
    else:
        print("❌ Voice Mismatch. Access Denied.")
        img_path = capture_intruder()
        print("🚨 Sending intrusion alert to all registered members...")
        members = db.collection("family").stream()
        for member in members:
            info = member.to_dict()
            send_email(
                info["email"],
                "🚨 Intruder Alert - Smart Lock System",
                f"""
Hi {info['name']},

An unauthorized attempt was made to access the smart lock system using your registered email ({email}).
The voice did not match, and access was denied.

Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please review your access logs and stay alert.

Smart Lock System
""",
                attachment_path=img_path
            )
        print("✅ Alert emails sent.")
        db.collection("access_logs").add({
            "email": email,
            "time": datetime.datetime.now().isoformat(),
            "otp_verified": True,
            "qr_verified": True,
            "voice_verified": False,
            "access": "Denied"
        })

def export_family_list_pdf():
    members = db.collection("family").stream()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Registered Family Members", ln=True, align='C')
    pdf.ln(4)
    for member in members:
        data = member.to_dict()
        name = data.get("name", "")
        email = data.get("email", "")
        phone = data.get("phone", "")
        relation = data.get("relation", "")
        qr = data.get("qr", "")
        timestamp = data.get("timestamp", "").replace("T", " ")[:19]
        pdf.set_font("Arial", '', 6.5)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 1, "", ln=True)
        pdf.cell(0, 27, "", ln=True, fill=True)
        pdf.set_y(pdf.get_y() - 26)
        x = pdf.get_x() + 2
        y = pdf.get_y()
        pdf.set_xy(x, y)
        pdf.multi_cell(0, 4, f"Name: {name}\nEmail: {email}\nPhone: {phone}\nRelation: {relation}\nQR Path: {qr}\nRegistered: {timestamp}", align='L')
        pdf.ln(1)
    filename = "registered_family_members_blocks.pdf"
    pdf.output(filename)
    print(f"✅ Exported: {filename}")

def export_access_logs_pdf():
    logs = db.collection("access_logs").stream()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Access Logs - Smart Lock System", ln=True, align='C')
    pdf.ln(5)
    headers = ["Email", "QR", "OTP", "Voice", "Access", "Time"]
    widths = [55, 15, 15, 20, 20, 60]
    pdf.set_font("Arial", 'B', 9)
    for i in range(len(headers)):
        pdf.cell(widths[i], 8, headers[i], 1, 0, 'C', True)
    pdf.ln()
    pdf.set_font("Arial", '', 8)
    for log in logs:
        data = log.to_dict()
        row = [
            data.get("email", "")[:50],
            "YES" if data.get("qr_verified") else "NO",
            "YES" if data.get("otp_verified") else "NO",
            "YES" if data.get("voice_verified") else "NO",
            data.get("access", "Denied"),
            data.get("time", "")[:50],
        ]
        for i in range(len(row)):
            pdf.cell(widths[i], 8, str(row[i]), 1)
        pdf.ln()
    filename = "access_logs.pdf"
    pdf.output(filename)
    print(f"✅ PDF Exported: {filename}")

# --- Main Menu ---
while True:
    print("\n--- Smart Lock Menu ---")
    print("1. Register Family Member")
    print("2. Access Door")
    print("3. Export Registered List PDF")
    print("4. Export Access Session Logs PDF")
    print("5. Exit")
    choice = input("Choose Option: ")
    if choice == '1':
        register_member()
    elif choice == '2':
        access_door()
    elif choice == '3':
        export_family_list_pdf()
    elif choice == '4':
        export_access_logs_pdf()
    elif choice == '5':
        break
    else:
        print("❌ Invalid Choice")
