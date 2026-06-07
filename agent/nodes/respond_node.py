from agent.state.agent_state import AgentState
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from agent.llm.llm_client import llm


def respond_node(state: AgentState) -> dict:
    # 1. preparing the system message conetxt for LLM
    system_prompt = [SystemMessage(content="You are an fitness assistant named KYH")]

    # 2. extracting current messages list
    history = state.get("messages", [])

    # 3. combining current messages with system message
    messages_for_llm = system_prompt + history

    # 4. now getting AI response
    ai_response = llm.invoke(messages_for_llm) # LLM automatically responds as AIMessage format, so no need to convert it as AIMessage :)

    # 5. now updating state by appendign the AIMessage
    updated_messages = history + [ai_response]

    return {"messages": updated_messages, "bot_reply": ai_response.content}
