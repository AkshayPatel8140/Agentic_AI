## Setup Instructions

1. **Clone the repository:**
    ```bash
    git clone https://github.com/AkshayPatel8140/Agentic_AI.git
    cd Agentic_AI
    ```

2. **Create and activate a virtual environment:**
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3. **Install dependencies:**
    ```bash
    uv add -r requirements.txt
    ```

4. **Set up environment variables:**
    - Copy `.env.example` to `.env` and fill in your API keys (e.g., `GROQ_API_KEY`).

---

## How to Run Each Section

### 1. **Basic Chatbot (`1-BasicChatbot/`)**

- **File:** `1-BasicChatbot.ipynb`
- **Description:**  
  Demonstrates a basic AI chatbot using LangGraph and Groq LLM.
- **How to run:**
    1. Open the notebook in VS Code or Jupyter:
        ```bash
        jupyter notebook 1-BasicChatbot/1-BasicChatbot.ipynb
        ```
    2. Run the cells in order.

---

### 2. **Tool Use (`2-ToolUse/`)**

- **File:** `tool_use.ipynb`
- **Description:**  
  Shows how to use external tools (like web search) with an LLM agent.
- **How to run:**
    1. Open the notebook:
        ```bash
        jupyter notebook 2-ToolUse/tool_use.ipynb
        ```
    2. Run the cells in order.

---

### 3. **Debugging (`3-Debugging`)**

- **Files:**  
  - `debugging.ipynb` (notebook demo)  
  - `agent.py` (Python script for agent definition)
- **Description:**  
  Demonstrates debugging and agent orchestration with LangGraph.
- **How to run the notebook:**
    ```bash
    jupyter notebook 3-Debugging/debugging.ipynb
    ```
- **How to run with LangGraph Studio:**
    1. Ensure you have `langgraph-cli[inmem]` installed (see requirements.txt).
    2. Start the studio:
        ```bash
        cd 3-Debugging
        langgraph dev
        ```

---

### 4. **Simple Multi AI Agent (`4-SimpleMultiAIAgent`)**

- **Files:**  
  - `simple_multi_AI_agent.ipynb`  
  - `supervise_multi_AI_agent.ipynb`
- **Description:**  
  Demonstrates multi-agent workflows, including supervised agent orchestration.
- **How to run:**
    1. Open the desired notebook:
        ```bash
        jupyter notebook 4-SimpleMultiAIAgent/simple_multi_AI_agent.ipynb
        ```
        or
        ```bash
        jupyter notebook 4-SimpleMultiAIAgent/supervise_multi_AI_agent.ipynb
        ```
    2. Run the cells in order.

---

### 5. **MCP Demo Langchain (`mcpDemoLangchain/`)**

- **Files:**  
  - `client.py`  
  - `mathServer.py`  
  - `weatherServer.py`  
  - Any supporting scripts or modules in the folder.
- **Description:**  
  Demonstrates using LangChain with MCP adapters for fast API calls and advanced agent workflows.
- **How to run:**
    1. First run the `weatherServer.py` in separate terminal:
        ```bash
        cd mcpDemoLangchain
        python weatherServer.py
        ```
    2. Do not close this terminal and open new terminal.
    3. Now in the new terminal run the `client.py` file.
        ```bash
        cd mcpDemoLangchain
        python client.py
        ```

---

## Notes

- **API Keys:**  
  - Make sure your [.env](http://_vscodecontentref_/4) file contains valid API keys for Groq and any other services you use.
- **Python Version:**  
  - Python 3.10+ is recommended.
- **Troubleshooting:**  
  - If you encounter errors, check that your environment variables are set and dependencies are installed.
  - If you encounter errors, or not able to generate output try to change the current LLM model and then try again to run the code.

---

## Contact

For questions or contributions, please open an issue or pull request