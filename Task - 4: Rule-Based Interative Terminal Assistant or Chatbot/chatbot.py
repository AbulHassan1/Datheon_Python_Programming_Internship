"""
Rule-Based Interactive Terminal Assistant
-----------------------------------------
A keyword/regex-driven support chatbot that loads its knowledge base from a
JSON dataset (greetings + FAQs), recognises multiple intents in one message,
falls back gracefully on low-confidence queries, and exits cleanly.

Conversation state: GREETING -> ACTIVE (intent identification + resolution) -> EXIT

Usage:
    python chatbot.py                 # uses sample_faq.json
    python chatbot.py my_faq.json     # custom dataset
"""

import json
import re
import sys
from difflib import SequenceMatcher

DEFAULT_DATA_FILE = "sample_faq.json"
BOT_NAME = "Datheon Assistant"

CONFIDENCE_THRESHOLD = 0.45   # minimum score to answer an FAQ
MULTI_INTENT_MARGIN = 0.15    # extra FAQs within this margin of the best are answered too

EXIT_PATTERN = re.compile(r"\b(bye|goodbye|exit|quit|see you|that'?s all)\b")
THANKS_PATTERN = re.compile(r"\b(thanks|thank you|thx|cheers)\b")
HELP_PATTERN = re.compile(r"\b(help|topics|what can you do|menu)\b")

STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "do", "does", "did", "i", "you", "your",
    "my", "me", "we", "our", "to", "of", "for", "on", "in", "at", "and", "or",
    "can", "will", "would", "how", "what", "when", "where", "which", "who",
    "please", "tell", "about", "it", "this", "that", "be", "get", "there",
}

# Small synonym map so common rephrasings hit the right intent
SYNONYMS = {
    "open": "hour", "opening": "hour", "close": "hour", "closing": "hour",
    "time": "hour", "timing": "hour", "schedule": "hour",
    "operate": "operation", "working": "operation",
    "upload": "submit", "send": "submit", "turn": "submit",
    "certification": "certificate", "receive": "receiv", "got": "receiv",
}

# States
GREETING, ACTIVE, EXIT = "GREETING", "ACTIVE", "EXIT"


# ----------------------------- data loading ----------------------------- #
def load_data(path: str) -> dict:
    """Load the JSON knowledge base, exiting with a clear message on failure."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("greetings", [])
        data.setdefault("faqs", [])
        return data
    except FileNotFoundError:
        sys.exit(f"Error: dataset '{path}' not found.")
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: '{path}' is not valid JSON ({exc}).")


# --------------------------- text normalisation -------------------------- #
def normalize(text: str) -> str:
    """Lowercase, strip, remove punctuation, collapse whitespace."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def stem(word: str) -> str:
    """Very light stemming so 'hours'/'hour', 'submitting'/'submit' match."""
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def keywords(text: str) -> set:
    """Regex keyword extraction: stemmed non-stopword tokens."""
    tokens = re.findall(r"[a-z0-9']+", normalize(text))
    return {stem(SYNONYMS.get(t, t)) for t in tokens if t not in STOPWORDS}


# ------------------------------ intent logic ----------------------------- #
def score_faq(user_input: str, faq: dict) -> float:
    """
    Confidence score in [0, 1] combining:
      - keyword overlap with the FAQ question (70%)
      - overall string similarity (30%)
    """
    user_kw = keywords(user_input)
    faq_kw = keywords(faq["question"])
    if not user_kw or not faq_kw:
        return 0.0
    # Divide by the smaller keyword set so short queries ('how do I submit?') can still match
    overlap = len(user_kw & faq_kw) / min(len(faq_kw), len(user_kw))
    similarity = SequenceMatcher(
        None, normalize(user_input), normalize(faq["question"])
    ).ratio()
    return 0.7 * overlap + 0.3 * similarity


def _confident(user_input: str, faqs: list) -> list:
    """Confident matches for a single piece of text, best first."""
    scored = sorted(((score_faq(user_input, f), f) for f in faqs),
                    key=lambda pair: pair[0], reverse=True)
    if not scored or scored[0][0] < CONFIDENCE_THRESHOLD:
        return []
    best = scored[0][0]
    return [(s, f) for s, f in scored
            if s >= CONFIDENCE_THRESHOLD and best - s <= MULTI_INTENT_MARGIN]


