import os
import subprocess
import threading
import time
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Basit bir mesaj saklama listesi (Yerel Sohbet için)
chat_messages = []

# Kodun çal??t??? ana klasörün tam yolunu otomatik bulur
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# HTML / JavaScript Arayüzü
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Yerel Mesh ve Bilgi Ekosistemi</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f4f4f9; color: #333; }
        header { background: #2c3e50; color: white; padding: 15px; text-align: center; border-radius: 5px; }
        .container { display: flex; gap: 20px; margin-top: 20px; }
        .card { flex: 1; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h2 { border-bottom: 2px solid #eee; padding-bottom: 10px; color: #2c3e50; }
        .chat-box { height: 300px; border: 1px solid #ddd; overflow-y: auto; padding: 10px; background: #fafafa; margin-bottom: 10px; border-radius: 4px; }
        .chat-msg { margin-bottom: 8px; padding: 5px; border-bottom: 1px dashed #eee; }
        input[type="text"] { width: 70%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { padding: 10px 15px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        button:hover { background: #2980b9; }
        iframe { width: 100%; height: 380px; border: 1px solid #ddd; border-radius: 4px; }
        .info { font-size: 0.9em; color: #666; margin-bottom: 10px; }
    </style>
</head>
<body>
    <header>
        <h1>?? Yerel Bilgi ve ?leti?im Ekosistemi</h1>
        <p>Çevrimd??? Wikipedia & Yerel A? Sohbet Portal?</p>
    </header>

    <div class="container">
        <!-- Sohbet Paneli -->
        <div class="card">
            <h2>?? Yerel Sohbet</h2>
            <div class="chat-box" id="chat-messages"></div>
            <div style="margin-bottom: 10px;">
                <input type="text" id="username" placeholder="Ad?n?z" style="width: 25%;" value="Telsizci">
            </div>
            <input type="text" id="message" placeholder="Mesaj?n?z? yaz?n..." onkeydown="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Gönder</button>
        </div>

        <!-- Kiwix Kütüphane Paneli -->
        <div class="card">
            <h2>?? Çevrimd??? Kütüphane (Kiwix)</h2>
            <p class="info">Kiwix yerel sunucu üzerinden çal??maktad?r.</p>
            <iframe id="kiwix-frame" title="Kiwix Kütüphane"></iframe>
        </div>
    </div>

    <script>
        window.addEventListener('DOMContentLoaded', () => {
            const currentHost = window.location.hostname;
            document.getElementById('kiwix-frame').src = `http://${currentHost}:8080`;
        });

        function loadMessages() {
            fetch('/get_messages')
                .then(response => response.json())
                .then(data => {
                    const chatBox = document.getElementById('chat-messages');
                    chatBox.innerHTML = '';
                    data.forEach(msg => {
                        chatBox.innerHTML += `<div class="chat-msg"><b>${msg.user}:</b> ${msg.text}</div>`;
                    });
                    chatBox.scrollTop = chatBox.scrollHeight;
                });
        }

        function sendMessage() {
            const user = document.getElementById('username').value;
            const text = document.getElementById('message').value;
            if(!text.trim()) return;

            fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user: user, text: text })
            }).then(() => {
                document.getElementById('message').value = '';
                loadMessages();
            });
        }

        setInterval(loadMessages, 2000);
        loadMessages();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_messages')
def get_messages():
    return jsonify(chat_messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    if data and 'user' in data and 'text' in data:
        chat_messages.append({'user': data['user'], 'text': data['text']})
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

def start_kiwix_server():
    """Kiwix sunucusunu arka planda otomatik ba?lat?r"""
    executable_name = "kiwix-serve.exe" if os.name == 'nt' else "kiwix-serve"
    executable_path = os.path.join(BASE_DIR, executable_name)
    zim_path = os.path.join(BASE_DIR, "kutuphane.zim")
    port = "8080"
    
    if not os.path.exists(executable_path):
        print(f"? HATA: '{executable_name}' dosyas? ?u klasörde bulunamad?:\n?? {BASE_DIR}")
        return

    if not os.path.exists(zim_path):
        print(f"? HATA: 'kutuphane.zim' dosyas? ?u klasörde bulunamad?:\n?? {BASE_DIR}")
        return

    print(f"?? Kiwix sunucusu ba?lat?l?yor ({executable_name} -> Port {port})...")
    try:
        subprocess.Popen([executable_path, "--port", port, zim_path])
    except Exception as e:
        print(f"? Sunucu ba?lat?l?rken hata olu?tu: {e}")

if __name__ == '__main__':
    server_thread = threading.Thread(target=start_kiwix_server, daemon=True)
    server_thread.start()
    
    time.sleep(1)

    print("\n============================================================")
    print("?? YEREL A? EKOS?STEM? AKT?F! ??")
    print("============================================================")
    print("Bu bilgisayardan giri? için: http://localhost:5000")
    print("A?daki di?er cihazlardan giri? için (Örnek): http://<IP_ADRESINIZ>:5000")
    print("------------------------------------------------------------\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)