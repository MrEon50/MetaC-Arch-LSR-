import time
import json
import os
from scoring import U, calculate_novelty
from universal_lsr_agent import AgenticOS

HISTORY_FILE = "metac_history.json"

class MetaController:
    """
    Warstwa Zarządcza MetaC-Arch (Świadomość).
    Nadzoruje silnik ewolucyjny LSR i decyduje o globalnej akceptacji wiedzy.
    """
    def __init__(self, agent_os: AgenticOS, threshold=0.4):
        self.os = agent_os
        self.threshold = threshold
        self.history = []
        self.last_u_score = 0.0
        self._load_history()

    def _load_history(self):
        """Wczytuje historię decyzji z pliku."""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []

    def _save_history(self):
        """Zapisuje historię decyzji do pliku."""
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history[-100:], f, ensure_ascii=False, indent=2)  # max 100 wpisów
        except Exception:
            pass

    def _calculate_context_score(self, relevant_facts):
        """
        Dynamiczny Globalness (G): mierzy ile źródeł/domen użyto w kontekście.
        Zamiast hardcoded 0.6, liczymy rzeczywiste pokrycie.
        """
        if not relevant_facts:
            return 0.1
        
        # Ile unikalnych domen pokrywają znalezione fakty
        domains_hit = set()
        for fact in relevant_facts:
            domain = fact.get('metadata', {}).get('domain', 'Inne')
            domains_hit.add(domain)
        
        # Normalizujemy: więcej domen = wyższy Globalness
        total_domains_in_memory = set()
        for m in self.os.rag.memory:
            total_domains_in_memory.add(m.get('metadata', {}).get('domain', 'Inne'))
        
        if not total_domains_in_memory:
            return 0.3
        
        return len(domains_hit) / max(len(total_domains_in_memory), 1)

    def evaluate_proposal(self, candidate_gem: dict, relevant_facts=None):
        """
        Ocenia propozycję Perełki wygenerowaną przez LSR.
        Zwraca wynik U i decyzję o akceptacji.
        """
        if not candidate_gem:
            return 0.0, False

        text_to_score = candidate_gem.get("synthetic_truth", "")
        
        # Dynamiczny context_score (BUG 3 FIX)
        context_score = self._calculate_context_score(relevant_facts or [])
        
        # Gęstość grafu (Connectivity)
        nodes_count = len(self.os.rag.memory)
        graph_density = 0.1
        if nodes_count > 0:
            connected = sum(1 for m in self.os.rag.memory if m.get("metadata", {}).get("parent_ids"))
            graph_density = connected / nodes_count

        # Obliczamy wskaźnik U (Unity)
        u_score = U(text_to_score, context_score=context_score, graph_density=graph_density)
        self.last_u_score = u_score
        
        is_accepted = u_score >= self.threshold
        
        status = "ZAAKCEPTOWANO" if is_accepted else "ODRZUCONO (Niskie U)"
        print(f"[MetaC] Ocena Perełki '{candidate_gem.get('gem_id')}': U={u_score} -> {status}")
        
        self.history.append({
            "timestamp": time.time(),
            "gem_id": candidate_gem.get("gem_id"),
            "domain": candidate_gem.get("domain", "Inne"),
            "u_score": u_score,
            "accepted": is_accepted
        })
        self._save_history()
        
        return u_score, is_accepted

    def run_conscious_cycle(self, problem: str):
        """
        Uruchamia cykl 'świadomy' - LSR generuje, MetaC decyduje.
        """
        print(f"\n[MetaC] >>> ŚWIADOMA REFLEKSJA NAD: '{problem}'")
        
        # 1. Pobranie faktów
        relevant_facts = self.os.rag.search(problem)
        parent_ids = [f['metadata'].get('id', 'unknown') for f in relevant_facts]
        
        # 2. Generowanie kandydata przez LSR (Podświadomość)
        gem_candidate = self.os.lsr.synthesize(problem, relevant_facts)
        
        if not gem_candidate:
            print("[MetaC] Błąd syntezy w warstwie LSR.")
            return None

        # 3. Ewaluacja przez Meta-Kontrolera (Filtr Świadomości)
        u_score, accepted = self.evaluate_proposal(gem_candidate, relevant_facts)
        
        if accepted:
            # 4. Walidacja LLM-as-Judge (DAG) z przekazaniem istniejącej wiedzy
            if self.os.dag.validate(gem_candidate, existing_knowledge=relevant_facts):
                # 5. Globalny rozgłos (Broadcast) -> Zapis do pamięci
                truth = gem_candidate['synthetic_truth']
                gem_type = "AXIOM" if u_score > 0.7 else "KNOWLEDGE"
                
                self.os.rag.add_gem(
                    truth,
                    metadata={
                        "id": gem_candidate['gem_id'], 
                        "domain": gem_candidate.get('domain', 'Inne'),
                        "u_score": u_score,
                        "type": gem_type
                    },
                    parent_ids=parent_ids
                )
                
                # Samokorekta
                for old_id in gem_candidate.get('deprecate_ids', []):
                    self.os.rag.deprecate_gem(old_id)
                
                print(f"[MetaC] 💎 Nowa PRAWDA SYSTEMOWA [{gem_type}]: {gem_candidate['gem_id']}")
                return gem_candidate
            else:
                print("[MetaC] Odrzucono: Sędzia DAG wykrył sprzeczność logiczną.")
        else:
            print(f"[MetaC] Odrzucono: Zbyt niska integracja (U={u_score} < PROG={self.threshold}).")
            
        return None

if __name__ == "__main__":
    try:
        from config import LLM_MODEL
        os_system = AgenticOS(llm_model=LLM_MODEL)
        meta = MetaController(os_system)
        meta.run_conscious_cycle("Definicja samoświadomego systemu w architekturze MetaC-LSR.")
    except Exception as e:
        print(f"Błąd inicjalizacji MetaC: {e}")
