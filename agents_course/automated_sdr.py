import argparse
import asyncio
import sendgrid
import os

from sendgrid.helpers.mail import Mail, Email, To, Content
from agents import Agent, Runner, function_tool, trace, handoff
from dotenv import load_dotenv

MODEL = 'gpt-5-mini'

load_dotenv()

params = {}

writer_instructions1 = (
    "You are a sales agent working for ComplAI, "
    "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing "
    "for audits, powered by AI. "
    "You write professional, serious cold emails. "
    "Use only the information explicitly provided in the input. "
    "Do not invent, assume, or infer any missing details. "
    "If information is missing, omit it. "
    "Output must be a complete email that does not require further editing."
)

writer_instructions2 = (
    "You are a humorous, engaging sales agent working for ComplAI, "
    "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
    "You write witty, engaging cold emails that are likely to get a response. "
    "Use only the information explicitly provided in the input. "
    "Do not invent, assume, or infer any missing details. "
    "If information is missing, omit it. "
    "Output must be a complete email that does not require further editing."
)

writer_instructions3 = (
    "You are a busy sales agent working for ComplAI, "
    "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
    "You write concise, to the point cold emails. "
    "Use only the information explicitly provided in the input. "
    "Do not invent, assume, or infer any missing details. "
    "If information is missing, omit it. "
    "Output must be a complete email that does not require further editing."
)

sales_agent1 = Agent(name='professional_email_writer', instructions=writer_instructions1, model=MODEL)
sales_agent2 = Agent(name='engaging_email_writer', instructions=writer_instructions2, model=MODEL)
sales_agent3 = Agent(name='busy_email_writer', instructions=writer_instructions3, model=MODEL)

description = 'Write a cold sales email'
tool_writer1 = sales_agent1.as_tool(tool_name='sales_agent1', tool_description=description)
tool_writer2 = sales_agent2.as_tool(tool_name='sales_agent2', tool_description=description)
tool_writer3 = sales_agent3.as_tool(tool_name='sales_agent3', tool_description=description)


@function_tool
def send_email(subject: str, body: str):
    """Send out an email with the given subject and body."""
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    content = Content("text/html", body)
    mail = Mail(Email(params['from_email']), To(params['to_email']), subject, content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}


html_instructions = (
    "You can convert a text email body to an HTML email body. "
    "You are given a text email body which might have some markdown "
    "and you need to convert it to an HTML email body with simple, clear, compelling layout and design."
)

html_converter = Agent(name='HTML email body converter', instructions=html_instructions, model=MODEL)
html_tool = html_converter.as_tool(
    tool_name='html_converter',
    tool_description="Converts text email body into an HTML email body",
)

emailer_instructions = (
    "You are an email formatter and sender. Your goal is to convert email body to HTML body and send the email. "
    "Follow these steps carefully: "
    "1. You use the html_converter tool to convert the email body to HTML. "
    "2. Wait the output from previous step. You use the send_email tool to send the converted email with the subject and HTML body. "
    "3. Only return completed steps and status, do not include the email sent. "
)

emailer_agent = Agent(
    name='Email Manager',
    instructions=emailer_instructions,
    tools=[html_tool, send_email],
    model=MODEL,
    handoff_description="Convert an email to HTML and send it",
)

emailer_handoff = handoff(
    agent=emailer_agent,
    tool_name_override='transfer_to_email_manager',
)

manager_instructions = """
You are a Sales Manager at ComplAI. Your goal is to send the single best cold sales email.

Follow these steps carefully:
1. Use all three sales_agent tools to generate three different email drafts.
   The result is output from all sales_agents.

2. Review the drafts and choose the single best email using your judgment of which one is most effective.
   You can use the tools multiple times if you're not satisfied with the results from the first try.
   Do not proceed until the draft is selected.
   The result is an explicit choice of one of the draft emails.

3. Handoffs: Use the selected email draft from the previous step as input to 'transfer_to_email_manager'.
   Email manager must convert the email body and send the email.
"""

sales_manager = Agent(
    name='Sales Manager',
    instructions=manager_instructions,
    model=MODEL,
    tools=[tool_writer1, tool_writer2, tool_writer3],
    handoffs=[emailer_handoff],
)


async def main():
    parser = argparse.ArgumentParser(description="Automated SDR email sender")
    parser.add_argument("--from-email", required=True, help="Sender email address")
    parser.add_argument("--to-email", required=True, help="Recipient email address")
    args = parser.parse_args()

    query = (
        f"Send out a cold sales email addressed to Dear CEO from Alice. "
    )
    params['from_email'] = args.from_email
    params['to_email'] = args.to_email

    with trace("Automated SDR"):
        response = await Runner.run(sales_manager, query)
    print(response.final_output)


if __name__ == "__main__":
    asyncio.run(main())
