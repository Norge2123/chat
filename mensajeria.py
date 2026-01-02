import socket
import struct
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# --- CONFIGURACIÓN DE RED (MULTICAST) ---
# Esta dirección permite que el mensaje "salte" entre diferentes rangos de IP
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

class ChatLocal:
    def __init__(self, root):
        self.root = root
        self.root.title("Mensajería Local - Baguano/Tacajó")
        self.root.geometry("450x550")
        self.root.configure(bg="#f0f0f0")

        # --- DISEÑO DE LA VENTANA ---
        # Etiqueta de Nombre
        tk.Label(root, text="Escribe tu nombre o local:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=5)
        self.entry_nombre = tk.Entry(root, font=("Arial", 11), justify='center')
        self.entry_nombre.pack(pady=5, padx=20, fill=tk.X)
        self.entry_nombre.insert(0, "Usuario_Local")

        # Área de mensajes
        self.area_chat = scrolledtext.ScrolledText(root, state='disabled', font=("Arial", 10), bg="white")
        self.area_chat.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

        # Entrada de mensaje
        tk.Label(root, text="Escribe tu mensaje aquí:", bg="#f0f0f0").pack()
        self.entry_msg = tk.Entry(root, font=("Arial", 11))
        self.entry_msg.pack(padx=15, pady=5, fill=tk.X)
        self.entry_msg.bind("<Return>", lambda e: self.enviar())

        # Botón Enviar
        self.btn_enviar = tk.Button(root, text="ENVIAR MENSAJE", command=self.enviar, 
                                   bg="#28a745", fg="white", font=("Arial", 10, "bold"), height=2)
        self.btn_enviar.pack(pady=15, padx=15, fill=tk.X)

        # --- LÓGICA DE CONEXIÓN ---
        try:
            # Crear socket UDP para Multicast
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Enlazar al puerto
            self.sock.bind(('', MCAST_PORT))

            # Unirse al grupo Multicast para recibir mensajes de cualquier IP en la red
            mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            # Iniciar hilo para escuchar mensajes
            threading.Thread(target=self.recibir, daemon=True).start()
            
            self.mostrar_mensaje("SISTEMA: Conectado a la red local.")
        except Exception as e:
            messagebox.showerror("Error de Red", f"No se pudo iniciar la red: {e}")

    def enviar(self):
        nombre = self.entry_nombre.get().strip()
        msg = self.entry_msg.get().strip()
        
        if not nombre:
            messagebox.showwarning("Aviso", "Por favor ponte un nombre.")
            return

        if msg:
            mensaje_completo = f"{nombre}: {msg}"
            try:
                # Enviar mensaje al grupo (todos lo reciben)
                self.sock.sendto(mensaje_completo.encode('utf-8'), (MCAST_GRP, MCAST_PORT))
                self.mostrar_mensaje(f"Yo: {msg}")
                self.entry_msg.delete(0, tk.END)
            except Exception as e:
                self.mostrar_mensaje(f"!!! Error al enviar: {e}")

    def recibir(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                mensaje = data.decode('utf-8')
                
                # Solo mostrar si el mensaje NO viene de nosotros mismos
                if not mensaje.startswith(f"{self.entry_nombre.get()}:"):
                    self.mostrar_mensaje(mensaje)
            except:
                break

    def mostrar_mensaje(self, m):
        self.area_chat.configure(state='normal')
        self.area_chat.insert(tk.END, m + "\n")
        self.area_chat.configure(state='disabled')
        self.area_chat.yview(tk.END)

if __name__ == "__main__":
    ventana = tk.Tk()
    app = ChatLocal(ventana)
    ventana.mainloop()