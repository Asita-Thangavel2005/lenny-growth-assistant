# Manual UI Test Plan — Lenny Growth Assistant

## Preconditions

- PostgreSQL is running, pgvector is enabled, and application tables exist.
- Transcript chunks have been ingested.
- Ollama is running with the configured model.
- The FastAPI backend and React frontend are running.

## Test cases

| ID | Test | Expected result |
|---|---|---|
| UI-01 | Open the application | Chat interface loads without a frontend error. |
| UI-02 | Create a conversation | A new session appears in the conversation list. |
| UI-03 | Ask a question about a podcast topic | The assistant responds using relevant transcript evidence when available. |
| UI-04 | Inspect source references | Returned sources display their episode titles and links. |
| UI-05 | Ask a follow-up question | The assistant uses the existing conversation context appropriately. |
| UI-06 | Ask about a topic unsupported by retrieved evidence | The assistant acknowledges insufficient evidence rather than inventing transcript-based facts. |
| UI-07 | Select the local provider | The request uses the configured Ollama model. |
| UI-08 | Select the cloud provider with valid credentials | Claude is used; if cloud generation fails, local fallback is attempted. |
| UI-09 | Request a Ship 30 for 30 essay | The dedicated essay-writing workflow is applied. |
| UI-10 | Reload the application | Persisted conversations remain available. |
| UI-11 | Open a generated artifact | The artifact viewer displays the generated content. |
| UI-12 | Stop Ollama and submit a local request | The failure is handled without an unhandled frontend crash. Restore Ollama afterward. |

## Execution record

For each test, record the date, environment, result (`PASS`, `FAIL`, or `BLOCKED`), and observations. Mark tests as passed only after executing them.

Cloud-provider tests require valid credentials and may incur API charges.
