# PDF Layout-Aware Translator

Un traduttore di PDF intelligente scritto in Python che mantiene il layout originale, i font e le immagini, adattando automaticamente la dimensione del testo per far sì che la traduzione rientri negli spazi originali.

## Caratteristiche
- **Layout Preservation**: Mantiene immagini, grafica e posizionamento del testo originale.
- **Intelligent Font Mapping**: Riconosce Arial, Times New Roman e Courier New (se installati) per la massima fedeltà visiva.
- **Auto-scaling**: Riduce dinamicamente la dimensione del font se la traduzione è più lunga dell'originale.
- **Supporto Multilingua**: Utilizza Google Translate via `deep-translator`.
- **OCR Fallback**: Predisposto per gestire pagine difficili tramite Tesseract OCR.

## Requisiti di Sistema
Il programma dà il meglio di sé su Linux con i font Microsoft installati:
```bash
sudo apt update
sudo apt install ttf-mscorefonts-installer tesseract-ocr tesseract-ocr-ita
```

## Installazione
1. Clona il repository.
2. Installa le dipendenze Python:
```bash
pip install -r requirements.txt
```

## Utilizzo
Esegui il programma passando il file PDF e la lingua di destinazione (opzionale, default: `it`):
```bash
python3 translator.py "Il_Mio_Libro.pdf" it
```

## Crediti e Riferimenti
- **PyMuPDF (fitz)**: Per la manipolazione avanzata dei PDF.
- **deep-translator**: Per l'interfaccia con i servizi di traduzione.
- **Google Translate**: Motore di traduzione.

## Licenza
Distribuito sotto licenza MIT. Vedere il file `LICENSE` per i dettagli.
