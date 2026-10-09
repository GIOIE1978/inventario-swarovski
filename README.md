# Inventario Swarovski

Dashboard di magazzino generata dalle fatture Swarovski (cartella Drive "Fatture Swarovski").

- `data/righe.txt` — righe estratte dalle fatture (fattura | data | codice | descrizione | qtà | importo riga)
- `build_data.py` — calcola giacenze e costo unitario (importo riga ÷ qtà, 2 decimali) → `data.json`
- `index.html` — web app (GitHub Pages)

Per aggiornare: aggiungi le nuove righe a `data/righe.txt`, esegui `python3 build_data.py`, fai commit e push.
