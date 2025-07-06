# Core Components of ResearchGPT

This document explains the main components and their roles in the ResearchGPT application, which is a web-based AI agent that searches the web for information and provides summarized answers based on user queries.

## 1. LangGraph for State Management

**Purpose**: Orchestrates the research workflow as a state machine.

**Implementation**: 
- Defines a `ResearchState` TypedDict with fields for query, sources, web results, summarized results, and response
- Creates a directed graph with three nodes: `search_web` → `summarize_results` → `generate_response`
- Manages state transitions between different stages of the research process

**Key Features**:
- State persistence across workflow steps
- Input/Output type definitions (`ResearchStateInput`, `ResearchStateOutput`)
- Automatic state propagation between nodes

```python
builder = StateGraph(
    ResearchState,
    input=ResearchStateInput,
    output=ResearchStateOutput
)
```

## 2. LangChain for Model and Prompt Management

**Purpose**: Provides abstractions for working with language models and structured prompts.

**Components Used**:
- `ChatPromptTemplate`: Creates reusable prompt templates for summarization and response generation
- `ChatOllama`: Interface to the Ollama-hosted Deepseek model
- Prompt chaining with the pipe operator (`|`) for streamlined processing

**Key Templates**:
- `summary_template`: Summarizes web content relevant to the query
- `generate_response_template`: Generates final responses based on summarized content

```python
prompt = ChatPromptTemplate.from_template(summary_template)
chain = prompt | model
```

## 3. Tavily for Web Search

**Purpose**: Performs web searches to gather relevant information for user queries.

**Configuration**:
- `max_results=3`: Limits search results to 3 sources for focused research
- Returns structured results with URLs and content
- Integrates seamlessly with the LangGraph workflow

**Usage**:
```python
search = TavilySearch(max_results=3)
search_results = search.invoke(state["query"])
```

## 4. Streamlit for Web Interface

**Purpose**: Creates an interactive web application for user interaction.

**Features**:
- Simple text input for research queries
- Real-time processing and display of results
- Automatic source citation display
- Clean, minimal user interface

**Interface Elements**:
- Title: "ResearchGPT"
- Text input field for queries
- Response display area
- Sources section with clickable links

## 5. dotenv for Environment Variable Management

**Purpose**: Securely manages API keys and configuration settings.

**Implementation**:
- Loads environment variables from `.env` file
- Keeps sensitive data (like Tavily API key) out of source code
- Follows security best practices for API key management

**Usage**:
```python
load_dotenv()  # Loads .env file automatically
```

## 6. Ollama for the Deepseek Model

**Purpose**: Provides local AI model inference capabilities.

**Model**: `deepseek-r1:8b` - A reasoning-capable language model
- Runs locally for privacy and control
- Handles both summarization and response generation tasks
- Supports advanced reasoning with `<think>` tags (which are cleaned from output)

**Integration**:
```python
model = ChatOllama(model="deepseek-r1:8b")
```

## 7. Python's venv for Virtual Environment Management

**Purpose**: Isolates project dependencies and ensures consistent runtime environments.

**Benefits**:
- Prevents dependency conflicts
- Ensures reproducible installations
- Easy activation/deactivation workflow

**Commands**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Activate
deactivate                 # Deactivate
```

## Workflow Architecture

The application follows a three-stage pipeline:

1. **Search Stage** (`search_web`): Uses Tavily to find relevant web content
2. **Summarization Stage** (`summarize_results`): Uses Deepseek to summarize each source
3. **Response Generation Stage** (`generate_response`): Creates final answer from summaries

## Data Flow

```
User Query → Web Search → Content Retrieval → Summarization → Response Generation → Display
```

Each stage maintains state through the LangGraph framework, ensuring data consistency and enabling complex multi-step reasoning workflows.

## Key Design Patterns

- **State Management**: Centralized state handling through TypedDict classes
- **Pipeline Architecture**: Sequential processing stages with clear boundaries
- **Template-based Prompting**: Reusable prompt templates for consistency
- **Error Handling**: Robust content processing with fallback mechanisms
- **Clean Output**: Automatic removal of model reasoning artifacts (`<think>` tags)

This architecture provides a scalable, maintainable foundation for AI-powered research applications while keeping the codebase simple and focused.
