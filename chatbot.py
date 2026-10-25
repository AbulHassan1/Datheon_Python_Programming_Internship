
"""
Project: Rule-Based Interactive Terminal Assistant
Program: Datheon Python Programming Internship

Features:
- Loads greetings and FAQs from JSON
- Normalizes user input
- Uses regular expressions and keyword rules
- Recognizes multiple intents in one message
- Handles greetings, business hours, project submission,
  certificate processing, and help requests
- Provides fallback responses
- Supports clean exit commands
"""

import json
import random
import re
from pathlib import Path


FAQ_FILE = Path(__file__).resolve().parent / "sample_faq.json"

EXIT_COMMANDS = {"bye", "goodbye", "exit", "quit"}

FALLBACK_RESPONSES = [
    "I'm not sure I understood that. Could you rephrase your question?",
    "I couldn't find a matching answer. Try asking about business hours, "
    "project submission, or certificates.",
    "Sorry, I don't have an answer for that yet. Type 'help' to see "
    "the topics I can handle.",
]

HELP_RESPONSE = (
    "I can help you with these topics:\n"
    "  - Business hours and opening times\n"
    "  - Internship project submission\n"
    "  - Certificate processing time\n"
    "  - Greetings and general help\n"
    "You can type 'bye', 'exit', or 'quit' to leave."
)


def load_knowledge_base():
    """Load greetings and FAQ entries from the JSON file."""
    try:
        with FAQ_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        greetings = data.get("greetings", [])
        faqs = data.get("faqs", [])

        if not isinstance(greetings, list) or not isinstance(faqs, list):
            raise ValueError("Greetings and FAQs must be lists.")

        valid_faqs = []

        for faq in faqs:
            if (
                isinstance(faq, dict)
                and isinstance(faq.get("question"), str)
                and isinstance(faq.get("answer"), str)
            ):
                valid_faqs.append(faq)

        if not valid_faqs:
            raise ValueError("The JSON file contains no valid FAQs.")

        return greetings, valid_faqs

    except FileNotFoundError:
        raise SystemExit(
            f"Knowledge base not found: {FAQ_FILE}\n"
            "Place sample_faq.json beside chatbot.py."
        )

    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid JSON in FAQ file: {error}")

    except ValueError as error:
        raise SystemExit(f"Invalid FAQ data: {error}")


def normalize_text(text):
    """Normalize text for consistent intent matching."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s'-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def matches_any(text, patterns):
    """Return True if any regular expression matches the text."""
    return any(re.search(pattern, text) for pattern in patterns)


def identify_intents(user_text, faqs):
    """
    Identify all supported intents in a message.

    Returns matching intents in a predictable order.
    """
    text = normalize_text(user_text)
    intents = []

    # Greeting intent
    greeting_patterns = [
        r"\bhello\b",
        r"\bhi\b",
        r"\bhey\b",
        r"\bgood morning\b",
        r"\bgood afternoon\b",
        r"\bgood evening\b",
    ]

    if matches_any(text, greeting_patterns):
        intents.append("greeting")

    # Help intent
    if matches_any(text, [
        r"\bhelp\b",
        r"\bwhat can you do\b",
        r"\bwhat can i ask\b",
        r"\bsupported topics\b",
    ]):
        intents.append("help")

    # Business-hours intent
    if matches_any(text, [
        r"\bhours?\b",
        r"\bopening times?\b",
        r"\boperating times?\b",
        r"\bwhen (?:are|do you)\b.{0,30}\bopen\b",
        r"\bwhen do you close\b",
        r"\bworking hours\b",
    ]):
        intents.append("hours")

    # Project-submission intent
    if matches_any(text, [
        r"\bsubmit\b",
        r"\bsubmission\b",
        r"\bturn in\b",
        r"\bhand in\b",
        r"\bupload\b",
        r"\bgithub\b",
        r"\brepository\b",
        r"\bproject link\b",
    ]):
        intents.append("submission")

    # Certificate intent
    if matches_any(text, [
        r"\bcertificate\b",
        r"\bcertificates\b",
        r"\bcredential\b",
        r"\bcredentials\b",
        r"\bhow long\b.{0,40}\b(?:receive|get|issue)\b",
        r"\bwhen\b.{0,40}\b(?:receive|get|issued)\b",
    ]):
        intents.append("certificate")

    # FAQ matching: recognize important words in the FAQ question.
    # This is a fallback for question phrasings not covered above.
    if not intents:
        for faq in faqs:
            question = normalize_text(faq["question"])
            words = re.findall(r"\b[a-z0-9]+\b", question)
            meaningful_words = [
                word for word in words
                if word not in {
                    "what", "are", "is", "how", "do", "i",
                    "your", "the", "a", "an", "my", "when",
                    "will", "can", "you", "to", "of", "and",
                }
            ]

            if meaningful_words and all(
                re.search(rf"\b{re.escape(word)}\b", text)
                for word in meaningful_words
            ):
                question_lower = question

                if "hours of operation" in question_lower:
                    intents.append("hours")
                elif "submit my internship project" in question_lower:
                    intents.append("submission")
                elif "receive my certificate" in question_lower:
                    intents.append("certificate")

    return list(dict.fromkeys(intents))


def find_faq_answer(intent, faqs):
    """Return the answer for an intent from the loaded FAQ data."""
    question_patterns = {
        "hours": [
            r"\bhours of operation\b",
        ],
        "submission": [
            r"\bsubmit my internship project\b",
        ],
        "certificate": [
            r"\breceive my certificate\b",
        ],
    }

    patterns = question_patterns.get(intent, [])

    for faq in faqs:
        question = normalize_text(faq["question"])

        if matches_any(question, patterns):
            return faq["answer"]

    return None


def generate_responses(user_text, intents, greetings, faqs):
    """Generate contextual responses for every recognized intent."""
    responses = []

    if "greeting" in intents:
        greeting = random.choice(greetings) if greetings else "Hello"
        responses.append(
            f"{greeting.capitalize()}! Welcome to the internship assistant."
        )

    if "help" in intents:
        responses.append(HELP_RESPONSE)

    for intent in ("hours", "submission", "certificate"):
        if intent in intents:
            answer = find_faq_answer(intent, faqs)

            if answer:
                responses.append(answer)
            else:
                responses.append(
                    f"I couldn't find the FAQ answer for {intent}."
                )

    if not responses:
        responses.append(random.choice(FALLBACK_RESPONSES))

    return responses


def main():
    """Run the interactive terminal chatbot."""
    greetings, faqs = load_knowledge_base()

    print("=" * 60)
    print("          DATHEON INTERNSHIP TERMINAL ASSISTANT")
    print("=" * 60)
    print("Hello! Ask me about business hours, submissions, or certificates.")
    print("Type 'help' for topics or 'bye' to exit.\n")

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAssistant: Goodbye! Have a great day.")
            break

        if not user_text:
            print("Assistant: Please enter a question.")
            continue

        normalized = normalize_text(user_text)

        # Exit only when the entire message is an exit command.
        if normalized in EXIT_COMMANDS:
            print("Assistant: Goodbye! Thanks for chatting.")
            break

        intents = identify_intents(user_text, faqs)
        responses = generate_responses(
            user_text, intents, greetings, faqs
        )

        for response in responses:
            print(f"Assistant: {response}")

        print()


if __name__ == "__main__":
    main()

