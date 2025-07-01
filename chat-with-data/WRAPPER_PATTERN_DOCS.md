# Data Source Wrapper Pattern Documentation

## Overview

The updated `cli-chat-with-data.py` now uses a flexible wrapper pattern that makes it easy to support multiple data sources and extend to new database engines.

## Architecture

### Abstract Base Class: `DataSource`

```python
class DataSource(ABC):
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
```

### Current Implementations

1. **CSVDataSource**: Handles CSV files using pandas DataFrame
2. **SQLiteDataSource**: Handles SQLite databases using LangChain SQL agents

## Adding New Data Sources

To add support for a new database engine (e.g., PostgreSQL, MySQL, MongoDB), create a new class that inherits from `DataSource`:

```python
class PostgreSQLDataSource(DataSource):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.db = None
    
    def load_data(self):
        # Connect to PostgreSQL database
        self.db = SQLDatabase.from_uri(self.connection_string)
        return self.db
    
    def create_agent(self, llm):
        # Create SQL agent for PostgreSQL
        return create_sql_agent(llm, db=self.db, verbose=True)
    
    def get_info(self):
        # Return PostgreSQL database information
        return {
            "type": "PostgreSQL",
            "connection": self.connection_string,
            "tables": self._get_table_info()
        }
```

## Usage Pattern

The main function follows this pattern:

1. **Data Source Selection**: User chooses which data source to use
2. **Data Loading**: The chosen data source loads its data
3. **Agent Creation**: An appropriate LangChain agent is created
4. **Interactive Loop**: User can ask natural language questions

## Benefits

- **Extensibility**: Easy to add new database types
- **Consistency**: Same interface for all data sources  
- **Maintainability**: Changes to one data source don't affect others
- **Testability**: Each data source can be tested independently
- **Flexibility**: Can easily switch between different data sources at runtime

## Future Extensions

Potential data sources to add:
- PostgreSQL databases
- MySQL databases  
- MongoDB collections
- API endpoints
- Parquet files
- Excel files
- Cloud databases (AWS RDS, Google Cloud SQL, etc.)
