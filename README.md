# 🛡️ TROJANZZ - Remote Access Trojan (RAT)

```
████████╗██████╗░░█████╗░░░░░░██╗░█████╗░███╗░░██╗███████╗███████╗
╚══██╔══╝██╔══██╗██╔══██╗░░░░░██║██╔══██╗████╗░██║╚════██║╚════██║
░░░██║░░░██████╔╝██║░░██║░░░░░██║███████║██╔██╗██║░░███╔═╝░░███╔═╝
░░░██║░░░██╔══██╗██║░░██║██╗░░██║██╔══██║██║╚████║██╔══╝░░██╔══╝░░
░░░██║░░░██║░░██║╚█████╔╝╚█████╔╝██║░░██║██║░╚███║███████╗███████╗
░░░╚═╝░░░╚═╝░░╚═╝░╚════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚══╝╚══════╝╚══════╝
```

**TROJANZZ** is a custom-made FUD (Fully Undetectable) Remote Access Trojan (RAT) that allows attackers to perform various remote actions on a compromised system.

This tool was developed for educational and cybersecurity research purposes only.
Unauthorized use is illegal and strictly discouraged.

---

## ✨ Features

This RAT supports the following remote commands:

| Command               | Description                                 |
| --------------------- | ------------------------------------------- |
| `upload <filename>`   | Upload a file to the target system          |
| `download <filename>` | Download a file from the target system      |
| `screen_share`        | Stream the target's screen in real-time     |
| `screen_shot`         | Capture a screenshot from the target device |
| `start_cam`           | Activate the target's webcam                |
| `start_logger`        | Start the keylogger                         |
| `baca_data`           | Retrieve data from the keylogger            |
| `stop_logger`         | Stop the keylogger                          |

---

## ⚙️ How to Use

### 🔹 On the Target System

1. **Modify `client.py`:**
   Open the script and replace the IP address with your attacker's IP (the one running `hacker.py`).

2. **Execution Options:**

   * Run `client.py` directly using Python
     **OR**
   * Convert `client.py` into a `.exe` file using tools like `pyinstaller` or `auto-py-to-exe` for stealth deployment:

     ```
     pyinstaller --onefile --noconsole client.py
     ```

3. **Run the Script:**
   Execute the compiled `.exe` or `client.py` on the victim/target machine.

### 🔹 On the Attacker Side

1. Ensure `hacker.py` is listening for incoming connections:

   ```bash
   python3 hacker.py
   ```

2. Once the connection is established, use the supported commands listed above to interact with the target system.

---

## 👨‍💻 Author

**Created by:** fakhruladani

---

## ⚠️ Disclaimer

This project is intended **for educational purposes only**.
Any misuse of this software is strictly prohibited.
You are responsible for complying with all applicable laws.
