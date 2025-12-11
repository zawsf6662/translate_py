import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab, ImageOps, Image
import pytesseract
from deep_translator import GoogleTranslator
import threading
import time

# =================ตั้งค่า (CONFIG)=================
# ใส่ตำแหน่งไฟล์ tesseract.exe ของคุณ
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# =================================================

class ResizableWindow(tk.Toplevel):
    """คลาสแม่แบบสำหรับหน้าต่างที่ลากได้และยืดหดได้"""
    def __init__(self, parent, title="Window", bg_color="black", alpha=0.5):
        super().__init__(parent)
        self.title(title)
        self.bg_color = bg_color
        
        # ตั้งค่าหน้าต่างไร้ขอบ
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", alpha)
        self.configure(bg=bg_color)

        # ตัวแปรสำหรับเก็บตำแหน่งเมาส์ตอนลาก
        self._drag_data = {"x": 0, "y": 0}

        # ผูก Event สำหรับลากหน้าต่าง (คลิกซ้ายค้างที่พื้นที่ว่าง)
        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)

        # สร้าง Grip (มุมขวาล่าง) สำหรับยืดหดหน้าต่าง
        # *** แก้ไขตรงนี้ครับ จาก sze_nw_se เป็น size_nw_se ***
        self.grip = tk.Label(self, bg="gray", cursor="size_nw_se")
        self.grip.place(relx=1.0, rely=1.0, x=-20, y=-20, width=20, height=20, anchor="nw")
        self.grip.bind("<Button-1>", self.start_resize)
        self.grip.bind("<B1-Motion>", self.do_resize)

    def start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def do_move(self, event):
        x = self.winfo_x() + (event.x - self._drag_data["x"])
        y = self.winfo_y() + (event.y - self._drag_data["y"])
        self.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def do_resize(self, event):
        # คำนวณขนาดใหม่
        width = self.winfo_width() + (event.x - self._drag_data["x"])
        height = self.winfo_height() + (event.y - self._drag_data["y"])
        # ป้องกันไม่ให้เล็กเกินไป
        if width > 50 and height > 50:
            self.geometry(f"{width}x{height}")


class App:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()

        # 1. หน้าต่าง Scanner (กรอบแดง)
        self.scanner = ResizableWindow(root, title="Scanner", bg_color="red", alpha=0.3)
        self.scanner.geometry("400x120+100+600")
        
        tk.Label(self.scanner, text="[พื้นที่อ่านข้อความ]\nลากฉันไปทับเกม\nดึงมุมขวาล่างเพื่อขยาย", 
                 bg="red", fg="white").pack(pady=20)

        # 2. หน้าต่าง Output (กรอบดำ)
        self.output = ResizableWindow(root, title="Output", bg_color="black", alpha=0.8)
        self.output.geometry("400x150+100+400")
        
        self.label_trans = tk.Label(self.output, text="...พร้อมทำงาน...", 
                                    font=("Sarabun", 18), fg="#00FF00", bg="black", wraplength=380)
        self.label_trans.pack(expand=True, fill="both", padx=10, pady=10)

        close_btn = tk.Button(self.output, text="X", command=self.close_app, bg="red", fg="white", font=("Arial", 8))
        close_btn.place(x=0, y=0, width=20, height=20)

        self.translator = GoogleTranslator(source='en', target='th')
        self.running = True

        self.thread = threading.Thread(target=self.loop_process)
        self.thread.daemon = True
        self.thread.start()

    def preprocess_image(self, img):
        """ฟังก์ชันแต่งรูปให้ชัดขึ้นก่อนส่งไปอ่าน"""
        # 1. ขยายภาพ 3 เท่า (เพื่อให้ Pixel ที่แตกๆ มันดูเนียนขึ้นเป็นตัวหนังสือ)
        width, height = img.size
        img = img.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
        
        # 2. เปลี่ยนเป็นขาวดำ (Grayscale)
        img = ImageOps.grayscale(img)
        
        # 3. กลับสี (Invert) : Fallout พื้นดำตัวหนังสือเขียว -> เปลี่ยนเป็น พื้นขาวตัวหนังสือดำ
        # Tesseract อ่านตัวหนังสือสีดำบนพื้นขาวได้แม่นยำที่สุด
        img = ImageOps.invert(img)
        
        # 4. เร่งความเข้ม (Threshold)
        # อะไรที่ไม่ดำสนิท ให้เป็นขาวไปเลย (ลบ Noise พื้นหลัง)
        # ตัวเลข 100 คือค่าความเข้ม (ปรับได้ 0-255) ถ้าอ่านไม่ติดลองปรับเลขนี้ดู
        img = img.point(lambda p: 255 if p > 150 else 0) 
        
        return img

    def loop_process(self):
        last_text = ""
        # config เสริมให้ Tesseract อ่านบรรทัดเดียว หรือบล็อกข้อความได้ดีขึ้น
        # --psm 6 คือ Assume a single uniform block of text.
        custom_config = r'--oem 3 --psm 6'

        while self.running:
            try:
                x = self.scanner.winfo_rootx()
                y = self.scanner.winfo_rooty()
                w = self.scanner.winfo_width()
                h = self.scanner.winfo_height()
                
                if w <= 1 or h <= 1: 
                    time.sleep(1)
                    continue

                # จับภาพ
                bbox = (x, y, x + w, y + h)
                img = ImageGrab.grab(bbox=bbox)

                # *** เรียกใช้ฟังก์ชันแต่งภาพ ***
                img = self.preprocess_image(img)

                # อ่านข้อความ (ใส่ config เพิ่ม)
                text = pytesseract.image_to_string(img, lang='eng', config=custom_config)
                
                # ทำความสะอาดข้อความ (ลบตัวประหลาดที่ชอบโผล่มาใน OCR)
                clean_text = text.strip().replace('\n', ' ').replace('|', 'I').replace('_', ' ')

                if clean_text and clean_text != last_text and len(clean_text) > 3:
                    # ปริ้นท์ดูว่าอ่านได้ว่าอะไร (เอาไว้เช็ค Error)
                    print(f"อ่านได้: {clean_text}") 
                    
                    translated = self.translator.translate(clean_text)
                    self.label_trans.config(text=translated)
                    last_text = clean_text
                
                time.sleep(0.5)
            except Exception as e:
                print(e)
                time.sleep(1)

    def close_app(self):
        self.running = False
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()