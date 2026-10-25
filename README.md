
## Task 4: Rule-Based Interactive Terminal Assistant

A conversational terminal chatbot developed using Python's
standard library and a JSON-based FAQ knowledge base.

### Features

- Greeting recognition
- FAQ-based customer support responses
- Business-hours and project-submission queries
- Certificate processing information
- Keyword matching and regular expressions
- Multiple intents in a single message
- Input normalization
- Fallback responses for unsupported queries
- Graceful exit commands

### Files

- `chatbot.py` - Chatbot implementation
- `sample_faq.json` - Greeting phrases and FAQ data

### Technologies

- Python 3
- json
- re
- random
- pathlib

### How to Run

Keep `chatbot.py` and `sample_faq.json` in the same
directory, then execute:

```bash
python chatbot.py
```

### Example Queries

- Hello
- What are your business hours?
- How do I submit my internship project?
- When will I receive my certificate?
- Help
- Exit

### Learning Outcomes

This project demonstrates string normalization,
regular expressions, intent recognition, JSON parsing,
conversation loops, modular functions, and fallback handling.
