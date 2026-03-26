import fitz
import os
from deep_translator import GoogleTranslator
from tqdm import tqdm
import math

class PDFTranslator:
    def __init__(self, input_pdf, target_lang='it'):
        self.input_pdf = input_pdf
        self.target_lang = target_lang
        self.translator = GoogleTranslator(source='auto', target=target_lang)
        self.doc = fitz.open(input_pdf)

    def translate_text(self, text):
        if not text.strip() or text.strip().isdigit():
            return text
        try:
            return self.translator.translate(text)
        except Exception as e:
            print(f"Error translating text: {e}")
            return text

    def process(self, output_pdf):
        new_doc = fitz.open()

        for page_num in tqdm(range(len(self.doc)), desc="Translating pages"):
            page = self.doc[page_num]
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            
            # Copy images and graphics from the original page
            # This is done by showing the original page as an image/template or by copying objects.
            # A simpler way is to copy the page and then redact text.
            
            # For simplicity and layout preservation, we'll use the original page as a base
            # and "white out" the old text before writing the new one.
            
            # Let's create a temporary page to work on
            temp_doc = fitz.open()
            temp_page = temp_doc.new_page(width=page.rect.width, height=page.rect.height)
            temp_page.show_pdf_page(temp_page.rect, self.doc, page_num)
            
            # Extract text blocks with detailed info
            dict_text = page.get_text("dict")
            
            for block in dict_text["blocks"]:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            original_text = span["text"]
                            if not original_text.strip():
                                continue
                                
                            translated_text = self.translate_text(original_text)
                            
                            # Original properties
                            font_size = span["size"]
                            font_name = span["font"]
                            color = span["color"] # integer color
                            origin = span["origin"] # (x, y)
                            bbox = span["bbox"] # (x0, y0, x1, y1)
                            
                            # Cover original text with a white rectangle (simplified)
                            # In a real scenario, we might want to detect background color
                            temp_page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
                            
                            # Try to fit the translated text in the same bbox
                            current_font_size = font_size
                            
                            # Function to calculate text width
                            def get_text_width(text, size, font):
                                return fitz.get_text_length(text, fontname="helv", fontsize=size) # Using helv as fallback

                            # Simple font scaling
                            max_width = bbox[2] - bbox[0]
                            while get_text_width(translated_text, current_font_size, font_name) > max_width and current_font_size > 4:
                                current_font_size -= 0.5
                            
                            # Insert translated text
                            # We use a standard font like 'helv' if the original font is not available
                            # fitz.insert_text uses (x, y) origin. 
                            # The 'origin' from 'dict' is the baseline start.
                            try:
                                temp_page.insert_text(origin, translated_text, 
                                                    fontsize=current_font_size, 
                                                    color=fitz.utils.getColor(color) if isinstance(color, int) else color,
                                                    fontname="helv") # Using Helvetica as safe bet
                            except Exception as e:
                                print(f"Error inserting text at {origin}: {e}")

            # Append the modified page to our new document
            new_doc.insert_pdf(temp_doc)
            temp_doc.close()

        new_doc.save(output_pdf)
        new_doc.close()
        print(f"Saved translated PDF to {output_pdf}")

if __name__ == "__main__":
    import sys
    input_file = "TheLittlePrince.pdf"
    output_file = "TheLittlePrince_translated.pdf"
    
    if not os.path.exists(input_file):
        print(f"File {input_file} not found.")
        sys.exit(1)
        
    translator = PDFTranslator(input_file, target_lang='it')
    translator.process(output_file)
