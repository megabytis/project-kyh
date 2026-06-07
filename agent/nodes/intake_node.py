from langchain_core.messages import HumanMessage
from agent.state.agent_state import AgentState


def intake_node(state: AgentState) -> dict:
    # 1. user input
    user_text = state["user_input"]

    # 2. converting user input to proper HumanMessage format
    new_message = [HumanMessage(content=user_text)]

    # 3. getting current messages list
    current_message = state.get("messages", [])

    # 4. appending current messages with user new message
    updated_messages = current_message + new_message

    # 5. returnign the final full message
    return {"messages": updated_messages}
