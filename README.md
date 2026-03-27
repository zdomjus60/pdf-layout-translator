# PDF Layout-Aware Translator (Block-Based)

Un traduttore di PDF intelligente scritto in Python che mantiene il layout originale, i font e le immagini, adattando automaticamente la dimensione del testo per far sì che la traduzione rientri negli spazi originali.

## Caratteristiche
- **Layout Preservation**: Mantiene immagini, grafica e posizionamento del testo originale tramite traduzione a blocchi.
- **Motori di Traduzione**:
  - **Google Translate**: Affidabile e veloce (default).
  - **LibreTranslate (Consigliato)**: Open-source, 100% privacy, se usato localmente via Docker.
- **Auto-scaling Intelligente**: Riduce la dimensione del font solo se strettamente necessario (scaling "pigro").
- **Traduzione Batch**: Esegue una sola richiesta per pagina per massima velocità e stabilità.

## Come usare LibreTranslate locale (Docker) - SOLUZIONE DEFINITIVA
Per evitare blocchi e avere privacy totale, avvia il tuo server di traduzione:

1. Assicurati di avere Docker installato.
2. Avvia il server:
   ```bash
   docker-compose up -d
   ```
   *Nota: Al primo avvio scaricherà circa 1GB di modelli linguistici (Inglese e Italiano).*

## Installazione
1. Clona il repository.
2. Installa le dipendenze Python:
```bash
pip install -r requirements.txt
```

## Utilizzo

### Esempi
```bash
# Traduzione con Google Translate (veloce, ma meno privacy)
python3 translator.py "Libro.pdf" it

# Traduzione con LibreTranslate LOCALE (Docker attivo su localhost:5000)
python3 translator.py "Libro.pdf" it --engine libre
```

### Parametri Disponibili
| Parametro | Descrizione |
|-----------|-------------|
| `input_file` | Percorso del file PDF da tradurre. |
| `target_lang` | Lingua di destinazione (default: `it`). |
| `--engine` | Motore da usare: `google` o `libre`. Default: `google`. |
| `--url` | URL dell'istanza LibreTranslate (default: `http://localhost:5000`). |

## Crediti
- **PyMuPDF (fitz)**: Manipolazione PDF.
- **deep-translator**: Interfaccia traduzione.
- **LibreTranslate**: Motore open-source.

## Licenza
MIT
