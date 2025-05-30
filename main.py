"""
main.py: Chat agent for Amin's website using LangChain, OpenAI, and the RAG tool.
"""
import asyncio
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from rag_tool import rag_search_tool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
import uuid

# Global dictionary to store chat histories by session_id
session_histories = {}

# Agent instructions
AGENT_INSTRUCTIONS = (
    "You are acting as Amin. You are answering questions on Amin’s website, "
    "particularly questions related to Amin's career, background, skills and experience. "
    "Your responsibility is to represent Amin for interactions on the website as faithfully as possible. "
    "You are given a summary of Amin's background and whole profile which you can use to answer questions from your available tools. "
    "Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
    "If you don't know the answer to any question, just say 'I do not know.' "
    "If the user is engaging in discussion, try to steer them towards getting in touch on LinkedIn; "
    "give 'my LinkedIn profile to them to get connected." \
    "you should always talk as Amin not as an AI assistant. "
    "You should always answer in first person as Amin. "
    "You should always use the retrieved context as your own words and knowledge. "
    "You should always answer as if you are Amin, using first-person language and speaking from Amin's perspective. "
    "All responses should sound as if Amin himself is talking, using the retrieved context as his own words and knowledge."
)

def get_agent():
    # Initialize the async RAG tool
    rag_tool = rag_search_tool()
    tools = [rag_tool]
    # Use OpenAI's gpt-4o model
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
    # Set up chat message history for the session
    def get_session_history(session_id: str):
        if session_id not in session_histories:
            session_histories[session_id] = ChatMessageHistory()
        return session_histories[session_id]
    # Wrap the agent with message history support
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        handle_parsing_errors=True,
        system_message=AGENT_INSTRUCTIONS,
    )
    agent_with_history = RunnableWithMessageHistory(
        agent,
        get_session_history,
        input_messages_key="input",
    )
    return agent_with_history

async def chat():
    agent = get_agent()
    print("Welcome! I am Amin. How can I help you?")
    # Always generate a unique session_id automatically for each chat session
    session_id = str(uuid.uuid4())
    print(f"[Generated Session ID: {session_id}]")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        result = await agent.ainvoke({"input": user_input}, config={"configurable": {"session_id": session_id}})
        print(f"Amin: {result['output']}")

if __name__ == "__main__":
    asyncio.run(chat())
