# PDF Layout-Aware Translator (Block-Based)

Un traduttore di PDF intelligente scritto in Python che mantiene il layout originale, i font e le immagini, adattando automaticamente la dimensione del testo per far sì che la traduzione rientri negli spazi originali.

## Caratteristiche
- **Layout Preservation**: Mantiene immagini, grafica e posizionamento del testo originale tramite traduzione a blocchi.
- **Motori di Traduzione**:
  - **Google Translate**: Affidabile, gratuito e veloce (default).
  - **LibreTranslate**: Open-source, ideale per la privacy (supporta istanze pubbliche o locali via Docker).
- **Intelligent Font Mapping**: Supporta Arial, Times New Roman e Courier New per la massima fedeltà visiva.
- **Auto-scaling**: Riduce dinamicamente la dimensione del font se la traduzione è più lunga dell'originale per non rompere il layout.
- **CLI Avanzata**: Gestione parametri tramite `argparse`.

## Requisiti di Sistema
Per i font Microsoft (consigliato su Linux):
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

### Esempi Rapidi
```bash
# Traduzione standard in italiano (usa Google Translate)
python3 translator.py "Il_Mio_Libro.pdf" it

# Traduzione usando LibreTranslate (istanza pubblica)
python3 translator.py "Il_Mio_Libro.pdf" it --engine libre

# Traduzione con istanza locale di LibreTranslate (es: Docker su porta 5000)
python3 translator.py "Il_Mio_Libro.pdf" it --engine libre --url http://localhost:5000
```

### Parametri Disponibili
| Parametro | Descrizione |
|-----------|-------------|
| `input_file` | Percorso del file PDF da tradurre. |
| `target_lang` | Lingua di destinazione (es: `it`, `en`, `fr`). Default: `it`. |
| `--engine` | Motore da usare: `google` o `libre`. Default: `google`. |
| `--url` | (LibreTranslate) URL dell'istanza da usare. |
| `--api-key` | (LibreTranslate) API Key se richiesta dall'istanza. |

## Come avviare LibreTranslate Locale (Docker)
Per la massima velocità e privacy, puoi avviare LibreTranslate sul tuo computer:
```bash
docker run -ti -p 5000:5000 libretranslate/libretranslate
```
Poi usa lo script con `--url http://localhost:5000`.

## Crediti e Riferimenti
- **PyMuPDF (fitz)**: Per la manipolazione avanzata dei PDF.
- **deep-translator**: Per l'interfaccia con i servizi di traduzione.
- **Google Translate / LibreTranslate**: Motori di traduzione supportati.

## Licenza
Distribuito sotto licenza MIT. Vedere il file `LICENSE` per i dettagli.
