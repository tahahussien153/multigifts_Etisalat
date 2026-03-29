import base64
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

@app.route('/activate-all-gifts', methods=['POST'])
def activate_gifts():
    email = request.form.get('phone') # الإيميل من الـ HTML
    password = request.form.get('password')

    if not email or not password:
        return jsonify({"status": "error", "message": "❌ برجاء إدخال البيانات كاملة"})

    auth_str = f"{email}:{password}"
    token = base64.b64encode(auth_str.encode()).decode()

    headers = {
        'Host': "mab.etisalat.com.eg:11003",
        'User-Agent': "okhttp/5.0.0-alpha.11",
        'Accept': "text/xml",
        'Content-Type': "text/xml; charset=UTF-8",
        'applicationVersion': "2",
        'applicationName': "MAB",
        'Authorization': f"Basic {token}",
        'Language': "ar",
        'APP-BuildNumber': "10650",
        'APP-Version': "33.1.0",
        'OS-Type': "Android",
        'OS-Version': "13",
        'APP-STORE': "GOOGLE",
        'Is-Corporate': "false"
    }

    # 1. تسجيل الدخول لسحب الرقم
    login_url = "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan"
    login_xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
    <loginRequest>
        <deviceId></deviceId><firstLoginAttempt>false</firstLoginAttempt>
        <platform>Android</platform><udid></udid>
    </loginRequest>"""

    try:
        r_login = requests.post(login_url, data=login_xml, headers=headers, timeout=15)
        root = ET.fromstring(r_login.text)
        number = root.find("dial").text
        
        # قائمة الهدايا (الأكواد اللي بعتها)
        gifts = [
            {"name": "500 ميجا", "id": "23283", "prod": "DYNAMIC_OFFERING_PAY_AND_GET_POOL_BONUS"},
            {"name": "100 ميجا", "id": "24036", "prod": "DYNAMIC_OFFERING_PAY_AND_GET_MI"},
            {"name": "50 ميجا", "id": "23283", "prod": "DYNAMIC_OFFERING_PAY_AND_GET_POOL_BONUS"}
        ]

        success_count = 0
        url_order = "https://mab.etisalat.com.eg:11003/Saytar/rest/zero11/submitOrder"

        for gift in gifts:
            payload = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
            <submitOrderRequest>
                <mabOperation></mabOperation>
                <msisdn>{number}</msisdn>
                <operation>ACTIVATE</operation>
                <parameters>
                    <parameter>
                        <name>GIFT_FULLFILMENT_PARAMETERS</name>
                        <value>Offer_ID:{gift['id']};isRTIM:Y</value>
                    </parameter>
                </parameters>
                <productName>{gift['prod']}</productName>
            </submitOrderRequest>"""
            
            res = requests.post(url_order, data=payload, headers=headers, timeout=10)
            if "true" in res.text.lower():
                success_count += 1
            time.sleep(1) # حماية من الحظر

        if success_count > 0:
            return jsonify({"status": "success", "message": f"✅ تم تفعيل {success_count} هدايا بنجاح!"})
        else:
            return jsonify({"status": "error", "message": "⚠️ العروض غير متاحة حالياً لخطك"})

    except:
        return jsonify({"status": "error", "message": "❌ خطأ في الحساب أو الاتصال"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)