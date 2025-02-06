from flask import Flask, render_template, request, jsonify, make_response
import ssl
import socket
import datetime
import concurrent.futures
from urllib.parse import urlparse
import json

app = Flask(__name__)

def get_ssl_info(domain):
    try:
        # Chuẩn hóa domain
        domain = domain.strip().lower()
        if domain.startswith('http://') or domain.startswith('https://'):
            domain = urlparse(domain).netloc
        
        # Tạo SSL context
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Lấy thông tin từ certificate
                not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                not_before = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                issuer = dict(x[0] for x in cert['issuer'])
                
                # Tính số ngày còn lại
                days_remaining = (not_after - datetime.datetime.now()).days
                
                return {
                    'domain': domain,
                    'status': 'valid',
                    'issuer': issuer.get('organizationName', 'N/A'),
                    'valid_from': not_before.strftime('%Y-%m-%d'),
                    'valid_to': not_after.strftime('%Y-%m-%d'),
                    'days_remaining': days_remaining,
                    'error': None
                }
                
    except Exception as e:
        return {
            'domain': domain,
            'status': 'error',
            'issuer': 'N/A',
            'valid_from': 'N/A',
            'valid_to': 'N/A',
            'days_remaining': 0,
            'error': str(e)
        }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check_ssl', methods=['POST'])
def check_ssl():
    domains = request.form.get('domains', '').split(',')
    domains = [d.strip() for d in domains if d.strip()]
    
    if not domains:
        return jsonify({'error': 'No domains provided'})
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(get_ssl_info, domains))
    
    # Lấy lịch sử hiện tại từ cookie
    history = request.cookies.get('ssl_history', '[]')
    try:
        history = json.loads(history)
    except:
        history = []
    
    # Thêm domain mới vào lịch sử (không trùng lặp)
    for domain in domains:
        if domain not in history:
            history.insert(0, domain)  # Thêm vào đầu danh sách
    
    # Giới hạn lịch sử 20 domain gần nhất
    history = history[:20]
    
    # Tạo response với kết quả và cập nhật cookie
    response = make_response(jsonify({'results': results}))
    response.set_cookie('ssl_history', json.dumps(history), max_age=30*24*60*60)  # Cookie hết hạn sau 30 ngày
    
    return response

@app.route('/get_history')
def get_history():
    history = request.cookies.get('ssl_history', '[]')
    try:
        history = json.loads(history)
    except:
        history = []
    return jsonify({'history': history})

if __name__ == '__main__':
    app.run(debug=True) 