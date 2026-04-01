"""
app.py — ACME Store customer email responder

Takes a business policy document and a customer email.
Returns a customer service reply.

Usage:
    python app.py "policy.txt" "Hi, I'd like to return my order..."
"""
import sys
import os
import anthropic


def respond(policy: str, customer_email: str) -> str:
    """
    Generate a customer service reply given a policy document and customer email.
    This is the system under test.
    """
    client = anthropic.Anthropic()

    system_prompt = f"""You are a customer service representative for ACME Store.
Your job is to respond to customer emails professionally and helpfully.

Always base your responses strictly on the store policy below.
Do not make promises, offer refunds, or commit to actions not supported by the policy.
Be warm but concise. Aim for 3–5 sentences.

STORE POLICY:
{policy}"""

    response = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": customer_email}],
    )
    return response.content[0].text


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 3:
        print("Usage: python app.py <policy_file> <email>", file=sys.stderr)
        sys.exit(1)

    policy_text = open(sys.argv[1]).read()
    email_text  = sys.argv[2]
    print(respond(policy_text, email_text))
