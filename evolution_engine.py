import time
import random
import sys
import os
import ollama
from universal_lsr_agent import AgenticOS

class EvolutionEngine:
    def __init__(self, agent_os: AgenticOS, meta_controller=None):
        self.os = agent_os
        self.meta = meta_controller
        self.is_running = False
        self.strategy_history = []

    def get_knowledge_summary(self):
        """Analizuje pamięć pod kątem domen i nasycenia wiedzy."""
        if not self.os.rag.memory:
            return "Pamięć jest pusta. Brak fundamentów."
        
        domains = {}
        for m in self.os.rag.memory:
            d = m.get('metadata', {}).get('domain', 'Inne')
            domains[d] = domains.get(d, 0) + 1
        
        summary = "HORYZONT WIEDZY (Domeny):\n"
        for d, count in domains.items():
            summary += f"- {d}: {count} perełek\n"
        return summary

    def get_worldview_axioms(self, limit=3):
        """Pobiera najbardziej 'witalne' perełki."""
        if not self.os.rag.memory:
            return ""
        active_memory = [m for m in self.os.rag.memory if m.get('metadata', {}).get('status') != 'DEPRECATED']
        if not active_memory: return ""
        sorted_memory = sorted(active_memory, key=lambda x: x.get('metadata', {}).get('usage_count', 0), reverse=True)
        axioms = sorted_memory[:limit]
        context = "\nAKTUALNE AKSJOMATY:\n"
        for a in axioms:
            context += f"- [{a.get('metadata', {}).get('id', 'N/A')}]: {a['text']}\n"
        return context

    def generate_curiosity_cartographer(self):
        """Strategia Top-down: Szukanie brakujących fundamentów."""
        summary = self.get_knowledge_summary()
        prompt = f"""
        Jesteś Strategiem-Kartografem AGI. Oto podsumowanie Twojej obecnej wiedzy:
        {summary}
        
        ZIDENTYFIKUJ domenę, która jest najsłabiej rozwinięta lub brakuje w niej fundamentów.
        ZAPROPONUJ ogólne, fundamentalne pytanie badawcze, które zbuduje szeroką bazę w tej lub nowej dziedzinie.
        Pytanie musi zaczynać się od 'Zbuduj fundamenty dla:' lub 'Zdefiniuj ogólne zasady:'.
        Zwróć TYLKO treść pytania.
        """
        try:
            res = ollama.generate(model=self.os.lsr.llm_model, prompt=prompt)
            return res['response'].strip()
        except Exception as e:
            print(f"[ENGINE] Błąd generowania ciekawości Kartografa: {e}")
            return "Zbuduj fundamenty dla: ogólnej teorii systemów złożonych."

    def generate_curiosity_explorer(self):
        """Strategia Bottom-up: Głęboka analiza i skoki intuicyjne."""
        if not self.os.rag.memory:
            return self.generate_curiosity_cartographer()
            
        random_gem = random.choice(self.os.rag.memory)
        prompt = f"""
        Jesteś Intuicyjnym Odkrywcą AGI. Twoim celem jest głęboka specjalizacja lub szalony skok myślowy.
        Bazując na fakcie: '{random_gem['text']}'
        ZAPROPONUJ paradoks, zderzenie z inną dziedziną lub ekstremalne pogłębienie detalu.
        Zwróć TYLKO treść pytania.
        """
        try:
            res = ollama.generate(model=self.os.lsr.llm_model, prompt=prompt)
            return res['response'].strip()
        except Exception as e:
            print(f"[ENGINE] Błąd generowania ciekawości Odkrywcy: {e}")
            return f"Znajdź paradoks w: '{random_gem['text'][:80]}'"

    def select_strategy(self):
        """Model decyduje o strategii, biorąc pod uwagę nasycenie wiedzy (Boredom)."""
        summary = self.get_knowledge_summary()
        
        # Sugestia filarów AGI, aby poszerzyć horyzont
        pillars = "Polecane filary: ETYKA, FIZYKA, SOCJOLOGIA, SZTUKA, BIOLOGIA, EKONOMIA"
        
        prompt = f"""
        Analiza Twojego Horyzontu Wiedzy:
        {summary}
        
        {pillars}
        
        ZASADA NASYCENIA (Boredom): Jeśli w jednej domenie masz już wiele perełek, 
        dalsza eksploracja detali może prowadzić do stagnacji. 
        Czy chcesz dalej zgłębiać obecne tematy (ODKRYWCA), 
        czy czujesz nasycenie i chcesz zbudować fundamenty w NOWEJ domenie (KARTOGRAF)?
        
        Odpowiedz TYLKO jednym słowem: KARTOGRAF lub ODKRYWCA.
        """
        res = ollama.generate(model=self.os.lsr.llm_model, prompt=prompt)
        choice = res['response'].strip().upper()
        return "KARTOGRAF" if "KARTOGRAF" in choice else "ODKRYWCA"

    def run_evolution_cycle(self):
        """Pojedynczy cykl ewolucji z wyborem strategii."""
        strategy = self.select_strategy()
        print(f"\n[ENGINE] Tryb wybrany przez model: {strategy}")
        
        if strategy == "KARTOGRAF":
            problem = self.generate_curiosity_cartographer()
        else:
            problem = self.generate_curiosity_explorer()

        print(f"[ENGINE] >>> INICJACJA CIEKAWOŚCI: {problem}")
        
        original_prompt = self.os.lsr.system_prompt
        self.os.lsr.system_prompt += self.get_worldview_axioms()
        
        try:
            if self.meta:
                self.meta.run_conscious_cycle(problem)
            else:
                self.os.execute_loop(problem)
        except Exception as e:
            print(f"[ENGINE] Błąd: {e}")
        finally:
            self.os.lsr.system_prompt = original_prompt

    def start(self, interval_seconds=45):
        self.is_running = True
        print("\n" + "="*50)
        print("   SILNIK AUTOEWOLUCJI MetaC-Arch v3.0 (DUAL STRATEGY)")
        print("="*50)
        try:
            while self.is_running:
                self.run_evolution_cycle()
                print(f"\n[ENGINE] Cykl zakończony. Odczekaj {interval_seconds}s...")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            self.is_running = False
