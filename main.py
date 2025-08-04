import os
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    function_tool,
    handoff,
    set_tracing_disabled,
    enable_verbose_stdout_logging,
    output_guardrail,
    RunConfig,
)

# === 1. Load environment variables & configure Gemini client ===
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Disable internal tracing for clean console output
set_tracing_disabled(disabled=True)
# Enable verbose logging to view full agent activity
enable_verbose_stdout_logging()

# Configure OpenAI client with Gemini model
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL,
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client,
)

# === 2. Define Pydantic models for agent outputs & shared context ===

class AgentResponse(BaseModel):
    response: str

class SupportContext(BaseModel):
    name: str
    is_premium_user: bool = False
    issue_type: str = None  # Will be filled during triage

# === 3. Output guardrail to block apologetic language (e.g., “sorry”) ===

class ApologyCheckOutput(BaseModel):
    has_apology: bool
    reasoning: str

# Create a dedicated agent to detect apologies in output
apology_guardrail_agent = Agent(
    name="Apology Guardrail",
    model=model,
    instructions=(
        "Inspect the given text and determine if it contains any apology "
        "language (the word 'sorry'). Return JSON with keys:\n"
        "- has_apology: true if any apology found, else false\n"
        "- reasoning: brief justification."
    ),
    output_type=ApologyCheckOutput,
)

@output_guardrail
async def no_apology_guardrail(ctx, agent, output: AgentResponse):
    result = await Runner.run(
        apology_guardrail_agent,
        output.response,
        context=ctx.context
    )
    return {
        "output_info": result.final_output,
        "tripwire_triggered": result.final_output.has_apology,
    }

# === 4. Define reusable tools with conditional availability ===

@function_tool
async def refund(ctx: SupportContext):
    return {"message": f"✅ Refund for {ctx.name} initiated; expect 3–5 business days."}
refund.is_enabled = lambda ctx: ctx.is_premium_user  # Only for premium users

@function_tool
async def restart_service(ctx: SupportContext):
    return {"message": f"✅ Service for {ctx.name} restarted successfully."}
restart_service.is_enabled = lambda ctx: ctx.issue_type == "technical"

@function_tool
async def general_info(ctx: SupportContext):
    return {"message": "🛈 How else can I assist—billing, technical, or general?"}
general_info.is_enabled = lambda ctx: True  # Always enabled

# === 5. Define specialist agents ===

billing_agent = Agent(
    name="Billing Agent",
    model=model,
    instructions="You are the Billing Specialist. Handle refunds, invoices, subscriptions.",
    output_type=AgentResponse,
    output_guardrails=[no_apology_guardrail],
)

technical_agent = Agent(
    name="Technical Agent",
    model=model,
    instructions="You are the Technical Specialist. Assist with restarts, connectivity, errors.",
    output_type=AgentResponse,
    output_guardrails=[no_apology_guardrail],
)

general_agent = Agent(
    name="General Agent",
    model=model,
    instructions="You are the General Support Agent. Answer any general inquiries.",
    output_type=AgentResponse,
    output_guardrails=[no_apology_guardrail],
)

# === 6. Define triage agent for classifying issues and handoff ===

triage_agent = Agent(
    name="Triage Agent",
    model=model,
    instructions=(
        "You are the FIRST POINT OF CONTACT. Classify the user’s issue as billing, technical, "
        "or general, then delegate by calling exactly one of:\n"
        "  • transfer_to_billing_agent\n"
        "  • transfer_to_technical_agent\n"
        "  • transfer_to_general_agent"
    ),
    output_type=AgentResponse,
    output_guardrails=[no_apology_guardrail],
    handoffs=[
        handoff(agent=billing_agent),
        handoff(agent=technical_agent),
        handoff(agent=general_agent),
    ],
)

# === 7. Setup the runner and async I/O interaction loop ===

runner = Runner()

async def main():
    print("🔧 Support System Initialized — type 'exit' to quit.")

    name = input("👤 Enter your name: ").strip() or "User"
    is_premium = input("⭐ Premium user? (y/n): ").lower().startswith("y")

    ctx = SupportContext(name=name, is_premium_user=is_premium)

    while True:
        msg = input("\n💬 How can I help you? ").strip()
        if msg.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break

        ctx.issue_type = None  # Reset before each triage

        print("\n[ 🧠 Triage in progress… ]")

        config = RunConfig(stream=True)

        # Stream output and events including text, tool calls, and handoffs
        result = await runner.run_streamed(
            agent=triage_agent,
            input=msg,
            context=ctx,
            config=config,
            tools=[refund, restart_service, general_info],
        )

        async for event in result.stream_events():
            print(event)  # Display streamed events in real time

if __name__ == "__main__":
    asyncio.run(main())