import fitz
import os
import re
import argparse
import requests
from tqdm import tqdm

class PDFTranslator:
    def __init__(self, input_pdf, target_lang='it', engine='google', base_url=None):
        self.input_pdf = input_pdf
        self.target_lang = target_lang
        self.engine = engine.lower()
        self.base_url = base_url if base_url else "http://localhost:5000"
        self.doc = fitz.open(input_pdf)
        
        print(f"[*] Motore: {self.engine.capitalize()} {'Locale' if self.engine == 'libre' else ''}")

    def is_gibberish(self, text):
        if not text or not text.strip(): return True
        # Se ha almeno qualche lettera o numero, proviamo a tenerlo. 
        # Riduciamo la soglia per supportare menù con molti simboli/puntini.
        alphanumeric = len(re.findall(r'[a-zA-Z0-9]', text))
        if len(text.strip()) == 0: return True
        return (alphanumeric / len(text.strip())) < 0.2

    def translate_text(self, text):
        if not text or self.is_gibberish(text) or text.strip().isdigit() or len(text.strip()) < 2:
            return text
            
        # Puliamo gli spazi orizzontali ma preserviamo i newline
        lines = text.split('\n')
        clean_lines = [" ".join(l.split()).strip() for l in lines]
        clean_text = "\n".join(clean_lines).strip()
        
        if not clean_text: return text

        try:
            if self.engine == 'libre':
                response = requests.post(
                    f"{self.base_url}/translate",
                    json={"q": clean_text, "source": "en", "target": self.target_lang, "format": "text"},
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json().get("translatedText", text)
                return text
            else:
                from deep_translator import GoogleTranslator
                # GoogleTranslator gestisce bene i newline (\n) preservandoli nella risposta
                return GoogleTranslator(source='auto', target=self.target_lang).translate(clean_text)
        except:
            return text

    def get_best_font_path(self, original_font_name):
        base_path = "/usr/share/fonts/truetype/msttcorefonts/"
        if not os.path.exists(base_path): return None
        fn = original_font_name.lower()
        is_bold = "bold" in fn or "black" in fn
        is_italic = "italic" in fn or "oblique" in fn
        if "times" in fn or "serif" in fn:
            f = "timesbi.ttf" if is_bold and is_italic else "timesbd.ttf" if is_bold else "timesi.ttf" if is_italic else "times.ttf"
        elif "courier" in fn or "mono" in fn:
            f = "courbi.ttf" if is_bold and is_italic else "courbd.ttf" if is_bold else "couri.ttf" if is_italic else "cour.ttf"
        else:
            f = "arialbi.ttf" if is_bold and is_italic else "arialbd.ttf" if is_bold else "ariali.ttf" if is_italic else "arial.ttf"
        p = os.path.join(base_path, f)
        return p if os.path.exists(p) else None

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
                    # Estraiamo e uniamo le righe in modo intelligente
                    lines = []
                    for line in block["lines"]:
                        line_text = "".join([span["text"] for span in line["spans"]]).strip()
                        if line_text: lines.append(line_text)
                    
                    if not lines: continue
                    
                    # Smart Join: decidiamo se usare spazio o \n
                    raw_text = ""
                    for i in range(len(lines)):
                        raw_text += lines[i]
                        if i < len(lines) - 1:
                            # Caso parola spezzata dal trattino
                            if lines[i].endswith("-"):
                                raw_text = raw_text[:-1]
                            # Caso continuazione frase (prossima riga inizia minuscola)
                            elif lines[i+1] and lines[i+1][0].islower():
                                raw_text += " "
                            # Caso lista o titolo (prossima riga inizia maiuscola o numero)
                            else:
                                raw_text += "\n"
                        
                    if self.is_gibberish(raw_text): continue
                        
                    translated_text = self.translate_text(raw_text)
                    if translated_text == raw_text: continue # Salta se non tradotto
                    
                    # Proprietà dal primo span e allineamento del blocco
                    span = block["lines"][0]["spans"][0]
                    font_size, original_font, color_int, bbox = span["size"], span["font"], span["color"], block["bbox"]
                    block_align = block.get("align", 0) # 0=S, 1=C, 2=D, 3=G
                    
                    # Copertura (Rettangolo bianco)
                    temp_page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
                    
                    # Font e Colore
                    font_path = self.get_best_font_path(original_font)
                    font_tag = os.path.basename(font_path).split('.')[0] if font_path else "helv"
                    r, g, b = ((color_int >> 16) & 0xFF)/255, ((color_int >> 8) & 0xFF)/255, (color_int & 0xFF)/255
                    
                    # Scaling con dry-run (senza sporcare la pagina)
                    current_size = font_size
                    while current_size > 4:
                        test_doc = fitz.open()
                        test_page = test_doc.new_page(width=page.rect.width, height=page.rect.height)
                        rc = test_page.insert_textbox(bbox, translated_text, fontsize=current_size, fontname=font_tag, fontfile=font_path, align=block_align)
                        test_doc.close()
                        if rc >= 0: break
                        current_size -= 0.5

                    # Scrittura finale con allineamento originale
                    temp_page.insert_textbox(bbox, translated_text, fontsize=current_size, color=(r,g,b), fontname=font_tag, fontfile=font_path, align=block_align)

            # Footer
            footer = f"Engine: {self.engine.upper()} | Page: {page_num+1}"
            temp_page.insert_text((10, page.rect.height - 10), footer, fontsize=6, color=(0.7, 0.7, 0.7))
            
            new_doc.insert_pdf(temp_doc)
            temp_doc.close()

        new_doc.save(output_pdf)
        new_doc.close()
        print(f"\n[+] Successo! PDF salvato in: {output_pdf}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("target_lang", nargs="?", default="it")
    parser.add_argument("--engine", choices=["google", "libre"], default="google")
    parser.add_argument("--url", default="http://localhost:5000")
    args = parser.parse_args()
    
    out = args.input_file.replace(".pdf", f"_{args.target_lang}_{args.engine}.pdf")
    PDFTranslator(args.input_file, args.target_lang, args.engine, args.url).process(out)
