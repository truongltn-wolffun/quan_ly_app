import winreg
import json
import os
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

def scan_apps():
    app_list = []
    # Các đường dẫn Registry quan trọng
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
                        name = ""
                        sub_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub_key_name) as sub_key:
                            # Lấy các trường dữ liệu
                            try: name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                            except: continue
                            
                            try: publisher = winreg.QueryValueEx(sub_key, "Publisher")[0]
                            except: publisher = "Unknown"
                            
                            try: install_loc = winreg.QueryValueEx(sub_key, "InstallLocation")[0]
                            except: install_loc = "N/A"

                            # 1. Lọc Microsoft
                            category = "Microsoft" if "Microsoft" in str(publisher) else "Third-party"
                            
                            # 2. Kiểm tra dấu hiệu License/Crack (Heuristics)
                            # - Nếu Publisher là Unknown và cài ở ổ khác C: -> Nghi vấn tải ngoài/Portable
                            # - Kiểm tra chuỗi "ReleaseType" hoặc "DisplayVersion" lạ
                            status = "Chính thống (Verified)"
                            if category == "Third-party":
                                if install_loc == "N/A" or not install_loc.startswith("C:\\Program Files"):
                                    status = "Nghi vấn (Portable/Tải ngoài)"
                                if "v3." in name and "WIN" in name: # Dấu hiệu đặt tên của các bản crack
                                    status = "Cần kiểm tra (Dấu hiệu Crack)"

                            app_list.append({
                                "name": name,
                                "publisher": publisher,
                                "category": category,
                                "location": install_loc,
                                "status": status
                            })
                    except: continue
        except: continue
    return app_list

@app.route('/')
def index():
    apps = scan_apps()
    return render_template('index.html', apps=apps)

@app.route('/export', methods=['POST'])
def export_data():
    data = scan_apps()
    # Lưu file cục bộ
    file_path = os.path.join(os.getcwd(), 'inventory_report.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return jsonify({"message": f"Đã lưu báo cáo tại: {file_path}"})

if __name__ == '__main__':
    # Chạy trên 0.0.0.0 để máy khác trong LAN (10.0.10.x) có thể truy cập
    app.run(host='0.0.0.0', port=5000, debug=True)