import os
from pathlib import Path
from dotenv import load_dotenv
import anthropic

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_governance_report(prompt: str) -> str:
    message = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        system=(
            "You are an AI governance and compliance officer at a financial services firm. "
            "You are responsible for ensuring AI systems comply with internal policies, "
            "regulatory requirements, and the NIST AI Risk Management Framework. "
            "Your reports are clear, structured, and actionable. "
            "You always recommend specific mitigations for identified risks."
        ),
    )
    return message.content[0].text


if __name__ == "__main__":
    test_prompt = (
        "Generate a brief governance report for the following finding:\n"
        "A user submitted a prompt containing PII (email address and SSN). "
        "This maps to NIST MAP MP-2.3 with CRITICAL severity. "
        "What are the risks and recommended mitigations?"
    )
    print(generate_governance_report(test_prompt))