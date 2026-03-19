import zlib
import math

# Minimalna długość tekstu dla wiarygodnej kompresji
MIN_TEXT_LENGTH = 50

def calculate_complexity(text):
    """
    Oblicza algorytmiczną złożoność (proxy Phi) za pomocą kompresji zlib.
    Zabezpieczenie: dla krótkich tekstów (< MIN_TEXT_LENGTH) stosuje fallback.
    """
    if not text:
        return 0.0
    
    raw_bytes = text.encode('utf-8')
    
    # Guard: zlib dodaje ~11 bajtów nagłówka, co zaburza wynik dla krótkich tekstów
    if len(raw_bytes) < MIN_TEXT_LENGTH:
        # Fallback: normalizowana długość (krótkie = niskie Phi)
        return len(raw_bytes) / (MIN_TEXT_LENGTH * 2)
    
    compressed_bytes = zlib.compress(raw_bytes)
    ratio = len(compressed_bytes) / len(raw_bytes)
    
    # Clamp do [0, 1] — ratio > 1 jest możliwe dla bardzo krótkich/losowych danych
    return min(ratio, 1.0)


def calculate_novelty(new_text_vec, existing_vectors):
    """
    Mierzy nowość informacji względem istniejącej wiedzy.
    Wysoka wartość = wiedza jest NOWA (różna od tego co już wiemy).
    """
    if not existing_vectors:
        return 0.5  # brak punktu odniesienia
    
    # Średnie podobieństwo do istniejącej wiedzy
    similarities = []
    for vec in existing_vectors:
        dot = sum(a * b for a, b in zip(new_text_vec, vec))
        mag = math.sqrt(sum(a*a for a in new_text_vec)) * math.sqrt(sum(b*b for b in vec))
        sim = dot / mag if mag else 0.0
        similarities.append(sim)
    
    avg_similarity = sum(similarities) / len(similarities)
    
    # Im MNIEJ podobna do istniejącej wiedzy, tym WYŻSZA nowość
    return 1.0 - avg_similarity


def U(response, context_score=0.5, graph_density=0.1):
    """
    Oblicza wskaźnik U (Unity):
    alpha * Phi (złożoność) + beta * Globalness (kontekst) + gamma * Connectivity (graf)
    """
    alpha, beta, gamma = 0.5, 0.3, 0.2
    
    phi = calculate_complexity(response)
    
    u_score = (alpha * phi) + (beta * context_score) + (gamma * graph_density)
    
    return round(u_score, 4)
