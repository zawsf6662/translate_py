ภาษาไทย:
เครื่องมือแปลภาษาบนหน้าจอแบบเรียลไทม์ พัฒนาด้วย Python โดยใช้เทคโนโลยี OCR (Optical Character Recognition) ในการดึงข้อความจากส่วนที่เลือกบนหน้าจอและแปลภาษาผ่าน Google Translate ทันที เหมาะสำหรับใช้แปลบทสนทนาในเกม หรือข้อความบนซอฟต์แวร์ที่ไม่สามารถคัดลอกได้

English:
A real-time screen translation tool developed in Python. It utilizes OCR (Optical Character Recognition) technology to capture text from a specific screen area and instantly translates it via Google Translate. Perfect for gamers and software users who need quick on-screen translations.

✨ คุณสมบัติ (Features)
Dual-Window Interface: แยกกรอบสำหรับสแกน (Scanner) และกรอบสำหรับแสดงผลภาษาไทย (Output)

Real-time OCR: ใช้ Tesseract OCR ในการอ่านข้อความภาษาอังกฤษบนหน้าจอ

Image Pre-processing: มีระบบแต่งภาพอัตโนมัติ (Grayscale, Invert, Threshold) เพื่อเพิ่มความแม่นยำในการอ่านข้อความ

Resizable & Draggable: หน้าต่างโปร่งใส สามารถลากไปวางทับตำแหน่งใดก็ได้บนหน้าจอ และปรับขนาดได้ตามต้องการ

Multithreading: ทำงานเบื้องหลังได้ลื่นไหล ไม่ทำให้หน้าต่างโปรแกรมค้าง (แต่ยังไม่สมบูรณ์)

🛠️ เทคโนโลยีที่ใช้ (Tech Stack)
Tesseract OCR: เอนจินหลักในการจำแนกตัวอักษรจากภาพ ([GitHub](https://github.com/tesseract-ocr/tesseract))

PyTesseract: ไลบรารี Python สำหรับเชื่อมต่อกับ Tesseract

Tkinter: ใช้สร้างหน้าต่าง User Interface (UI) แบบโปร่งใส

Pillow (PIL): จัดการเรื่องการจับภาพหน้าจอ (Screen Grab) และการปรับแต่งภาพ

Deep Translator: เชื่อมต่อกับ Google Translate API เพื่อแปลภาษา

