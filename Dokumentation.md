# Dokumentation: Transcibio (Seite 1/3)

## 1. Einleitung und Projektziel

**Transcibio** ist eine Demonstrator-Anwendung, die im Rahmen des Forschungsprojekts **AI Traqc** an der **Hochschule Heilbronn** entwickelt wurde. Das Hauptziel des Projekts ist es, die Fähigkeiten moderner KI-Modelle im Bereich der Audioverarbeitung aufzuzeigen und praktisch erlebbar zu machen.

Die Anwendung konzentriert sich auf eine vollständig **lokale Verarbeitung** von Audiodaten, um Datenschutz und Unabhängigkeit von Cloud-Diensten zu gewährleisten.

### Kernfunktionen

*   **Automatische Transkription:** Umwandlung von gesprochener Sprache in Text mithilfe von OpenAIs Whisper-Modell.
*   **Sprecher-Diarisierung:** Erkennung und Zuordnung von Sprachsegmenten zu verschiedenen Sprechern ("Wer hat wann gesprochen?"). Dies wird durch `pyannote.audio` realisiert.
*   **KI-gestützte Zusammenfassung:** Erstellung von Inhaltszusammenfassungen der Transkripte durch ein lokal betriebenes Large Language Model (LLM) über LM Studio.

---

## 2. Bedienungsanleitung

Die Benutzeroberfläche ist in einen Hauptbereich für die Interaktion und eine Seitenleiste für die Konfiguration unterteilt.

### Schritt 1: Konfiguration in der Seitenleiste

Bevor Sie Audio verarbeiten, nehmen Sie die gewünschten Einstellungen in der linken Seitenleiste vor:

1.  **Transcription & Diarization:**
    *   **Whisper Model:** Wählen Sie ein Whisper-Modell. Größere Modelle (`large`) sind genauer, aber langsamer. Kleinere Modelle (`base`, `small`) sind schneller.
    *   **Number of Speakers:** Geben Sie die bekannte Anzahl der Sprecher an. Wenn die Anzahl unbekannt ist, belassen Sie den Wert bei `0` für eine automatische Erkennung.

2.  **Hugging Face (für Diarisierung):**
    *   Für die Sprecher-Diarisierung wird ein Hugging Face Token benötigt.
    *   Wenn das Token nicht automatisch gefunden wird, geben Sie es manuell in das passwortgeschützte Feld ein. Ohne Token ist die Diarisierung deaktiviert.

3.  **Summarization (LM Studio):**
    *   Stellen Sie sicher, dass **LM Studio** auf Ihrem Computer läuft, ein Modell geladen und der Server gestartet ist.
    *   **LM Studio API URL:** Geben Sie die URL Ihres LM-Studio-Servers ein (standardmäßig `http://localhost:1234/v1`).
    *   **Local Model Name:** Tragen Sie den Modell-Identifier ein, wie er in LM Studio angezeigt wird.

4.  **Summary Type:**
    *   Wählen Sie das gewünschte Format für die Zusammenfassung (z. B. Standard, Meeting-Protokoll).

### Schritt 2: Audioeingabe im Hauptbereich

Wählen Sie eine der beiden Methoden zur Audiobereitstellung:

*   **Upload File:** Laden Sie eine existierende `.wav`-Audiodatei hoch.
*   **Record Audio:** Nehmen Sie live Audio über Ihr Mikrofon auf.
    *   **Einverständnis:** Bei der ersten Nutzung müssen Sie die **Datenschutzhinweise** lesen und alle Checkboxen aktivieren, um Ihre Zustimmung zu geben.
    *   **Aufnahme:** Klicken Sie auf das Mikrofonsymbol, um die Aufnahme zu starten und erneut, um sie zu beenden.

### Schritt 3: Verarbeitung starten

1.  Klicken Sie auf den Button **"📊 Process Audio"**. Die Verarbeitung kann je nach Audiolänge und gewähltem Modell einige Zeit in Anspruch nehmen.
2.  Nach Abschluss wird das **sprecher-zugeordnete Transkript** im Hauptbereich angezeigt.

### Schritt 4: Zusammenfassung erstellen

1.  Wenn die Transkription erfolgreich war und LM Studio korrekt konfiguriert ist, erscheint der Button **"Generate Summary"**.
2.  Klicken Sie darauf, um eine Zusammenfassung des Transkripts zu erstellen. Das Ergebnis wird darunter angezeigt. 


## 3. Architektur und Anwendungsstruktur

Die Anwendung ist als monolithischer Service konzipiert, der alle Aufgaben lokal ausführt. Die Architektur ist in drei logische Hauptkomponenten gegliedert:

1.  **Benutzeroberfläche (Frontend):**
    *   Erstellt mit **Streamlit**, einem Python-Framework zur schnellen Entwicklung von interaktiven Webanwendungen für Data Science und KI.
    *   Verantwortlich für die Konfiguration, Dateiuploads, Audioaufnahme und die Darstellung der Ergebnisse.

2.  **Verarbeitungspipeline (Backend-Logik):**
    *   Dies ist das Herzstück der Anwendung und orchestriert die verschiedenen KI-Modelle.
    *   Die Pipeline wird aktiviert, wenn der Benutzer auf "Process Audio" klickt.
    *   Sie folgt einem sequenziellen Ablauf:
        1.  **Audio-Input:** Empfängt die Audiodatei (Upload oder Aufnahme).
        2.  **Diarisierung:** `pyannote.audio` analysiert die Audiodatei und identifiziert die Zeitstempel der verschiedenen Sprecher.
        3.  **Transkription:** Das Whisper-Modell transkribiert den gesamten Audioinhalt zu Text.
        4.  **Alignierung:** Die Ergebnisse aus Diarisierung und Transkription werden zusammengeführt, um jedem Textsegment einen Sprecher zuzuordnen.

