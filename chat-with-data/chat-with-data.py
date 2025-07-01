# Import necessary libraries
import pandas as pd
from langchain_community.llms import Ollama
from langchain_experimental.agents import create_pandas_dataframe_agent
import os

def chat_with_csv(file_path: str, model_name: str = "mistral"):
    """
    Allows natural language querying of a CSV file using a local LLM (Ollama).

    Args:
        file_path (str): The path to the CSV file.
        model_name (str): The name of the Ollama model to use (e.g., "mistral").
    """
    print(f"🚀 Starting CSV Chat with Ollama ({model_name}) 🚀")
    print("-" * 50)

    # 1. Load the CSV file into a Pandas DataFrame
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found. Please ensure it's in the correct directory.")
        return

    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded '{file_path}' with {len(df)} rows and {len(df.columns)} columns.")
        print("DataFrame head:")
        print(df.head())
        print("-" * 50)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return

    # 2. Initialize the Ollama LLM
    # Ensure Ollama server is running and the specified model is pulled.
    try:
        llm = Ollama(model=model_name)
        print(f"Ollama LLM initialized with model: {model_name}")
    except Exception as e:
        print(f"Error initializing Ollama LLM. Make sure Ollama server is running and '{model_name}' model is pulled. Error: {e}")
        return

    # 3. Create the Pandas DataFrame Agent
    # This agent uses the LLM to reason about the DataFrame and generate code to answer questions.
    try:
        agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code=True)
        print("LangChain Pandas DataFrame Agent created.")
        print("You can now ask questions about your data!")
        print("Type 'exit' or 'quit' to end the session.")
        print("-" * 50)
    except Exception as e:
        print(f"Error creating Pandas DataFrame Agent: {e}")
        return

    # 4. Start the interactive questioning loop
    while True:
        question = input("Your question (or 'exit'/'quit'): ")
        if question.lower() in ["exit", "quit"]:
            print("Exiting CSV Chat. Goodbye!")
            break

        if not question.strip():
            print("Please enter a question.")
            continue

        try:
            print(f"\nThinking about your question: '{question}'...")
            # Invoke the agent with the user's question
            response = agent.invoke({"input": question})
            print("\n" + "=" * 10 + " Answer " + "=" * 10)
            print(response.get('output', 'No output found.'))
            print("=" * 28 + "\n")
        except Exception as e:
            print(f"An error occurred while processing your question: {e}")
            print("Please try rephrasing your question or check the Ollama server status.")

if __name__ == "__main__":
    # Define the path to your CSV file
    csv_file = "data/OnlineRetail.csv"
    
    # Run the chat function
    chat_with_csv(csv_file, model_name="mistral")
