import fitz
import os
import re
import argparse
from deep_translator import GoogleTranslator, LibreTranslator
from tqdm import tqdm

class PDFTranslator:
    def __init__(self, input_pdf, target_lang='it', engine='google', base_url=None, api_key=None):
        self.input_pdf = input_pdf
        self.target_lang = target_lang
        self.engine = engine.lower()
        
        if self.engine == 'libre':
            # Se non fornito, tenta un'istanza pubblica (attenzione ai limiti di rate!)
            url = base_url if base_url else "https://libretranslate.de"
            print(f"[*] Motore: LibreTranslate ({url})")
            self.translator = LibreTranslator(
                source='auto', 
                target=target_lang, 
                base_url=url,
                api_key=api_key
            )
        else:
            print(f"[*] Motore: Google Translate")
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
        if not text or not text.strip() or text.strip().isdigit() or len(text.strip()) < 3:
            return text
        try:
            clean_text = " ".join(text.split())
            result = self.translator.translate(clean_text)
            return result if result else text
        except Exception as e:
            # In caso di errore (es: rate limit di LibreTranslate), restituisce l'originale
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

    def process(self, output_pdf):
        new_doc = fitz.open()

        for page_num in tqdm(range(len(self.doc)), desc="Translating pages"):
            page = self.doc[page_num]
            temp_doc = fitz.open()
            temp_page = temp_doc.new_page(width=page.rect.width, height=page.rect.height)
            temp_page.show_pdf_page(temp_page.rect, self.doc, page_num)
            
            dict_text = page.get_text("dict")

            for block in dict_text["blocks"]:
                if block["type"] == 0:  # Blocco di testo
                    block_text_parts = []
                    for line in block["lines"]:
                        line_text = "".join([span["text"] for span in line["spans"]])
                        block_text_parts.append(line_text)
                    
                    full_block_text = " ".join(block_text_parts)
                    if not full_block_text.strip():
                        continue
                        
                    translated_block = self.translate_text(full_block_text)
                    
                    first_line = block["lines"][0]
                    first_span = first_line["spans"][0]
                    font_size = first_span["size"]
                    original_font = first_span["font"]
                    color_int = first_span["color"]
                    block_bbox = block["bbox"]
                    
                    r = ((color_int >> 16) & 0xFF) / 255.0
                    g = ((color_int >> 8) & 0xFF) / 255.0
                    b = (color_int & 0xFF) / 255.0
                    rgb_color = (r, g, b)
                    
                    temp_page.draw_rect(block_bbox, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
                    
                    font_path = self.get_best_font_path(original_font)
                    font_tag = os.path.basename(font_path).split('.')[0] if font_path else "helv"
                    
                    current_font_size = font_size
                    
                    def try_insert(size):
                        return temp_page.insert_textbox(
                            block_bbox, 
                            translated_block, 
                            fontsize=size, 
                            color=rgb_color,
                            fontname=font_tag,
                            fontfile=font_path,
                            align=fitz.TEXT_ALIGN_LEFT
                        )

                    rc = try_insert(current_font_size)
                    while rc < 0 and current_font_size > 4:
                        current_font_size -= 0.5
                        rc = try_insert(current_font_size)

            new_doc.insert_pdf(temp_doc)
            temp_doc.close()

        new_doc.save(output_pdf)
        new_doc.close()
        print(f"\n[+] Successo! PDF salvato in: {output_pdf}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traduttore PDF basato su blocchi di testo.")
    parser.add_argument("input_file", help="Il file PDF da tradurre.")
    parser.add_argument("target_lang", nargs="?", default="it", help="Lingua di destinazione (default: it).")
    parser.add_argument("--engine", choices=["google", "libre"], default="google", help="Motore di traduzione da usare (default: google).")
    parser.add_argument("--url", help="URL base per LibreTranslate (opzionale).")
    parser.add_argument("--api-key", help="API key per LibreTranslate (opzionale).")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Errore: Il file '{args.input_file}' non esiste.")
        exit(1)
        
    output_file = args.input_file.replace(".pdf", f"_{args.target_lang}.pdf")
    
    print(f"Inizio traduzione di '{args.input_file}' in '{args.target_lang}'...")
    translator = PDFTranslator(
        args.input_file, 
        target_lang=args.target_lang, 
        engine=args.engine, 
        base_url=args.url, 
        api_key=args.api_key
    )
    translator.process(output_file)
