import socket
import threading
import os
import time
import logging
import json
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Чтение конфигурационного файла
with open('config.json', 'r') as f:
    config = json.load(f)

PORT = config['port']
WEB_ROOT = config['web_root']
MAX_REQUEST_SIZE = config['max_request_size']
SERVER_NAME = config['server_name']

# HTTP-заголовок ответа
def get_http_header(content_length, content_type="text/html"):
    date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    return f"""HTTP/1.1 200 OK
Date: {date}
Content-Type: {content_type}
Server: {SERVER_NAME}
Content-Length: {content_length}
Connection: close

"""

# Создание рабочей директории и файлов, если их нет
os.makedirs(WEB_ROOT, exist_ok=True)
if not os.path.exists(os.path.join(WEB_ROOT, 'index.html')):
    with open(os.path.join(WEB_ROOT, 'index.html'), 'w') as f:
        f.write('<H1>Index File</H1>')
if not os.path.exists(os.path.join(WEB_ROOT, '1.html')):
    with open(os.path.join(WEB_ROOT, '1.html'), 'w') as f:
        f.write('<H1>Первый файл</H1>')
if not os.path.exists(os.path.join(WEB_ROOT, '2.html')):
    with open(os.path.join(WEB_ROOT, '2.html'), 'w') as f:
        f.write('<H1>Второй файл</H1>')

def handle_client_connection(conn, addr):
    try:
        logging.info(f"Connected to {addr}")
        data = conn.recv(MAX_REQUEST_SIZE)
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
        sock.bind(('', PORT))
    except OSError:
        logging.error(f"Port {PORT} is already in use. Exiting.")
        return
    sock.listen(5)
    logging.info(f"Server started on port {PORT}")
    
    while True:
        conn, addr = sock.accept()
        client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()



# http://localhost:8080/1.html
# http://localhost:8080/2.html
# http://localhost:8080