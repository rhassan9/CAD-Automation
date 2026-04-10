import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from PIL import Image
import os

class AppUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Lumos Data Extraction Engine")
        self.geometry("800x600")
        
        # App Icon Integration
        try:
            self.iconbitmap(os.path.abspath("Materials/App Icon.ico"))
        except Exception:
            pass

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # App Background Integration
        try:
            bg_image = Image.open("Materials/Background.png")
            self.bg_image_ctk = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(800, 600))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image_ctk, text="")
            self.bg_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"Could not load background: {e}")

        # Main Central Card Panel (Glassmorphism inspired)
        self.main_frame = ctk.CTkFrame(self, width=600, height=480, corner_radius=20, fg_color=("#EBEBEB", "#1C1C1E"))
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # App Header Logo Integration
        try:
            logo_image = Image.open("Materials/App Logo.png")
            aspect_ratio = logo_image.width / logo_image.height
            new_height = 80
            new_width = int(new_height * aspect_ratio)
            self.logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(new_width, new_height))
            self.logo_label = ctk.CTkLabel(self.main_frame, image=self.logo_ctk, text="")
            self.logo_label.pack(pady=(30, 20))
        except Exception as e:
            print(f"Could not load logo: {e}")
            self.title_label = ctk.CTkLabel(self.main_frame, text="LUMOS AUTOMATION ENGINE", font=ctk.CTkFont(size=24, weight="bold"))
            self.title_label.pack(pady=(30, 20))

        # Variables
        self.dxf_path = ctk.StringVar()
        self.template_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        
        # Dynamic Fields
        self.create_input_row("1. Target Extractor Source (DXF File):", self.dxf_path, self.browse_dxf)
        self.create_input_row("2. Master Company Blueprint (Excel Template):", self.template_path, self.browse_template)
        self.create_input_row("3. Destination Output (Save As):", self.output_path, self.browse_output)
        
        # Action Area
        self.run_btn = ctk.CTkButton(self.main_frame, text="GENERATE EXCEL WORKBOOK", 
                                     font=ctk.CTkFont(size=14, weight="bold"), 
                                     height=50, fg_color="#0066CC", hover_color="#0052A3",
                                     command=self.start_process)
        self.run_btn.pack(pady=(20, 10), padx=40, fill="x")

        # Feedback Area
        self.status_var = ctk.StringVar(value="Status: Ready")
        self.status_lbl = ctk.CTkLabel(self.main_frame, textvariable=self.status_var, font=ctk.CTkFont(size=12, slant="italic"))
        self.status_lbl.pack(pady=(0, 20))

    def create_input_row(self, label_text, string_var, browse_cmd):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.pack(fill="x", padx=40, pady=10)
        
        lbl = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=13, weight="bold"))
        lbl.pack(anchor="w")
        
        entry_frame = ctk.CTkFrame(frame, fg_color="transparent")
        entry_frame.pack(fill="x", pady=(2, 0))
        
        entry = ctk.CTkEntry(entry_frame, textvariable=string_var, placeholder_text="Required...", height=35)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn = ctk.CTkButton(entry_frame, text="Browse", width=80, height=35, command=browse_cmd)
        btn.pack(side="right")

    def browse_dxf(self):
        filename = filedialog.askopenfilename(title="Select DXF File", filetypes=[("DXF Files", "*.dxf")])
        if filename: self.dxf_path.set(filename)

    def browse_template(self):
        filename = filedialog.askopenfilename(title="Select Excel Template", filetypes=[("Excel Files", "*.xlsx")])
        if filename: self.template_path.set(filename)

    def browse_output(self):
        filename = filedialog.asksaveasfilename(title="Save Output As", defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if filename: self.output_path.set(filename)

    def start_process(self):
        if not self.dxf_path.get() or not self.template_path.get() or not self.output_path.get():
            messagebox.showwarning("Missing inputs", "Please accurately select all three target files before executing!")
            return
            
        self.status_var.set("Status: Mapping DXF Topology to Excel Frame... Please Wait")
        self.run_btn.configure(state="disabled")
        threading.Thread(target=self.execute_logic, daemon=True).start()
        
    def execute_logic(self):
        try:
            from pipeline import parse_dxf_data
            from excel_writer import ExcelWriter
            
            # 1. Boot up pipeline mathematical generation
            data = parse_dxf_data(self.dxf_path.get())
            
            # 2. Boot up Excel engine with rigid Master Prompt targets
            writer = ExcelWriter(self.output_path.get(), self.template_path.get())
            writer.populate_house_count(data['house_count'])
            writer.populate_splices(data['splitters_1x8'])
            writer.populate_1x4_splits(data['splitters_1x8'])
            writer.populate_cable_sheet(data.get('cable_spans', {}))
            writer.save()
            
            self.after(0, lambda: self.status_var.set("Status: Success!"))
            self.after(0, lambda: messagebox.showinfo("Success", f"Topology mapped securely. Final output generated at:\n{self.output_path.get()}"))
        except Exception as e:
            self.after(0, lambda: self.status_var.set("Status: System Exception Encountered!"))
            self.after(0, lambda: messagebox.showerror("Execution Fault", f"An internal exception occurred during mapping:\n{str(e)}"))
        finally:
            self.after(0, lambda: self.run_btn.configure(state="normal"))

if __name__ == "__main__":
    app = AppUI()
    app.mainloop()
