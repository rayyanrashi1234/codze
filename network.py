# network.py
import requests
import threading
import os

class NetworkBridge:
    def __init__(self, server_url):
        self.server_url = server_url

    def send_to_server(self, file_path, local_result, callback):
        """Sends file to server for deep AI analysis & quarantine"""
        def _task():
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f)}
                    data = {
                        'local_verdict': str(local_result['is_malicious']),
                        'device_id': 'Aegis_Mobile_01'
                    }
                    res = requests.post(f"{self.server_url}/api/upload_malware", files=files, data=data, timeout=15)
                    if res.status_code == 200:
                        callback(True, "Payload quarantined on server")
                    else:
                        callback(False, "Server rejected file")
            except Exception as e:
                callback(False, f"Network error: {str(e)[:30]}")
        
        threading.Thread(target=_task, daemon=True).start()

    def fetch_live_threats(self, callback):
        """Polls server for real-time threat feed"""
        def _task():
            try:
                res = requests.get(f"{self.server_url}/api/dashboard", timeout=5)
                if res.status_code == 200:
                    callback(res.json().get('threats', []))
            except:
                pass
        threading.Thread(target=_task, daemon=True).start()