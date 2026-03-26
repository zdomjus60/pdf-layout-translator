import fitz
import os
import re
from deep_translator import GoogleTranslator
from tqdm import tqdm

class PDFTranslator:
    def __init__(self, input_pdf, target_lang='it'):
        self.input_pdf = input_pdf
        self.target_lang = target_lang
        self.translator = GoogleTranslator(source='auto', target=target_lang)
        self.doc = fitz.open(input_pdf)

    def is_gibberish(self, text):
        if not text or not text.strip():
            return False
        alphanumeric = len(re.findall(r'[a-zA-Z0-9]', text))
        total = len(text.strip())
        if total == 0: return False
        return (alphanumeric / total) < 0.3

    def translate_text(self, text):
        if not text or not text.strip() or text.strip().isdigit() or len(text.strip()) < 2:
            return text
        try:
            clean_text = " ".join(text.split())
            result = self.translator.translate(clean_text)
            return result if result else text
        except Exception:
            return text

    def get_best_font_path(self, original_font_name):
        base_path = "/usr/share/fonts/truetype/msttcorefonts/"
        if not os.path.exists(base_path):
            return None
            
        fn = original_font_name.lower()
        is_bold = "bold" in fn or "black" in fn
        is_italic = "italic" in fn or "oblique" in fn
        
        if "times" in fn or "serif" in fn or "georgia" in fn:
            if is_bold and is_italic: font_file = "timesbi.ttf"
            elif is_bold: font_file = "timesbd.ttf"
            elif is_italic: font_file = "timesi.ttf"
            else: font_file = "times.ttf"
        elif "courier" in fn or "mono" in fn or "consolas" in fn:
            if is_bold and is_italic: font_file = "courbi.ttf"
            elif is_bold: font_file = "courbd.ttf"
            elif is_italic: font_file = "couri.ttf"
            else: font_file = "cour.ttf"
        else: # Arial / Sans-serif
            if is_bold and is_italic: font_file = "arialbi.ttf"
            elif is_bold: font_file = "arialbd.ttf"
            elif is_italic: font_file = "ariali.ttf"
            else: font_file = "arial.ttf"
            
        full_path = os.path.join(base_path, font_file)
        return full_path if os.path.exists(full_path) else None

    def get_text_width(self, text, size, font_path=None):
        """Calcola la larghezza del testo per determinare lo scaling."""
        try:
            if font_path:
                # Crea un oggetto font temporaneo per la misurazione
                font = fitz.Font(fontfile=font_path)
                return font.text_length(text, fontsize=size)
            else:
                return fitz.get_text_length(text, fontname="helv", fontsize=size)
        except:
            return len(text) * size * 0.5 # Fallback grossolano

    def process(self, output_pdf):
        new_doc = fitz.open()

        for page_num in tqdm(range(len(self.doc)), desc="Translating pages"):
            page = self.doc[page_num]
            temp_doc = fitz.open()
            temp_page = temp_doc.new_page(width=page.rect.width, height=page.rect.height)
            temp_page.show_pdf_page(temp_page.rect, self.doc, page_num)
            
            dict_text = page.get_text("dict")

            for block in dict_text["blocks"]:
                if block["type"] == 0:
                    for line in block["lines"]:
                        line_text = "".join([span["text"] for span in line["spans"]])
                        if not line_text.strip():
                            continue
                            
                        translated_line = self.translate_text(line_text)
                        
                        first_span = line["spans"][0]
                        font_size = first_span["size"]
                        original_font = first_span["font"]
                        color_int = first_span["color"]
                        origin = list(first_span["origin"]) # [x, y]
                        line_bbox = line["bbox"] # [x0, y0, x1, y1]
                        
                        # Colore
                        r = ((color_int >> 16) & 0xFF) / 255.0
                        g = ((color_int >> 8) & 0xFF) / 255.0
                        b = (color_int & 0xFF) / 255.0
                        rgb_color = (r, g, b)
                        
                        # 1. Copri testo originale
                        temp_page.draw_rect(line_bbox, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
                        
                        # 2. Gestione Font e Scaling
                        font_path = self.get_best_font_path(original_font)
                        max_width = line_bbox[2] - line_bbox[0]
                        current_font_size = font_size
                        
                        # Riduci font finché non entra nel box
                        while self.get_text_width(translated_line, current_font_size, font_path) > max_width and current_font_size > 4:
                            current_font_size -= 0.3
                        
                        # 3. Inserimento testo
                        try:
                            if font_path:
                                font_tag = os.path.basename(font_path).split('.')[0]
                                temp_page.insert_text(
                                    origin, 
                                    translated_line, 
                                    fontsize=current_font_size, 
                                    color=rgb_color,
                                    fontname=font_tag,
                                    fontfile=font_path
                                )
                            else:
                                temp_page.insert_text(
                                    origin, 
                                    translated_line, 
                                    fontsize=current_font_size, 
                                    color=rgb_color,
                                    fontname="helv"
                                )
                        except Exception as e:
                            print(f"\n[!] Errore riga: {e}")

            new_doc.insert_pdf(temp_doc)
            temp_doc.close()

        new_doc.save(output_pdf)
        new_doc.close()
        print(f"\n[+] Successo! PDF salvato in: {output_pdf}")

if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) < 2:
        print("Utilizzo: python translator.py <nome_file.pdf> [<lingua_target>]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    target_lang = sys.argv[2] if len(sys.argv) > 2 else 'it'
    output_file = input_file.replace(".pdf", f"_{target_lang}.pdf")
    
    if not os.path.exists(input_file):
        print(f"Errore: Il file '{input_file}' non esiste.")
        sys.exit(1)
        
    translator = PDFTranslator(input_file, target_lang=target_lang)
    translator.process(output_file)
