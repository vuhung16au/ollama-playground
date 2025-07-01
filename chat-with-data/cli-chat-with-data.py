# Import necessary libraries
import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
import os
import sqlite3
from abc import ABC, abstractmethod
from typing import Union, Any

class DataSource(ABC):
    """Abstract base class for different data sources."""
    
    @abstractmethod
    def load_data(self) -> Union[pd.DataFrame, SQLDatabase]:
        """Load data from the source."""
        pass
    
    @abstractmethod
    def create_agent(self, llm) -> Any:
        """Create an appropriate agent for this data source."""
        pass
    
    @abstractmethod
    def get_info(self) -> Union[dict, str]:
        """Get information about the data source."""
        pass


class CSVDataSource(DataSource):
    """Data source for CSV files."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
    
    def load_data(self):
        """Load CSV data into a pandas DataFrame."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"The file '{self.file_path}' was not found.")
        
        self.df = pd.read_csv(self.file_path)
        return self.df
    
    def create_agent(self, llm):
        """Create a pandas DataFrame agent."""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        return create_pandas_dataframe_agent(
            llm, 
            self.df, 
            verbose=True, 
            allow_dangerous_code=True, 
            handle_parsing_errors=True
        )
    
    def get_info(self):
        """Get information about the CSV data."""
        if self.df is None:
            return "CSV data not loaded."
        
        return {
            "type": "CSV",
            "file_path": self.file_path,
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": list(self.df.columns)
        }


class SQLiteDataSource(DataSource):
    """Data source for SQLite databases."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = None
        self.tables_info = None
    
    def load_data(self):
        """Load SQLite database connection."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"The database '{self.db_path}' was not found.")
        
        # Create SQLDatabase instance for LangChain
        self.db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")
        
        # Get table information
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        self.tables_info = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            
            self.tables_info[table_name] = {
                "columns": [col[1] for col in columns],
                "column_details": columns,
                "row_count": row_count
            }
        
        conn.close()
        return self.db
    
    def create_agent(self, llm):
        """Create a SQL agent."""
        if self.db is None:
            raise ValueError("Database not loaded. Call load_data() first.")
        
        return create_sql_agent(
            llm,
            db=self.db,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def get_info(self):
        """Get information about the SQLite database."""
        if self.tables_info is None:
            return "Database not loaded."
        
        return {
            "type": "SQLite",
            "db_path": self.db_path,
            "tables": self.tables_info
        }


def choose_data_source():
    """Interactive function to choose between CSV and SQLite data sources."""
    print("📊 Available Data Sources:")
    print("1. CSV File (OnlineRetail.csv)")
    print("2. SQLite Database (OnlineRetail.db)")
    print("-" * 40)
    
    while True:
        choice = input("Please choose a data source (1 or 2): ").strip()
        
        if choice == "1":
            return CSVDataSource("data/OnlineRetail.csv")
        elif choice == "2":
            return SQLiteDataSource("data/OnlineRetail.db")
        else:
            print("Invalid choice. Please enter 1 or 2.")


def chat_with_data(data_source: DataSource, model_name: str = "mistral"):
    """
    Allows natural language querying of data using a local LLM (Ollama).

    Args:
        data_source (DataSource): The data source to query (CSV or SQLite).
        model_name (str): The name of the Ollama model to use (e.g., "mistral").
    """
    print(f"🚀 Starting Data Chat with Ollama ({model_name}) 🚀")
    print("-" * 50)

    # 1. Load the data source
    try:
        data_source.load_data()
        info = data_source.get_info()
        
        if isinstance(info, dict):
            if info["type"] == "CSV":
                print(f"Successfully loaded CSV '{info['file_path']}' with {info['rows']} rows and {info['columns']} columns.")
                print("DataFrame columns:", ", ".join(info['column_names']))
            elif info["type"] == "SQLite":
                print(f"Successfully loaded SQLite database '{info['db_path']}'")
                for table_name, table_info in info['tables'].items():
                    print(f"  Table '{table_name}': {table_info['row_count']} rows, columns: {', '.join(table_info['columns'])}")
        else:
            print(info)
        
        print("-" * 50)
    except Exception as e:
        print(f"Error loading data source: {e}")
        return

    # 2. Initialize the Ollama LLM
    try:
        llm = OllamaLLM(model=model_name)
        print(f"Ollama LLM initialized with model: {model_name}")
    except Exception as e:
        print(f"Error initializing Ollama LLM. Make sure Ollama server is running and '{model_name}' model is pulled. Error: {e}")
        return

    # 3. Create the appropriate agent based on data source type
    try:
        agent = data_source.create_agent(llm)
        print("LangChain Agent created.")
        print("You can now ask questions about your data!")
        print("Type 'exit' or 'quit' to end the session.")
        print("-" * 50)
    except Exception as e:
        print(f"Error creating agent: {e}")
        return

    # 4. Start the interactive questioning loop
    while True:
        question = input("Your question (or 'exit'/'quit'): ")
        if question.lower() in ["exit", "quit"]:
            print("Exiting Data Chat. Goodbye!")
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
    # Choose data source interactively
    try:
        data_source = choose_data_source()
        # Run the chat function
        chat_with_data(data_source, model_name="mistral")
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
