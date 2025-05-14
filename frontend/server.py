from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Redirigir '/' a '/login.html'
        if self.path == '/':
            self.path = '/login.html'
        return super().do_GET()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

def run(server_class=HTTPServer, handler_class=CORSRequestHandler, port=8001):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor iniciado en http://localhost:{port}")
    print("Para acceder al sistema, abre en tu navegador:")
    print(f"  - Login: http://localhost:{port}/login.html")
    print(f"  - Registro: http://localhost:{port}/registro.html")
    httpd.serve_forever()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run() 