def match_faqs(user_input: str, faqs: list) -> list:
    """
    Multi-intent matching: score the whole message, then each clause
    (split on 'and', commas, '?', ';') so 'X and Y?' answers both.
    Returns [(score, faq)] deduplicated, best first.
    """
    pieces = [user_input]
    clauses = [c for c in re.split(r"\band\b|[,;?&]|\balso\b", user_input.lower())
               if len(keywords(c)) >= 1]
    if len(clauses) > 1:
        pieces += clauses

    found = {}
    for piece in pieces:
        for score, faq in _confident(piece, faqs):
            key = faq["question"]
            found[key] = max(found.get(key, (0, faq))[0], score), faq
    return sorted(found.values(), key=lambda pair: pair[0], reverse=True)


def is_greeting(user_input: str, greetings: list) -> bool:
    words = set(normalize(user_input).split())
    text = normalize(user_input)
    return any(
        (g in words) if " " not in g else (g in text)
        for g in map(normalize, greetings)
    )


# ------------------------------- the bot --------------------------------- #
class ChatBot:
    def __init__(self, data: dict):
        self.greetings = data["greetings"]
        self.faqs = data["faqs"]
        self.state = GREETING
        self.fallback_count = 0
        self.last_topic = None  # simple context memory

    def topics(self) -> str:
        return "\n".join(f"  - {f['question']}" for f in self.faqs)

    def respond(self, raw: str) -> str:
        text = normalize(raw)

        if not text:
            return "I didn't catch that. Could you type your question?"

        # Exit command works in any state
        if EXIT_PATTERN.search(text):
            self.state = EXIT
            return "Goodbye! Thanks for chatting. Have a great day!"

        # State: GREETING
        if is_greeting(text, self.greetings) and self.state == GREETING:
            self.state = ACTIVE
            reply = "Hello! How can I help you today?"
            # Greeting + question in one message (e.g. "hi, what are your hours?")
            matches = match_faqs(raw, self.faqs)
            if matches:
                return reply + "\n\n" + self.resolve(matches)
            return reply + " (Type 'help' to see what I can answer.)"

        self.state = ACTIVE  # any non-greeting first message also activates

        if is_greeting(text, self.greetings) and len(text.split()) <= 3:
            return "Hi again! What would you like to know?"

        if THANKS_PATTERN.search(text):
            return "You're welcome! Anything else I can help with?"

        if HELP_PATTERN.search(text):
            return "Here are the topics I can help with:\n" + self.topics()

        # State: ACTIVE -> intent identification -> resolution
        matches = match_faqs(raw, self.faqs)
        if matches:
            self.fallback_count = 0
            return self.resolve(matches)
        return self.fallback()

    def resolve(self, matches: list) -> str:
        """Build the answer; combine answers if multiple intents matched."""
        self.last_topic = matches[0][1]["question"]
        if len(matches) == 1:
            return matches[0][1]["answer"]
        return "\n".join(f"* {f['answer']}" for _, f in matches)

    def fallback(self) -> str:
        """Graceful low-confidence handling; escalates help after repeats."""
        self.fallback_count += 1
        if self.fallback_count == 1:
            return ("Sorry, I'm not sure I understood that. "
                    "Could you rephrase your question?")
        return ("I still couldn't find an answer. Here's what I can help with:\n"
                + self.topics())


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA_FILE
    bot = ChatBot(load_data(path))

    print("=" * 50)
    print(f"  {BOT_NAME}  (type 'bye', 'exit' or 'quit' to leave)")
    print("=" * 50)

    while bot.state != EXIT:
        try:
            user_input = input("\nYou: ")
        except (EOFError, KeyboardInterrupt):
            print(f"\n{BOT_NAME}: Goodbye!")
            break
        print(f"{BOT_NAME}: {bot.respond(user_input)}")


if __name__ == "__main__":
    main()