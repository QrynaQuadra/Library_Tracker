import customtkinter as ctk

class UI:
    @staticmethod
    def kart_yap(parent, baslik, row, col, renk):
        # Senin o sevdiğin çerçeveli tasarım
        k = ctk.CTkFrame(parent, width=250, height=150, corner_radius=15, border_width=2, border_color=renk)
        k.grid(row=row, column=col, padx=20, pady=20)
        k.grid_propagate(False)
        ctk.CTkLabel(k, text=baslik, font=("Arial", 16)).pack(pady=10)
        lbl = ctk.CTkLabel(k, text="0", font=("Arial", 40, "bold"), text_color=renk)
        lbl.pack()
        return lbl

    @staticmethod
    def bildirim(parent, mesaj, tur="basari"):
        renk = "#10b981" if tur == "basari" else "#ef4444"
        f = ctk.CTkFrame(parent, fg_color=renk, corner_radius=10)
        f.place(relx=0.5, rely=0.1, anchor="center")
        ctk.CTkLabel(f, text=mesaj, text_color="white", font=("Arial", 14, "bold")).pack(padx=20, pady=10)
        parent.after(2500, f.destroy)