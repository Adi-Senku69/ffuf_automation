def count_wordlist(path: str) -> int:
    with open(path) as f:
        return sum(1 for line in f if line.strip() and not line.startswith("#"))
