import socket
import threading
import customtkinter as ctk

class ServerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Network Test Server")
        self.geometry("500x400")
        
        self.label = ctk.CTkLabel(self, text="Servidor de Teste de Rede", font=("Roboto", 20))
        self.label.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Status: Parado", text_color="red")
        self.status_label.pack(pady=5)

        self.log_box = ctk.CTkTextbox(self, width=400, height=200)
        self.log_box.pack(pady=10)

        self.start_button = ctk.CTkButton(self, text="Iniciar Servidor", command=self.start_threading)
        self.start_button.pack(pady=10)
        
        self.running = False

    def log(self, message):
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")

    def start_threading(self):
        if not self.running:
            self.running = True
            thread = threading.Thread(target=self.run_server, daemon=True)
            thread.start()
            self.start_button.configure(state="disabled")
            self.status_label.configure(text="Status: Rodando", text_color="green")

    def run_server(self, host='0.0.0.0', port=5005):
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.bind((host, port))
        tcp_sock.listen(5)
        
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind((host, port))
        
        self.log(f"[*] Escutando em {host}:{port}")

        while True:
            # Thread simples para não travar o loop de UDP
            conn, addr = tcp_sock.accept()
            self.log(f"[TCP] Conexão de {addr}")
            
            # Limpa o buffer do TCP
            while True:
                data = conn.recv(4096)
                if not data: break
            conn.close()
            
            # Atende UDP (ECHO)
            for _ in range(100):
                data, addr = udp_sock.recvfrom(1024)
                udp_sock.sendto(data, addr)
            self.log(f"[UDP] Teste de latência concluído com {addr}")

if __name__ == "__main__":
    app = ServerApp()
    app.mainloop()