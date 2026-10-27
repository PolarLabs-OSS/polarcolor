"""PolarColor - local palette and screen color picker."""
import colorsys
import json
import re
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk

BG="#091623"; PANEL="#122537"; FG="#EAF6FA"; ACC="#27D6D0"; MUTED="#9BB5C2"
def normalize(v):
    v=v.strip().lstrip("#")
    if len(v)==3 and re.fullmatch("[0-9a-fA-F]{3}",v):v="".join(x*2 for x in v)
    if not re.fullmatch("[0-9a-fA-F]{6}",v):raise ValueError("Colore HEX non valido")
    return "#"+v.upper()
def rgb(v):
    c=normalize(v)
    return tuple(int(c[i:i+2],16) for i in (1,3,5))
def hsl(v):
    r,g,b=(x/255 for x in rgb(v))
    h,l,s=colorsys.rgb_to_hls(r,g,b)
    return round(h*360),round(s*100),round(l*100)
def from_rgb(r,g,b):
    if any(not isinstance(x,int) or x<0 or x>255 for x in (r,g,b)):
        raise ValueError("RGB deve essere tra 0 e 255")
    return f"#{r:02X}{g:02X}{b:02X}"

class App:
    def __init__(self,root):
        self.root=root;root.title("PolarColor | PolarLabs-OSS")
        root.geometry("910x680");root.configure(bg=BG)
        self.palette=[];self.hex=tk.StringVar(value=ACC);self.status=tk.StringVar(value="Pronto")
        box=tk.Frame(root,bg=BG,padx=24,pady=20);box.pack(fill="both",expand=True)
        tk.Label(box,text="POLAR / COLOR",fg=ACC,bg=BG,font=("Segoe UI",25,"bold")).pack(anchor="w")
        tk.Label(box,text="Color picker  •  HEX / RGB / HSL  •  Palette offline",bg=BG,fg=MUTED).pack(anchor="w",pady=(0,20))
        controls=tk.Frame(box,bg=BG);controls.pack(fill="x")
        self.preview=tk.Label(controls,bg=ACC,width=14,height=6,relief="flat")
        self.preview.pack(side="left",padx=(0,20))
        inner=tk.Frame(controls,bg=BG);inner.pack(side="left",fill="both",expand=True)
        top=tk.Frame(inner,bg=BG);top.pack(fill="x",pady=(4,10))
        tk.Label(top,text="HEX",fg=FG,bg=BG).pack(side="left",padx=(0,10))
        tk.Entry(top,textvariable=self.hex,font=("Consolas",15),bg=PANEL,fg=FG,insertbackground=FG,relief="flat",width=12).pack(side="left",ipady=7)
        self.button(top,"Applica",self.update).pack(side="left",padx=10)
        self.button(top,"Scegli colore",self.choose).pack(side="left")
        self.info=tk.Label(inner,text="",fg=FG,bg=BG,font=("Consolas",12),justify="left")
        self.info.pack(anchor="w",pady=8)
        buttons=tk.Frame(inner,bg=BG);buttons.pack(anchor="w",pady=6)
        self.button(buttons,"Copia HEX",lambda:self.copy(normalize(self.hex.get()))).pack(side="left",padx=(0,8))
        self.button(buttons,"Copia RGB",lambda:self.copy("rgb("+", ".join(map(str,rgb(self.hex.get())))+")")).pack(side="left",padx=(0,8))
        self.button(buttons,"Copia HSL",lambda:self.copy("hsl("+", ".join(map(str,hsl(self.hex.get())))+")")).pack(side="left")
        self.button(box,"Preleva colore dallo schermo",self.eyedropper).pack(anchor="w",pady=(18,8))
        tk.Label(box,text="PALETTE",bg=BG,fg=FG,font=("Segoe UI",13,"bold")).pack(anchor="w",pady=(15,8))
        row=tk.Frame(box,bg=BG);row.pack(fill="x",pady=(0,10))
        for name,func in [("+ Aggiungi",self.add),("Rimuovi selezionato",self.remove),("Esporta JSON",self.export),("Importa JSON",self.load),("Svuota",self.clear)]:
            self.button(row,name,func).pack(side="left",padx=(0,7))
        style=ttk.Style();style.theme_use("clam")
        style.configure("Treeview",background=PANEL,fieldbackground=PANEL,foreground=FG,rowheight=30)
        style.configure("Treeview.Heading",background="#1B3850",foreground=FG)
        self.tree=ttk.Treeview(box,columns=("hex","rgb","hsl"),show="headings",height=8)
        for name,label in (("hex","HEX"),("rgb","RGB"),("hsl","HSL")):
            self.tree.heading(name,text=label);self.tree.column(name,width=220)
        self.tree.pack(fill="both",expand=True)
        self.tree.bind("<<TreeviewSelect>>",self.select)
        tk.Label(box,textvariable=self.status,bg=BG,fg=MUTED).pack(anchor="w",pady=8)
        tk.Label(box,text="PolarLabs-OSS  •  Tutti i colori rimangono sul dispositivo",bg=BG,fg=MUTED,font=("Segoe UI",8)).pack(anchor="w")
        self.update()
    def button(self,p,label,fn):
        return tk.Button(p,text=label,command=fn,bg=PANEL,fg=FG,activebackground="#185969",activeforeground=FG,relief="flat",padx=12,pady=8)
    def update(self):
        try:
            v=normalize(self.hex.get())
            self.hex.set(v);self.preview.config(bg=v)
            self.info.config(text=f"RGB  {rgb(v)}\nHSL  {hsl(v)}")
            self.status.set("Colore: "+v)
        except ValueError as e:self.status.set(str(e))
    def choose(self):
        chosen=colorchooser.askcolor(color=normalize(self.hex.get()),parent=self.root)
        if chosen[1]:self.hex.set(chosen[1]);self.update()
    def copy(self,v):
        self.root.clipboard_clear();self.root.clipboard_append(v);self.status.set("Copiato: "+v)
    def add(self):
        try:v=normalize(self.hex.get())
        except ValueError:return
        if v not in self.palette:self.palette.append(v)
        self.draw()
    def remove(self):
        ids=self.tree.selection()
        if ids:
            self.palette.remove(self.tree.item(ids[0],"values")[0]);self.draw()
    def clear(self):
        self.palette=[];self.draw()
    def draw(self):
        for x in self.tree.get_children():self.tree.delete(x)
        for v in self.palette:
            self.tree.insert("","end",values=(v,str(rgb(v)),str(hsl(v))))
        self.status.set(f"{len(self.palette)} colori nella palette")
    def select(self,event=None):
        ids=self.tree.selection()
        if ids:self.hex.set(self.tree.item(ids[0],"values")[0]);self.update()
    def export(self):
        if not self.palette:return
        name=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")])
        if name:
            with open(name,"w",encoding="utf-8") as f:json.dump({"app":"PolarColor","colors":self.palette},f,indent=2)
    def load(self):
        name=filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if not name:return
        try:
            with open(name,encoding="utf-8") as f:data=json.load(f)
            colors=data["colors"]
            if not isinstance(colors,list) or len(colors)>10000:raise ValueError("Palette non valida")
            self.palette=list(dict.fromkeys(normalize(x) for x in colors))
            self.draw()
        except (ValueError,KeyError,TypeError,OSError) as e:messagebox.showerror("PolarColor",str(e))
    def eyedropper(self):
        overlay=tk.Toplevel(self.root)
        overlay.attributes("-fullscreen",True)
        overlay.attributes("-alpha",0.14)
        overlay.attributes("-topmost",True)
        overlay.configure(bg="black",cursor="crosshair")
        label=tk.Label(overlay,text="Clic per catturare il pixel sotto il cursore  |  ESC per annullare",fg="white",bg="black",font=("Segoe UI",16))
        label.pack(pady=35)
        def pick(event):
            x,y=event.x_root,event.y_root
            overlay.withdraw()
            self.root.after(220,lambda:self.capture(x,y,overlay))
        overlay.bind("<Button-1>",pick)
        overlay.bind("<Escape>",lambda e:overlay.destroy())
    def capture(self,x,y,overlay):
        try:
            from PIL import ImageGrab
            img=ImageGrab.grab(bbox=(x,y,x+1,y+1),all_screens=True)
            r,g,b=img.convert("RGB").getpixel((0,0))
            self.hex.set(from_rgb(r,g,b));self.update()
        except Exception as e:messagebox.showerror("PolarColor","Cattura schermo non disponibile: "+str(e))
        finally:overlay.destroy()

from ui_theme import apply_theme

if __name__=="__main__":
    root=tk.Tk();App(root);apply_theme(root);root.mainloop()
