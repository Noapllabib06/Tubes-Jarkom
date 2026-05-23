import socket
import threading
import os
from datetime import datetime

HOST = '127.0.0.1' 
TCP_PORT = 8000
UDP_PORT = 9000

def get_timestamp():
    """Fungsi bantuan untuk mendapatkan waktu saat ini"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def handle_tcp_client(client_socket, client_address):
    """Menangani permintaan HTTP GET berbasis TCP"""
    try:
        request = client_socket.recv(1024).decode('utf-8')
        if not request:
            client_socket.close()
            return

        # Parsing HTTP Request
        headers = request.split('\n')
        if len(headers) > 0 and len(headers[0].split()) > 1:
            filename = headers[0].split()[1]
        else:
            filename = '/'
        
        # Default ke index.html jika meminta root '/'
        if filename == '/':
            filename = '/index.html'
            
        filepath = filename.lstrip('/')

        try:
            # Skenario Berhasil: 200 OK
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            response = 'HTTP/1.1 200 OK\r\n'
            response += 'Content-Type: text/html; charset=utf-8\r\n'
            response += f'Content-Length: {len(content)}\r\n'
            response += '\r\n'
            response += content
            
            client_socket.sendall(response.encode('utf-8'))
            print(f"[TCP LOG] {get_timestamp()} | IP: {client_address[0]} | 200 OK | Jalur: {filename}")
            
        except FileNotFoundError:
            # Skenario Gagal: 404 Not Found
            error_msg = "<html><body><h1>404 Not Found</h1><p>Berkas tidak ditemukan.</p></body></html>"
            response = 'HTTP/1.1 404 Not Found\r\n'
            response += 'Content-Type: text/html; charset=utf-8\r\n'
            response += f'Content-Length: {len(error_msg)}\r\n'
            response += '\r\n'
            response += error_msg
            
            client_socket.sendall(response.encode('utf-8'))
            print(f"[TCP LOG] {get_timestamp()} | IP: {client_address[0]} | 404 Not Found | Jalur: {filename}")

    except Exception as e:
        # Skenario Gagal: 500 Internal Server Error
        error_msg = "<html><body><h1>500 Internal Server Error</h1></body></html>"
        response = 'HTTP/1.1 500 Internal Server Error\r\n'
        response += 'Content-Type: text/html; charset=utf-8\r\n'
        response += f'Content-Length: {len(error_msg)}\r\n'
        response += '\r\n'
        response += error_msg
        client_socket.sendall(response.encode('utf-8'))
        
        print(f"[TCP ERROR] {get_timestamp()} | IP: {client_address[0]} | 500 Internal Server Error | Detail: {e}")
        
    finally:
        client_socket.close()

def start_tcp_server():
    """Menjalankan server TCP (HTTP)"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, TCP_PORT))
    server_socket.listen(5)
    print(f"[*] TCP HTTP Server listening on {HOST}:{TCP_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        # Menggunakan thread untuk menangani konkurensi
        client_thread = threading.Thread(target=handle_tcp_client, args=(client_socket, client_address))
        client_thread.start()

def start_udp_server():
    """Menjalankan server UDP (QoS Echo)"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    print(f"[*] UDP Echo Server listening on {HOST}:{UDP_PORT}")

    while True:
        data, client_address = udp_socket.recvfrom(1024)
        udp_socket.sendto(data, client_address)
        print(f"[UDP LOG] {get_timestamp()} | Echoed payload back to {client_address[0]}")

if __name__ == "__main__":
    tcp_thread = threading.Thread(target=start_tcp_server)
    udp_thread = threading.Thread(target=start_udp_server)
    
    tcp_thread.start()
    udp_thread.start()