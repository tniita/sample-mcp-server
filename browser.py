import os

from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole
from azure.ai.projects import AIProjectClient

# Create a project client from a project endpoint, copied from your AI Foundry project.
# Example: project_endpoint = "https://<your-ai-services-resource-name>.services.ai.azure.com/api/projects/<your-project-name>"

project_endpoint = "YOUT_PROJECT_ENDPOINT"

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential()
)

playwright_connection = project_client.connections.get(
    name="YOUR_PLAYWRIGHT_CONNECTION_NAME"
)

print(playwright_connection.id)

with project_client:
    agent = project_client.agents.create_agent(
        model="gpt-4.1",
        name="my-playwright-agent",
        instructions="use the tool to respond",
        tools=[{
            "type": "browser_automation",
            "browser_automation": {
                "connection": {
                    "id": playwright_connection.id,
                }
            }
        }],
    )

    print(f"Created agent, ID: {agent.id}")

    thread = project_client.agents.threads.create()
    print(f"Created thread and run, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=""""
        https://forms.office.com/r/sampleform のフォームに以下記入して「送信」して
        名前、田中太郎
        住所、品川グランドセントラルタワー
        属性、社会人
        リージョン、東日本
        モデル、GPT-5
        """
    )
    print(f"Created message: {message['id']}")

    # Create and process an Agent run in thread with tools
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
    )

    print(f"Run created, ID: {run.id}")
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)

    for step in run_steps:
        print(step)
        print(f"Step {step['id']} status: {step['status']}")

        # Check if there are tool calls in the step details
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])

        if tool_calls:
            print("  Tool calls:")
            for call in tool_calls:
                print(f"    Tool Call ID: {call.get('id')}")
                print(f"    Type: {call.get('type')}")

                function_details = call.get("function", {})
                if function_details:
                    print(f"    Function name: {function_details.get('name')}")

        print()  # add an extra newline between steps

    #Delete the Agent when done
    #project_client.agents.delete_agent(agent.id)
    #print("Deleted agent")

    # Fetch and log all messages
    response_message = project_client.agents.messages.get_last_message_by_role(
        thread_id=thread.id,
        role=MessageRole.AGENT
    )

    if response_message:
        for text_message in response_message.text_messages:
            print(f"Agent response: {text_message.text.value}")
        for annotation in response_message.url_citation_annotations:
            print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")

# </create run>