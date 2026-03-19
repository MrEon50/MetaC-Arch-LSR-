import time
import sys
import os
import ollama
from config import LLM_MODEL, EMBED_MODEL, THRESHOLD_U, MEMORY_FILE
from universal_lsr_agent import AgenticOS
from metac import MetaController
from evolution_engine import EvolutionEngine

# ============================================
# ESTETYKA TERMINALA
# ============================================
LOGO = """
╔══════════════════════════════════════════════════════╗
║   🧠  GNOSIS LSR × MetaC-Arch                      ║
║   ──  INTEGRACJA SYSTEMÓW DEEP AI  ──              ║
╚══════════════════════════════════════════════════════╝"""

SEPARATOR = "─" * 56

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_installed_models():
    try:
        response = ollama.list()
        if hasattr(response, 'models'):
            return [m.model for m in response.models]
        else:
            return [m.get('model', m.get('name', '')) for m in response.get('models', [])]
    except Exception:
        return []

def estimate_cycle_time(model_name, num_cycles):
    """Szacuje czas trwania cykli na podstawie rozmiaru modelu."""
    # Przybliżone czasy w sekundach na cykl (strategia + LSR + DAG Judge)
    size_map = {
        "1b": 15, "3b": 25, "7b": 45, "8b": 50, 
        "9b": 55, "13b": 80, "14b": 85, "32b": 150, "70b": 300
    }
    per_cycle = 60  # domyślnie
    for key, val in size_map.items():
        if key in model_name.lower():
            per_cycle = val
            break
    
    total = per_cycle * num_cycles
    if total < 60:
        return f"~{total}s"
    elif total < 3600:
        return f"~{total // 60}m {total % 60}s"
    else:
        return f"~{total // 3600}h {(total % 3600) // 60}m"

def print_header(model_name, gem_count=0):
    print(LOGO)
    print(f"  Model: {model_name} | Próg U: {THRESHOLD_U} | Perełki: {gem_count}")
    print(SEPARATOR)

# ============================================
# CHAT Z KOMENDAMI
# ============================================
CHAT_HELP = """
╔═══════════════════════════════════════╗
║  KOMENDY CZATU                       ║
╠═══════════════════════════════════════╣
║  /exit   - Powrót do menu głównego   ║
║  /help   - Pokaż tę pomoc            ║
║  /status - Status systemu            ║
║  /gems   - Pokaż perełki wiedzy      ║
║  /clear  - Wyczyść ekran             ║
╚═══════════════════════════════════════╝"""

def handle_chat_command(cmd, os_instance, meta, current_model):
    """Obsługuje komendy w trybie czatu. Zwraca True jeśli /exit."""
    cmd = cmd.strip().lower()
    
    if cmd == '/exit':
        return True
    elif cmd == '/help':
        print(CHAT_HELP)
    elif cmd == '/status':
        print(f"\n  Model: {current_model}")
        print(f"  Perełki: {len(os_instance.rag.memory)}")
        print(f"  Ostatnie U: {meta.last_u_score}")
        print(f"  Decyzje podjęte: {len(meta.history)}")
    elif cmd == '/gems':
        show_gems(os_instance)
    elif cmd == '/clear':
        clear_screen()
    else:
        print(f"  Nieznana komenda: {cmd}. Wpisz /help")
    return False

def show_gems(os_instance):
    """Wyświetla perełki wiedzy z informacjami o domenie."""
    memory = os_instance.rag.memory
    if not memory:
        print("\n  Pamięć jest pusta.")
        return
    
    # Statystyki domen
    domains = {}
    for m in memory:
        d = m.get('metadata', {}).get('domain', 'Inne')
        domains[d] = domains.get(d, 0) + 1
    
    print(f"\n{SEPARATOR}")
    print(f"  💎 PEREŁKI WIEDZY ({len(memory)} łącznie)")
    print(f"  📊 Domeny: {', '.join([f'{d}({c})' for d, c in domains.items()])}")
    print(SEPARATOR)
    
    for i, gem in enumerate(memory, 1):
        meta_data = gem.get('metadata', {})
        u_val = meta_data.get('u_score', 'N/A')
        domain = meta_data.get('domain', 'Inne')
        gem_type = meta_data.get('type', '?')
        status = meta_data.get('status', 'ACTIVE')
        
        icon = "💎" if gem_type == "AXIOM" else "📝"
        status_icon = "✓" if status == "ACTIVE" else "✗"
        
        print(f"  {i}. {icon} [{meta_data.get('id')}]")
        print(f"     {status_icon} {domain} | U={u_val} | usage={meta_data.get('usage_count')} | {gem_type}")
        print(f"     {gem['text'][:100]}...")

