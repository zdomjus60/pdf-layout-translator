# Traduttore PDF Layout-Aware

Questo programma traduce PDF mantenendo il layout originale (immagini, grafica) e cercando di far rientrare il testo tradotto negli stessi spazi dell'originale, scalando il font se necessario.

## Funzionalità
- Estrazione del testo con coordinate precise tramite **PyMuPDF**.
- Traduzione tramite **Google Translate** (via `deep-translator`).
- Ricostruzione del PDF con sovrapposizione del testo tradotto.
- Auto-scaling dei font per preservare l'impaginazione.

## Requisiti
- Python 3.7+
- Librerie: `PyMuPDF`, `deep-translator`, `tqdm`

## Installazione
```bash
pip install -r requirements.txt
```

## Utilizzo
Modifica `translator.py` per cambiare lingua (default: `it`) o file di input, oppure eseguilo direttamente:
```bash
python translator.py
```

## Note Tecniche
- Il programma utilizza un font standard (Helvetica) per la traduzione per garantire la compatibilità, ma cerca di mantenere dimensione e colore originali.
- La "copertura" del testo originale avviene tramite rettangoli bianchi. Per PDF con sfondi non bianchi, il risultato potrebbe variare.
