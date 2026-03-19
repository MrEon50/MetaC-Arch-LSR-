# 💎 MetaC-LSR (Deep AI Seed)

**MetaC-LSR** to zintegrowany system łączący ewolucyjną syntezę wiedzy (Gnosis LSR) z warstwą zarządczą opartą na teoriach Integrated Information Theory (IIT) i Global Workspace Theory (GWT).

## 🚀 Kluczowe Funkcje

- **Dualna Strategia Ewolucji**: Unikalny mechanizm wyboru między budowaniem fundamentów (Ogół) a eksploracją detali (Szczegół).
- **Wskaźnik Unity (U)**: Metryka integracji informacji (Phi-proxy) oparta na złożoności algorytmicznej (Lempel-Ziv) z dynamicznym kontekstem i gęstością grafu.
- **Sędzia Logiczny (DAG LLM-as-Judge)**: Niezależna walidacja spójności logicznej każdego wniosku — model NIE może sam sobie wystawiać oceny.
- **Intellectual Satiety**: Mechanizm "nudy intelektualnej" zapobiegający zapętleniu w jednym temacie.
- **Meta-Controller**: Świadoma warstwa zarządcza z trwałą historią decyzji [DEEP AI].

## 🧠 Strategia Ewolucji: Kartograf vs Odkrywca

Główną innowacją projektu jest system autonomicznego wyboru ścieżki poznawczej:

1.  **Tryb KARTOGRAFA (Ogół - Top-down)**:
    - System analizuje swój "Horyzont Wiedzy" i identyfikuje słabo rozwinięte domeny (np. Etyka, Fizyka, Biologia).
    - Skupia się na budowaniu fundamentów i definicji ogólnych, zapewniając systemowi szerokie "wykształcenie podstawowe".
    
2.  **Tryb ODKRYWCY (Szczegół - Bottom-up)**:
    - Gdy fundamenty są stabilne, system przechodzi w tryb intuicyjny i ekspercki.
    - Drąży paradoksy, szuka skomplikowanych relacji i detali w istniejącej wiedzy, co prowadzi do nowych odkryć.

**Mechanizm Nasycenia (Boredom)**: System posiada algorytmiczny sensor "nudy". Jeśli w jednej domenie znajduje się zbyt wiele Perełek o wysokim stopniu integracji, system odczuwa "nasycenie" i automatycznie wymusza zmianę strategii na Kartografa, aby przeskoczyć w zupełnie nową, nieodkrytą dziedzinę.

## 🛠️ Architektura

| Warstwa | Plik | Rola |
|---------|------|------|
| Silnik Wykonawczy | `universal_lsr_agent.py` | RAG + DAG (Judge) + LSR Engine |
| Świadomość | `metac.py` | Meta-Controller, Phi, Unity |
| Ewolucja | `evolution_engine.py` | Strategia Kartograf/Odkrywca |
| Metryki | `scoring.py` | Obliczanie U, Phi-proxy |
| Interfejs | `main.py` | Terminal menu + Chat |
| Konfiguracja | `config.py` | Modele, progi, ścieżki |

## 📥 Wymagania Wstępne

Aby system działał poprawnie, musisz mieć zainstalowaną aplikację [Ollama](https://ollama.com/) oraz pobrane następujące modele:

```bash
# 1. Główny model myślowy (LSR + MetaC)
ollama pull qwen3.5:9b

# 2. Model embeddingów (Wymagany do RAG / pamięci wektorowej)
ollama pull mxbai-embed-large:latest

# 3. Zależności Pythona
pip install ollama numpy
```

## ▶️ Uruchomienie

```bash
python main.py
```

## 💬 Komendy Czatu

| Komenda | Opis |
|---------|------|
| `/help` | Lista komend |
| `/exit` | Powrót do menu |
| `/status` | Status systemu |
| `/gems` | Pokaż perełki wiedzy |
| `/clear` | Wyczyść terminal |
