# Design Document — Lenny Growth Assistant

## 1. Design Overview

Lenny Growth Assistant uses a conversational interface for asking questions about Lenny's Podcast transcripts. The design keeps the conversation as the primary workspace while making previous sessions, provider selection, and supporting source material accessible.

The design prioritizes:
- A focused chat experience.
- Visible control over the model provider.
- Persistent access to previous conversations.
- Traceability from answers to supporting transcript excerpts.
- Clear separation between generated answers and source evidence.

## 2. Interface Layout

The main interface is organized into three functional areas.

### 2.1 Session Sidebar

The sidebar lists available chat sessions and allows the user to return to an earlier conversation.

Responsibilities:
- Display previously created sessions.
- Allow selection of a session.
- Load messages for the selected session.
- Preserve the selected session across page reloads where supported by the frontend.

Session records and messages are persisted by the backend in PostgreSQL. The frontend stores the selected session identifier locally to restore the selection.

### 2.2 Conversation Area

The conversation area is the primary interaction surface.

Responsibilities:
- Display user questions and assistant answers.
- Provide a question input.
- Submit a question to the backend.
- Display the response and associated source information.
- Support follow-up questions within a conversation.

A new session should be created before submitting a question when no active session exists. The interface should make request failures visible instead of presenting them as successful responses.

### 2.3 Provider Selector

The provider selector allows users to choose between:

- **Local — Ollama:** Sends generation requests to a model served by the local Ollama installation.
- **Cloud — Claude:** Uses the Claude Agent SDK and requires a backend-configured Anthropic API key.

The frontend sends the selected provider with the chat request. The backend remains responsible for provider execution and fallback.

The selector indicates the requested provider; it should not be interpreted as proof that the provider successfully handled a particular response. If cloud generation fails and local fallback succeeds, the backend currently logs the fallback, but the response schema does not necessarily expose the provider that actually generated the answer.

## 3. Source and Artifact Viewer

The viewer presents source information associated with assistant responses.

Source metadata includes:
- Episode title.
- Episode URL.
- Transcript chunk index.
- Transcript excerpt.

The viewer supports answer inspection by allowing the user to examine the evidence returned by retrieval.

### Interaction behavior

1. The user submits a question.
2. The backend retrieves relevant transcript chunks.
3. The assistant response and source metadata are persisted.
4. The frontend reads source metadata from the response or the saved assistant message.
5. The user inspects the associated source material in the viewer.

When a previous session is reopened, the frontend should restore the source information available in the saved assistant-message metadata.

### Generated HTML safety

Generated HTML must be treated as untrusted content. It must not be inserted into the application's trusted DOM without appropriate safeguards.

If HTML artifacts are rendered, use a suitable sanitizer and/or a sandboxed iframe with a restrictive policy. Avoid enabling scripts or unrestricted access to the parent application. The viewer should provide a safe text or source-inspection fallback when secure rendering is not available.

## 4. Primary User Flows

### Flow A — Start a conversation

1. The user opens the application.
2. The frontend loads available sessions.
3. The user creates a new session.
4. The user enters a question.
5. The frontend submits the session ID, question, and provider.
6. The backend retrieves evidence and generates a response when appropriate.
7. The interface displays the answer and supporting source information.

### Flow B — Continue a previous conversation

1. The user selects a session in the sidebar.
2. The frontend requests its messages.
3. The conversation area displays the saved messages.
4. The viewer restores source metadata where it is available.
5. The user submits a follow-up question.

### Flow C — Change provider

1. The user selects Local or Cloud.
2. The selected value is included in the next chat request.
3. The backend chooses the corresponding generation path.
4. Cloud errors may trigger local Ollama fallback.

### Flow D — Request a Ship 30 for 30 essay

1. The user explicitly requests a Ship 30 for 30 essay.
2. The backend detects the request phrase.
3. The dedicated essay skill is loaded into the RAG prompt.
4. Retrieved transcript evidence is supplied to generation.
5. The response follows the essay skill while retaining source-grounding requirements.

The current implementation activates the skill using explicit phrase matching, including `Ship 30 for 30`, `Ship 30/30`, and `Ship30for30`.

## 5. Visual and Interaction Principles

### Clarity

Keep the question-and-answer exchange visually dominant. Provider controls and session navigation should remain easy to locate.

### Traceability

Make the connection between an answer and its supporting sources apparent. Source metadata should remain associated with the correct assistant response.

### User control

Allow users to select a provider and reopen earlier sessions without losing access to persisted history.

### Honest feedback

Do not imply that a cloud request succeeded if the service fell back to local generation. Make loading and error states understandable.

### Safe presentation

Do not treat generated text, transcript content, or generated HTML as trusted application code.

## 6. Frontend and Backend Contract

The frontend communicates with the FastAPI backend over HTTP using JSON.

The chat request includes:
- `session_id`
- `question`
- `provider` (`local`, `cloud`, or omitted to use the backend default)

The chat response includes:
- `session_id`
- `answer`
- `sources`

The exact error response and session-list contract are defined by the backend API implementation.

The frontend's API base URL must be configured to match the backend address in the selected environment. Production deployments should not rely on a hard-coded localhost URL.

## 7. Accessibility and Usability Considerations

- Provide readable contrast and legible text.
- Keep provider labels explicit rather than relying only on color.
- Ensure controls can be operated using a keyboard.
- Give loading and failure states clear text labels.
- Keep source links recognizable and usable.
- Avoid presenting long transcript excerpts in a way that overwhelms the conversation.

These are design goals; verify them against the rendered interface before claiming full accessibility compliance.

## 8. Design Limitations and Future Improvements

Potential improvements include:
- Displaying the actual provider used for each response.
- Adding clearer loading, retry, and connection-error states.
- Allowing source citations in answer text to open the corresponding source in the viewer.
- Supporting safe preview of generated HTML artifacts.
- Improving keyboard navigation and accessibility checks.
- Adding session renaming and deletion if needed.

These improvements should be treated as future work unless they are implemented and verified in the application.
