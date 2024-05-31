import socket
import threading
import os

# Рабочая директория сервера
WEB_ROOT = './web_root'

# HTTP-заголовок ответа
HTTP_HEADER = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'

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
        print("Connected", addr)
        data = conn.recv(8192)
        msg = data.decode()
        print(msg)

        # Разбор строки запроса
        request_line = msg.splitlines()[0]
        request_method, path, _ = request_line.split()

        if path == '/':
            path = '/index.html'

        file_path = os.path.join(WEB_ROOT, path[1:])

        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                response_body = f.read()
        else:
            response_body = '<H1>404 Not Found</H1>'

        response = HTTP_HEADER + response_body
        conn.send(response.encode())
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()

def start_server():
    sock = socket.socket()
    try:
        sock.bind(('', 80))
    except OSError:
        sock.bind(('', 8080))
    sock.listen(5)
    print("Server started on port 80")

    while True:
        conn, addr = sock.accept()
        client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()

# http://localhost:80/1.html
# http://localhost:80/2.html
# http://localhost:80