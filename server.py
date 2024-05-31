import socket
import threading
import os
import time
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Рабочая директория сервера
WEB_ROOT = './web_root'

# HTTP-заголовок ответа
SERVER_NAME = "SimplePythonServer/0.1"

def get_http_header(content_length, content_type="text/html"):
    date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    return f"""HTTP/1.1 200 OK
Date: {date}
Content-Type: {content_type}
Server: {SERVER_NAME}
Content-Length: {content_length}
Connection: close

"""

# Создание рабочей директории и файлов
os.makedirs(WEB_ROOT, exist_ok=True)
with open(os.path.join(WEB_ROOT, 'index.html'), 'w') as f:
    f.write('<H1>Index File</H1>')
with open(os.path.join(WEB_ROOT, '1.html'), 'w') as f:
    f.write('<H1>First file</H1>')
with open(os.path.join(WEB_ROOT, '2.html'), 'w') as f:
    f.write('<H1>Second file</H1>')

def handle_client_connection(conn, addr):
    try:
        logging.info(f"Connected to {addr}")
        data = conn.recv(8192)
        msg = data.decode()
        logging.info(f"Request: {msg}")
        
        # Разбор строки запроса
        request_line = msg.splitlines()[0]
        request_method, path, _ = request_line.split()
        
        if path == '/':
            path = '/index.html'
        
        file_path = os.path.join(WEB_ROOT, path[1:])
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                response_body = f.read()
            content_length = len(response_body)
            response_header = get_http_header(content_length)
        else:
            response_body = '<H1>404 Not Found</H1>'
            content_length = len(response_body)
            response_header = get_http_header(content_length)
        
        response = response_header + response_body
        conn.send(response.encode())
        logging.info(f"Response sent with headers:\n{response_header}")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        conn.close()

def start_server():
    sock = socket.socket()
    try:
        sock.bind(('', 80))
    except OSError:
        sock.bind(('', 8080))
    sock.listen(5)
    logging.info("Server started on port 80 or 8080")
    
    while True:
        conn, addr = sock.accept()
        client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()


# http://localhost:80/1.html
# http://localhost:80/2.html
# http://localhost:80