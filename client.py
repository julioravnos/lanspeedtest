import socket
import time
import threading
import customtkinter as ctk

class ClientApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Network Test Client")
        self.geometry("450x550")

        ctk.CTkLabel(self, text="Teste sua Conexão Interna", font=("Roboto", 24)).pack(pady=20)

        # Input IP
        self.ip_entry = ctk.CTkEntry(self, placeholder_text="IP do Servidor (ex: 192.168.1.5)")
        self.ip_entry.pack(pady=10, padx=20, fill="x")

        self.run_button = ctk.CTkButton(self, text="Iniciar Teste", command=self.start_test_thread)
        self.run_button.pack(pady=20)

        # Frame de Resultados
        self.res_frame = ctk.CTkFrame(self)
        self.res_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Correção aqui: removido o erro de chamada do frame
        self.tcp_res = self.create_result_label("Vazão TCP:", "--- Mbps")
        self.lat_res = self.create_result_label("Latência (RTT):", "--- ms")
        self.jit_res = self.create_result_label("Jitter:", "--- ms")
        self.loss_res = self.create_result_label("Perda de Pacotes:", "--- %")

        self.progress = ctk.CTkProgressBar(self, mode="indeterminate")

    def create_result_label(self, text, val):
        # Cria um container para cada linha de resultado
        frame = ctk.CTkFrame(self.res_frame, fg_color="transparent")
        frame.pack(pady=8, padx=15, fill="x")
        
        title = ctk.CTkLabel(frame, text=text, font=("Roboto", 13, "bold"))
        title.pack(side="left")
        
        value = ctk.CTkLabel(frame, text=val, font=("Roboto", 13), text_color="#1f6aa5")
        value.pack(side="right")
        return value

    def start_test_thread(self):
        ip = self.ip_entry.get().strip()
        if not ip: 
            return
        
        self.run_button.configure(state="disabled")
        self.progress.pack(pady=10)
        self.progress.start()
        
        # Resetar labels
        self.tcp_res.configure(text="Testando...")
        self.lat_res.configure(text="Testando...")
        
        threading.Thread(target=self.run_logic, args=(ip,), daemon=True).start()

    def run_logic(self, server_ip, port=5005):
        try:
            # 1. Teste TCP (Vazão)
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_sock.settimeout(5)
            tcp_sock.connect((server_ip, port))
            
            payload = b'X' * 1024 * 1024 # 1MB
            start_t = time.time()
            for _ in range(30): # Envia 30MB
                tcp_sock.sendall(payload)
            dur = time.time() - start_t
            throughput = (30 * 8) / dur # Megabits por segundo
            
            self.tcp_res.configure(text=f"{throughput:.2f} Mbps")
            tcp_sock.close()

            # 2. Teste UDP (Latência e Jitter)
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.settimeout(1.0)
            latencies = []
            
            for i in range(50):
                s_t = time.perf_counter()
                udp_sock.sendto(f"ping{i}".encode(), (server_ip, port))
                try:
                    udp_sock.recvfrom(1024)
                    latencies.append((time.perf_counter() - s_t) * 1000)
                except:
                    continue
                time.sleep(0.01) # Pequena pausa entre pings
            
            if latencies:
                avg_l = sum(latencies) / len(latencies)
                jitters = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
                avg_j = sum(jitters) / len(jitters) if jitters else 0
                loss = ((50 - len(latencies)) / 50) * 100
                
                self.lat_res.configure(text=f"{avg_l:.2f} ms")
                self.jit_res.configure(text=f"{avg_j:.2f} ms")
                self.loss_res.configure(text=f"{loss:.0f}%")
            else:
                self.lat_res.configure(text="Erro UDP")
            
        except Exception as e:
            self.tcp_res.configure(text="Erro de Conexão")
            print(f"Erro: {e}")
        
        self.progress.stop()
        self.progress.pack_forget()
        self.run_button.configure(state="normal")

if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()