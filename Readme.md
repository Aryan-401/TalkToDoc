# Talk To Doc

## How to Get Environment Ready
1. Make sure you have Poetry installed.
2. Clone the repository.
```bash
git clone https://github.com/Aryan-401/TalkToDoc.git
```
2. Run `poetry install` to install all dependencies.
3. Run `poetry shell` to activate the virtual environment.
4. Run `poetry show` to verify.

## How to Run Test Modules
- Run `pytest` to run all test modules.
- Run `pytest .\test\agent_test. to test a specific File`

## How to get Environment Variables

1. Groq
    - Login To`https://console.groq.com/keys` and get the API Key. (Free Ratelimits should be enough)
2. Jina
   - Open `https://jina.ai/embeddings/` in a **PRIVATE WINDOW** and scroll down til you find a hidden key. 
   - You can use this key until its credits get used up, then repeat the process.