3.  **Zusammenfassung (LLM-Integration):**
    *   Diese Komponente ist von der Haupt-Pipeline entkoppelt.
    *   Sie kommuniziert über eine **HTTP-API** mit dem **LM Studio Server**.
    *   Der transkribierte Text wird in Blöcke (Chunks) aufgeteilt und an das LLM gesendet, um Teil-Zusammenfassungen zu erstellen, die am Ende zu einem Gesamttext kombiniert werden.

### Dateistruktur

Die Codebasis ist wie folgt organisiert:

*   `app.py`: Die Hauptdatei, die die Streamlit-Anwendung und die Benutzeroberfläche definiert.
*   `src/`: Ein Verzeichnis, das die Kernlogik enthält, aufgeteilt in Module:
    *   `processing.py`: Funktionen für Diarisierung, Transkription und Alignierung.
    *   `summarization.py`: Logik für die Kommunikation mit LM Studio und die Erstellung von Zusammenfassungen.
    *   `utils.py`: Hilfsfunktionen (z. B. Speichern von Dateien).
*   `requirements.txt`: Listet alle Python-Abhängigkeiten des Projekts auf.
*   `consent.md`: Enthält den Text für die Einverständniserklärung.

---

## 4. Verwendete Technologien

*   **Sprache:** Python 3.9+
*   **Web-Framework:** Streamlit
*   **Transkription:** [Whisper](https://github.com/openai/whisper) (Modelle von OpenAI, ausgeführt mit `faster-whisper`)
*   **Sprecher-Diarisierung:** [pyannote.audio](https://github.com/pyannote/pyannote-audio) (erfordert ein Hugging Face Token)
*   **Lokales Large Language Model (LLM):** [LM Studio](https://lmstudio.ai/) als Host für Modelle wie Llama, Mistral etc.
*   **Audioaufnahme:** `audiorecorder` (Streamlit-Komponente)
*   **Abhängigkeitsmanagement:** `pip` und `requirements.txt`
*   **Containerisierung (optional):** Docker 


## 5. Installationsanleitung

Um die Anwendung lokal auszuführen, sind mehrere Schritte erforderlich. Diese Anleitung setzt voraus, dass **Python 3.9** oder höher sowie **Git** auf Ihrem System installiert sind.

### Schritt 1: Projekt-Repository klonen

Öffnen Sie ein Terminal und klonen Sie das Repository von GitHub:

```bash
git clone <URL_des_Repositorys>
cd <Name_des_geklonten_Ordners>
```

### Schritt 2: Python-Umgebung einrichten

Es wird dringend empfohlen, eine virtuelle Umgebung zu verwenden, um Abhängigkeitskonflikte zu vermeiden.

```bash
# Erstellen einer virtuellen Umgebung
python -m venv .venv

# Aktivieren der Umgebung
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

### Schritt 3: Abhängigkeiten installieren

Installieren Sie alle benötigten Python-Pakete mit `pip`:

```bash
pip install -r requirements.txt
```

**Hinweis:** Die Installation von `torch` und `torchaudio` (Abhängigkeiten von `pyannote.audio`) kann je nach System eine Weile dauern und erfordert möglicherweise eine stabile Internetverbindung.

### Schritt 4: Hugging Face Token konfigurieren

Die Sprecher-Diarisierung mit `pyannote.audio` benötigt eine Authentifizierung bei Hugging Face.

1.  Erstellen Sie ein Konto auf [huggingface.co](https://huggingface.co/).
2.  Akzeptieren Sie die Nutzungsbedingungen für die Modelle [pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization-py3.11) und [pyannote/segmentation](https://huggingface.co/pyannote/segmentation-py3.11).
3.  Erstellen Sie ein **Access Token** in Ihren Hugging Face-Profileinstellungen.
4.  **Optional (empfohlen):** Speichern Sie das Token als Umgebungsvariable `HF_TOKEN`, damit die Anwendung es automatisch laden kann. Alternativ können Sie es bei jeder Nutzung manuell in der Seitenleiste der Anwendung eingeben.

### Schritt 5: LM Studio einrichten (für Zusammenfassungen)

1.  Laden Sie **LM Studio** von [lmstudio.ai](https://lmstudio.ai/) herunter und installieren Sie es.
2.  Suchen und laden Sie in LM Studio ein passendes Modell herunter (z. B. `Mistral`, `Llama`).
3.  Wechseln Sie zum "Local Server"-Tab (Symbol `<->`).
4.  Wählen Sie das geladene Modell aus und starten Sie den Server durch Klick auf **"Start Server"**.
5.  Die angezeigte Server-URL (z.B. `http://localhost:1234/v1`) wird in der Transcibio-Anwendung benötigt.

### Schritt 6: Anwendung starten

Nachdem alle vorherigen Schritte abgeschlossen sind, starten Sie die Streamlit-Anwendung mit folgendem Befehl im Terminal:

```bash
streamlit run app.py
```

Die Anwendung sollte nun in Ihrem Webbrowser unter einer lokalen Adresse (z. B. `http://localhost:8501`) geöffnet werden. 