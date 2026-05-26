import os
import json
import winreg
import platform # Thư viện lấy thông tin máy tính
from datetime import datetime

def get_apps():
    app_list = []
    # Danh sách các từ khóa phần mềm thường cần License (bạn có thể thêm bớt)
    license_keywords = ["Adobe", "Autodesk", "Office", "Spine", "Unity", "SQL Server", "WinRAR", "JetBrains", "Filmora"]
    
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
                            
                            # Kiểm tra xem có thuộc nhóm cần License không
                            need_license = any(kw.lower() in name.lower() for kw in license_keywords)
                            
                            app_list.append({
                                "name": name,
                                "publisher": publisher,
                                "need_license": need_license
                            })
                    except: continue
        except: continue
    return app_list

# 1. Lấy thông tin định danh máy
computer_name = platform.node() # Tên máy tính
report_file = f"reports/{computer_name}.json"

# 2. Tạo thư mục reports nếu chưa có
if not os.path.exists('reports'):
    os.makedirs('reports')

# 3. Quét và lưu dữ liệu
print(f"Đang quét máy: {computer_name}...")
data = {
    "computer_name": computer_name,
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "apps": get_apps()
}

with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# 4. Tự động đẩy lên GitHub
print("Đang gửi báo cáo về hệ thống...")
os.system(f"git add {report_file}")
os.system(f'git commit -m "Update report from {computer_name}"')
os.system("git push origin main")
print("Hoàn tất!")