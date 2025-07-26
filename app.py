from flask import Flask, request
import os
from pymongo import MongoClient

app = Flask(__name__)

# إعداد الاتصال بقاعدة بيانات MongoDB عبر متغير بيئة
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://flask_user:Ir41jpShsCFxLBCn@cluster0.xcm0cwx.mongodb.net/iot_db?retryWrites=true&w=majority&appName=Cluster0"
)
client = MongoClient(MONGO_URI)
db = client["iot_db"]
collection = db.devices

# استقبال البيانات
@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    if not data:
        return "No data received", 400

    collection.insert_one(data)
    return "تم الحفظ", 200

# عرض البيانات
@app.route("/", methods=["GET"])
def index():
    all_data = list(collection.find({}, {"_id": 0}))

    if not all_data:
        return "<h2>لا توجد بيانات بعد.</h2>"

    headers = """
        <th>معلومات الموديل</th>
        <th>معلومات الشبكة</th>
        <th>النظام والتاريخ</th>
        <th>التطبيقات المثبتة</th>
    """

    rows = ""
    for d in all_data:
        model_info = "<br>".join([
            f"الشركة: {d.get('manufacturer', '')}",
            f"الموديل: {d.get('model', '')}",
            f"العلامة: {d.get('brand', '')}",
            f"الجهاز: {d.get('device', '')}",
            f"SDK: {d.get('sdk_int', '')}",
        ])
        network_info = "<br>".join([
            f"IP: {d.get('ip_address', '')}",
            f"WiFi SSID: {d.get('wifi_ssid', '')}",
            f"إشارة WiFi: {d.get('wifi_signal', '')}",
            f"شركة الاتصالات: {d.get('carrier', '')}",
        ])
        system_info = "<br>".join([
            f"إصدار النظام: {d.get('os_version', '')}",
            f"التاريخ: {d.get('timestamp', '')}",
        ])
        apps = d.get("installed_apps", [])
        if isinstance(apps, list):
            apps_info = "<ul style='text-align:right; padding-right:20px;'>" + "".join(f"<li>{app}</li>" for app in apps) + "</ul>"
        else:
            apps_info = str(apps)

        rows += f"""
        <tr>
            <td>{model_info}</td>
            <td>{network_info}</td>
            <td>{system_info}</td>
            <td>{apps_info}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>عرض البيانات</title>
        <style>
            body {{ background: #fafafa; font-family: Arial, Tahoma, sans-serif; }}
            .table-container {{ width: 80%; margin: 40px auto; }}
            table {{ border-collapse: collapse; width: 100%; direction: rtl; background: #fff; }}
            th, td {{ border: 1px solid #bbb; padding: 12px; text-align: center; font-size: 16px; vertical-align: top; }}
            th {{ background-color: #e9e9e9; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #f7f7f7; }}
            ul {{ margin: 0; padding: 0 0 0 20px; text-align: right; }}
        </style>
    </head>
    <body>
        <div class="table-container">
            <h2 style="text-align:center;">البيانات المستلمة</h2>
            <table>
                <thead><tr>{headers}</tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)