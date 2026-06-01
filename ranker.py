import json

# --- CONFIGURATION ---
INPUT_FILE = 'candidates.jsonl'
TOP_N = 100

# --- 1. TRAP DETECTION ---
def is_trap(cand):
    signals = cand.get('redrob_signals', {})
    # Agar 100% response rate hai aur connections 5 se kam hai, toh ye trap hai
    if signals.get('recruiter_response_rate', 0) == 1.0 and signals.get('connection_count', 0) < 5:
        return True
    return False

# --- 2. SMART REASONING GENERATOR ---
def generate_reasoning(cand):
    profile = cand.get('profile', {})
    title = profile.get('current_title', 'Professional')
    exp = int(profile.get('years_of_experience', 0))
    summary = str(profile.get('summary', '')).lower()
    
    # Skills mapping
    skills = []
    if 'rag' in summary: skills.append("RAG")
    if 'llm' in summary: skills.append("LLM")
    if 'production' in summary: skills.append("production-systems")
    
    skills_str = f" with expertise in {', '.join(skills)}" if skills else ""
    return f"{title} with {exp}+ years of experience{skills_str}."

# --- 3. SCORING ENGINE ---
def calculate_score(cand):
    if is_trap(cand): return 0
    
    score = 0
    summary = str(cand['profile'].get('summary', '')).lower()
    
    # JD-based relevance
    if 'production' in summary: score += 40
    if 'llm' in summary or 'rag' in summary: score += 30
    if 'recommendation' in summary or 'ranking' in summary: score += 20
    
    # Signal-based relevance
    signals = cand.get('redrob_signals', {})
    score += (signals.get('recruiter_response_rate', 0) * 20)
    
    return score

# --- 4. MAIN PROCESSING ---
def main():
    processed_candidates = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                cand = json.loads(line)
                score = calculate_score(cand)
                if score > 0:
                    cand['final_score'] = score
                    processed_candidates.append(cand)
            except: continue

    # Sort candidates
    top_candidates = sorted(processed_candidates, key=lambda x: x['final_score'], reverse=True)[:TOP_N]

    # Print CSV output
    print("candidate_id,rank,score,reasoning")
    for i, cand in enumerate(top_candidates):
        reason = generate_reasoning(cand)
        # reasoning ko quotes mein wrap karna zaroori hai agar usme commas ho
        print(f"{cand['candidate_id']},{i+1},{cand['final_score']:.4f},\"{reason}\"")

if __name__ == "__main__":
    main()
