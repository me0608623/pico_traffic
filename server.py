import http.server
import socketserver
import os
import socket

PORT = 8000

# 確保正確的 MIME type，雖然 .glb 應該預設是 application/octet-stream，但明確指定更保險
extensions_map = http.server.SimpleHTTPRequestHandler.extensions_map
extensions_map['.glb'] = 'model/gltf-binary'
extensions_map['.gltf'] = 'model/gltf+json'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    def log_message(self, format, *args):
        # 簡化 log 輸出，只顯示請求
        print(f"[{self.log_date_time_string()}] {args[0]}")

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    # 允許地址重用，避免 "Address already in use"
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            ip = get_ip_address()
            print("="*60)
            print(f"🚀 簡易網頁伺服器已啟動！")
            print(f"📂 根目錄: {os.getcwd()}")
            print("-" * 60)
            print(f"請在瀏覽器輸入以下網址來開啟網頁：")
            print(f"👉 http://localhost:{PORT}")
            print(f"👉 http://{ip}:{PORT} (區域網路)")
            print("-" * 60)
            print("按 Ctrl+C 可以停止伺服器")
            print("="*60)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 伺服器已停止")
