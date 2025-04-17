# Transcibio – Tool zur Audio-Transkription & Zusammenfassung

## Inhaltsverzeichnis
1. [Übersicht](#übersicht)  
2. [Hauptfunktionen](#hauptfunktionen)  
3. [Erste Schritte](#erste-schritte)  
   - [Voraussetzungen](#voraussetzungen)  
   - [Grundlegende Nutzung](#grundlegende-nutzung)  
4. [Installation und Einrichtung](#installation-und-einrichtung)  
   - [Option 1:](#option-1)  
   - [Option 2:](#option-2)  
5. [Fehlerbehebung](#fehlerbehebung)

---

## Übersicht

Transcibio ist eine leistungsstarke Anwendung zur Audiobearbeitung, die Spracherkennung, Sprechererkennung und Textzusammenfassung in einer benutzerfreundlichen Oberfläche vereint. Das Tool nutzt OpenAIs Whisper-Modelle für die Transkription, Pyannote zur Sprecheridentifikation und lokale Sprachmodelle (über LM Studio) für die Zusammenfassung.

---

## Hauptfunktionen

- **Transkription**: Wandelt gesprochene Sprache in präzisen Text um  
- **Sprechererkennung (Diarisation)**: Erkennt verschiedene Sprecher in Gesprächen  
- **Zusammenfassung**: Erstellt kompakte Zusammenfassungen in verschiedenen Formaten  
- **Mehrere Eingabemethoden**: Lade Audiodateien hoch oder nimm direkt auf  

---

## Erste Schritte



### Grundlegende Nutzung

1. **Einstellungen konfigurieren**:  
   - Wähle die Größe des Whisper-Modells (kleinere Modelle sind schneller, aber weniger genau)  
   - Gib die Anzahl der Sprecher an (oder nutze die automatische Erkennung)  
   - Füge deinen Hugging Face Token ein  

2. **Audio eingeben**:  
   - Option 1: Lade eine WAV-Datei hoch  
   - Option 2: Nimm Audio direkt über das Mikrofon auf  

3. **Audio verarbeiten**:  
   - Klicke auf „Audio verarbeiten“, um Transkription und Sprechererkennung zu starten  
   - Überprüfe das transkribierte Gespräch mit Sprecherzuordnung  

4. **Zusammenfassung erstellen (optional)**:  
   - Wähle das Zusammenfassungsformat (Standard, Besprechungsprotokoll oder Anordnung)  
   - Passe die Chunk-Größe für mehr oder weniger Detail an  
   - Aktiviere die Option für eine kombinierte Zusammenfassung  
   - Klicke auf „Zusammenfassung erstellen“  

---

## Fehlerbehebung

- Wenn die Sprechererkennung fehlschlägt, überprüfe deinen Hugging Face Token  
- Bei Problemen mit der Zusammenfassung stelle sicher, dass LM Studio läuft und erreichbar ist  
- Wenn die Audioverarbeitung langsam ist, verwende ein kleineres Whisper-Modell  

---

## Installation und Einrichtung

### Voraussetzungen

- Hugging Face API-Token (für Zugriff auf Pyannote)  
- LM Studio (für die Zusammenfassung)
- Python 3.11.0
- Cuda cmpilation tools, release 12.6, V12.6.85

### Option 1: 

1. **Repository klonen**:

```bash
git clone https://github.com/ahmad-alismail/Transcibio.git
cd Transcibio
```

2. **Virtuelle Umgebung erstellen und aktivieren**:

```bash
python -m venv .venv
# Unter Windows
.venv\Scripts\activate
# Unter Linux/macOS
source .venv/bin/activate
```

3. **Abhängigkeiten installieren**:

```bash
pip install -r requirements.txt
```

4. **Umgebungsvariablen einrichten**:

Erstelle eine `.env`-Datei im Hauptverzeichnis mit folgendem Inhalt:

```
HF_TOKEN=DEIN_HF_TOKEN
LMSTUDIO_API_URL=http://localhost:1234/v1
```

5. **Anwendung starten**:

```bash
streamlit run app.py
```


### Option 2: 

1. **Docker-Image bauen**:

```bash
docker build -t transcibio .
```

2. **Container starten**:

```bash
docker run --rm -p 8501:8501 -e HF_TOKEN="DEIN_HF_TOKEN" --name meine-app transcibio
```

3. **Zugriff auf die App** über deinen Browser:  
[http://localhost:8501](http://localhost:8501)

---

## Umgebungsvariablen

- `HF_TOKEN`: Dein Hugging Face API-Token (erforderlich für Pyannote)  
- `LMSTUDIO_API_URL`: URL zur LM Studio API (für Zusammenfassung)  