# ============================================
# MENU GŁÓWNE
# ============================================
def main_menu():
    current_model = LLM_MODEL
    os_instance = None
    meta = None

    while True:
        gem_count = len(os_instance.rag.memory) if os_instance else 0
        clear_screen()
        print_header(current_model, gem_count)
        
        print(f"""
  1. 🧠  WYBIERZ MODEL OLLAMA
  2. 💬  CZAT OGÓLNY (z oceną Meta-Kontrolera)
  3. 🧬  URUCHOM CYKL EWOLUCJI (LSR)
  4. 💎  PRZEGLĄDAJ PEREŁKI WIEDZY
  5. 🛡️   STATUS SYSTEMU
  6. 🗑️   WYCZYŚĆ PAMIĘĆ
  0. 🚪  WYJŚCIE
{SEPARATOR}""")
        
        choice = input("  Opcja >> ").strip()

        # ── 1. WYBÓR MODELU ──
        if choice == '1':
            models = get_installed_models()
            if not models:
                print("\n  Brak modeli w Ollama. Upewnij się, że Ollama jest uruchomiona.")
                input("  Enter...")
                continue
            print(f"\n  Zainstalowane modele Ollama:")
            for i, m in enumerate(models, 1):
                marker = " ← aktywny" if m == current_model else ""
                print(f"  {i}. {m}{marker}")
            idx = input("\n  Wybierz numer (enter = powrót): ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(models):
                current_model = models[int(idx)-1]
                os_instance = None
                meta = None
                print(f"  Model zmieniony na: {current_model}")
                time.sleep(1)

        # ── 2. CZAT ŚWIADOMY ──
        elif choice == '2':
            if not os_instance or not meta or os_instance.lsr.llm_model != current_model:
                print(f"\n  Inicjalizacja z modelem {current_model}...")
                try:
                    os_instance = AgenticOS(llm_model=current_model)
                    meta = MetaController(os_instance, threshold=THRESHOLD_U)
                except Exception as e:
                    print(f"  Błąd inicjalizacji: {e}")
                    input("\n  Enter...")
                    continue
            
            clear_screen()
            print(f"\n{SEPARATOR}")
            print(f"  💬 CZAT OGÓLNY | Model: {current_model}")
            print(f"  Wpisz /help aby zobaczyć komendy")
            print(SEPARATOR)
            
            while True:
                query = input("\n  User >> ").strip()
                if not query:
                    continue
                
                # Obsługa komend
                if query.startswith('/'):
                    if handle_chat_command(query, os_instance, meta, current_model):
                        break
                    continue
                
                result = meta.run_conscious_cycle(query)
                if result:
                    print(f"\n  [DEEP AI] {result['synthetic_truth']}")
                else:
                    response = os_instance.lsr.synthesize(query, os_instance.rag.search(query))
                    if response:
                        print(f"\n  [AI - Low U] {response.get('synthetic_truth', 'Błąd syntezy.')}")

        # ── 3. CYKL EWOLUCJI ──
        elif choice == '3':
            if not os_instance or not meta:
                print(f"\n  Inicjalizacja z modelem {current_model}...")
                try:
                    os_instance = AgenticOS(llm_model=current_model)
                    meta = MetaController(os_instance, threshold=THRESHOLD_U)
                except Exception as e:
                    print(f"  Błąd: {e}")
                    input("\n  Enter...")
                    continue
            
            engine = EvolutionEngine(os_instance, meta_controller=meta)
            
            try:
                msg = "\n  Ile cykli? (domyślnie 1, 'auto' dla ciągłej): "
                num_input = input(msg).strip().lower()
                
                if num_input == 'auto':
                    engine.start(interval_seconds=30)
                else:
                    count = int(num_input) if num_input.isdigit() else 1
                    est = estimate_cycle_time(current_model, count)
                    print(f"\n  ⏱ Szacowany czas: {est} ({count} cykli)")
                    print(SEPARATOR)
                    
                    for i in range(count):
                        print(f"\n{'='*40}")
                        print(f"  CYKL {i+1}/{count}")
                        print(f"{'='*40}")
                        engine.run_evolution_cycle()
                    
                    input(f"\n  Cykle zakończone. Enter...")
            except KeyboardInterrupt:
                print("\n  Ewolucja przerwana.")
                time.sleep(1)
            except Exception as e:
                print(f"  Błąd: {e}")
                time.sleep(2)

        # ── 4. PEREŁKI WIEDZY ──
        elif choice == '4':
            if not os_instance or not meta:
                os_instance = AgenticOS(llm_model=current_model)
                meta = MetaController(os_instance, threshold=THRESHOLD_U)
            show_gems(os_instance)
            input(f"\n  Enter...")

        # ── 5. STATUS ──
        elif choice == '5':
            print(f"\n{SEPARATOR}")
            print(f"  🛡️  STATUS SYSTEMU")
            print(SEPARATOR)
            print(f"  Model aktywny:    {current_model}")
            print(f"  Model embeddingów: {EMBED_MODEL}")
            print(f"  Próg U (Unity):   {THRESHOLD_U}")
            print(f"  Plik pamięci:     {MEMORY_FILE}")
            if os_instance:
                active = sum(1 for m in os_instance.rag.memory if m.get('metadata', {}).get('status') != 'DEPRECATED')
                deprecated = len(os_instance.rag.memory) - active
                print(f"  Perełki aktywne:  {active}")
                print(f"  Perełki wycofane: {deprecated}")
            if meta:
                print(f"  Decyzji MetaC:    {len(meta.history)}")
                print(f"  Ostatnie U:       {meta.last_u_score}")
            input(f"\n  Enter...")

        # ── 6. RESET ──
        elif choice == '6':
            confirm = input("\n  Wyczyścić pamięć? (tak/nie): ").lower()
            if confirm == 'tak':
                if os.path.exists(MEMORY_FILE):
                    os.remove(MEMORY_FILE)
                os_instance = None
                meta = None
                print("  Pamięć wyczyszczona.")
                time.sleep(1)

        # ── 0. EXIT ──
        elif choice == '0':
            print("\n  Zamykanie systemu...")
            break

if __name__ == "__main__":
    main_menu()
