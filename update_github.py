import os
import json
import winreg
from datetime import datetime

# Copy lại hàm scan_apps từ app.py vào đây
def scan_apps():
    app_list = []
    paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    for root, path in paths:
        try:
            with winreg.OpenKey(root, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub_key_name) as sub_key:
                            name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                            publisher = winreg.QueryValueEx(sub_key, "Publisher")[0] if "Publisher" in [winreg.EnumValue(sub_key, j)[0] for j in range(winreg.QueryInfoKey(sub_key)[1])] else "Unknown"
                            category = "Microsoft" if "Microsoft" in str(publisher) else "Third-party"
                            app_list.append({"name": name, "publisher": publisher, "category": category, "status": "Scanned"})
                    except: continue
        except: continue
    return app_list

# Chạy quét và đẩy lên GitHub
print("Đang quét ứng dụng...")
data = scan_apps()
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Đang đẩy dữ liệu lên GitHub...")
os.system("git add data.json index.html update_github.py")
os.system(f'git commit -m "Auto-update data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"')
os.system("git push origin main")
print("Hoàn tất!")