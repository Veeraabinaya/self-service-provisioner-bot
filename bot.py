import discord
from discord import app_commands
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

from terraform_generator.generator import generate

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
POLICY_URL = os.getenv("POLICY_ENGINE_URL", "http://localhost:8001/validate")

ALLOWED_TYPES = ["docker", "aws", "ec2"]
ALLOWED_ENVS = ["dev", "test", "qa", "staging"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def create_session_with_retries() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def validate_inputs(type: str, env: str) -> str | None:
    if not type or not type.strip():
        return "❌ **Invalid input:** `type` cannot be empty."
    if not env or not env.strip():
        return "❌ **Invalid input:** `env` cannot be empty."
    if type.lower() not in ALLOWED_TYPES:
        return (
            f"❌ **Invalid type:** `{type}` is not supported.\n"
            f"Allowed types: `{', '.join(ALLOWED_TYPES)}`"
        )
    if env.lower() not in ALLOWED_ENVS:
        return (
            f"❌ **Invalid environment:** `{env}` is not supported.\n"
            f"Allowed environments: `{', '.join(ALLOWED_ENVS)}`"
        )
    return None


@tree.command(name="provision", description="Request a new environment")
@app_commands.describe(
    type="Environment type (docker, aws, ec2)",
    env="Environment name (dev, test, qa, staging)",
)
async def provision(interaction: discord.Interaction, type: str, env: str):
    await interaction.response.defer()

    error = validate_inputs(type, env)
    if error:
        await interaction.followup.send(error)
        return

    type = type.lower().strip()
    env = env.lower().strip()
    user = interaction.user.name

    session = create_session_with_retries()
    try:
        resp = session.post(
            POLICY_URL,
            json={"type": type, "env": env, "user": user},
            timeout=10,
        )
        resp.raise_for_status()
        result = resp.json()

        if result.get("allowed"):
            try:
                template = generate(type)
                template_block = f"\n\n📄 **Generated IaC Template:**\n```yaml\n{template}\n```"
            except Exception:
                template_block = "\n\n⚠️ Template generation failed."

            msg = (
                f"✅ **Provision Request Approved!**\n"
                f"👤 User: `{user}`\n"
                f"🖥️ Type: `{type}` | 🌍 Env: `{env}`\n\n"
                f"📋 Policy: {result.get('message', 'Allowed by policy.')}"
                f"{template_block}"
            )
        else:
            msg = (
                f"🚫 **Provision Request Denied**\n"
                f"👤 User: `{user}`\n"
                f"🖥️ Type: `{type}` | 🌍 Env: `{env}`\n\n"
                f"📋 Reason: {result.get('message', 'Denied by policy.')}"
            )

    except requests.exceptions.ConnectionError:
        msg = (
            f"⚠️ **Policy Engine Unavailable**\n"
            f"Could not connect to the policy engine after 3 retries.\n"
            f"Please try again later or contact an admin."
        )
    except requests.exceptions.Timeout:
        msg = (
            f"⏱️ **Request Timed Out**\n"
            f"The policy engine took too long to respond. Please try again."
        )
    except requests.exceptions.HTTPError as e:
        msg = (
            f"❌ **Policy Engine Error**\n"
            f"Server returned an error: `{e.response.status_code}`\n"
            f"Please contact an admin."
        )
    except Exception as e:
        msg = (
            f"❌ **Unexpected Error**\n"
            f"`{str(e)}`\n"
            f"Please contact an admin."
        )

    await interaction.followup.send(msg)


@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot is online as {client.user}")


client.run(TOKEN)