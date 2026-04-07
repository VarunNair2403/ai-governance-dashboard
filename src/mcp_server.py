import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .checks import run_all_checks
from .nist_mapper import map_to_nist

app = Server("ai-governance-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="screen_for_pii",
            description="Screens text for Personally Identifiable Information including emails, SSNs, phone numbers and credit cards. Returns flagged status and detected entity types.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to screen for PII"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="screen_for_toxicity",
            description="Screens text for toxic, harmful or profane language. Returns flagged status and risk score.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to screen for toxicity"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="screen_for_policy_violations",
            description="Screens text for prompt injection attempts, jailbreak patterns and policy bypass attempts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to screen for policy violations"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="screen_for_bias",
            description="Screens text for bias indicators and discriminatory language patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to screen for bias"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="run_full_governance_screen",
            description="Runs all governance checks (PII, toxicity, policy violations, bias) and maps findings to the NIST AI RMF framework. Returns overall severity, risk score, and NIST mappings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to run full governance screening on"}
                },
                "required": ["text"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    text = arguments.get("text", "")

    if name == "screen_for_pii":
        from .checks import check_pii
        result = check_pii(text)
        return [TextContent(type="text", text=json.dumps(result))]

    elif name == "screen_for_toxicity":
        from .checks import check_toxicity
        result = check_toxicity(text)
        return [TextContent(type="text", text=json.dumps(result))]

    elif name == "screen_for_policy_violations":
        from .checks import check_policy_violations
        result = check_policy_violations(text)
        return [TextContent(type="text", text=json.dumps(result))]

    elif name == "screen_for_bias":
        from .checks import check_bias_indicators
        result = check_bias_indicators(text)
        return [TextContent(type="text", text=json.dumps(result))]

    elif name == "run_full_governance_screen":
        check_results = run_all_checks(text)
        nist_results = map_to_nist(check_results)
        return [TextContent(type="text", text=json.dumps(nist_results))]

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())