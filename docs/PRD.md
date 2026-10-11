# Product Requirements Document (PRD)

## 1. Product Overview

**Product:** Lenny Growth Assistant

**Purpose:** Help users explore product management, growth, and startup topics using evidence retrieved from Lenny's Podcast transcripts.

The application combines a conversational interface, transcript retrieval, an LLM-powered response layer, persistent chat sessions, and a dedicated Ship 30 for 30 essay-writing skill.

## 2. Problem Statement

Users need a convenient way to explore a large collection of podcast transcripts without manually searching individual episodes. General-purpose LLM responses may also include unsupported claims or lack traceable sources.

Lenny Growth Assistant addresses these problems by retrieving relevant transcript excerpts, grounding responses in those excerpts, and exposing source information alongside the conversation.

## 3. Product Goals

- Answer questions using relevant podcast transcript evidence.
- Make supporting episodes and transcript excerpts discoverable.
- Preserve chat sessions and conversation history.
- Allow users to select local or cloud generation.
- Support a dedicated, transcript-grounded Ship 30 for 30 essay workflow.
- Provide a straightforward local development and demonstration experience.

## 4. Intended Users

- Product managers exploring product strategy and growth.
- Founders and startup teams researching product decisions.
- Students and practitioners learning from product and startup discussions.
- Writers creating evidence-based essays from podcast material.

## 5. Core User Journeys

### 5.1 Ask a question

1. The user opens the chat interface.
2. The user creates or selects a conversation.
3. The user submits a question.
4. The backend retrieves relevant transcript chunks.
5. The selected LLM provider generates a response when relevant evidence is available.
6. The response and associated source metadata are saved.
7. The user reviews the answer and its supporting sources.

### 5.2 Resume a conversation

1. The user selects an existing session.
2. The frontend requests its messages.
3. The application displays the conversation history.
4. Available source metadata is restored for the relevant assistant response.

### 5.3 Change the generation provider

1. The user selects Local or Cloud in the interface.
2. The frontend includes the selected provider in the chat request.
3. The backend uses the requested provider.
4. If cloud generation fails, the backend attempts local Ollama fallback.

Cloud generation requires a configured Anthropic API key. Local fallback requires a running Ollama service and an installed model.

### 5.4 Generate a Ship 30 for 30 essay

1. The user explicitly requests a Ship 30 for 30 essay.
2. The backend detects the request and loads the dedicated essay skill.
3. Relevant transcript chunks are retrieved.
4. The essay workflow is included in the generation prompt.
5. The response follows the skill's writing guidance while retaining evidence and citation requirements.

If no relevant chunks are retrieved, the current chat flow returns an evidence-limitation response instead of generating an unsupported essay.

## 6. Functional Requirements

### FR-1: Conversational API

The backend must expose HTTP endpoints for creating and retrieving sessions, reading messages, and submitting chat questions.

### FR-2: Session persistence

Sessions must have identifiers, timestamps, and relevant metadata. A user must be able to return to a previous session.

### FR-3: Message persistence

User and assistant messages must be stored with their session association, timestamps, and applicable metadata.

### FR-4: Transcript retrieval

The application must retrieve relevant transcript chunks using vector similarity and the configured retrieval limit.

### FR-5: Source metadata

Responses must expose supporting source information, including episode titles, URLs, and transcript excerpts.

### FR-6: Evidence-grounded responses

The generation prompt must require factual grounding, source citations, and disclosure when evidence is insufficient. Retrieved transcript content must be treated as untrusted input.

### FR-7: Provider selection

The interface must allow the user to choose local Ollama or cloud Claude. Provider configuration and cloud credentials must remain on the backend.

### FR-8: Cloud fallback

When cloud generation fails with a handled LLM service error, the service must attempt generation through local Ollama.

### FR-9: Essay skill

The application must load and apply the dedicated Ship 30 for 30 skill when the corresponding essay request is detected.

### FR-10: Source and artifact viewing

The interface must allow users to inspect retrieved source information alongside the conversation.

### FR-11: Configuration

The application must support environment-based configuration and provide a safe `.env.example` without real credentials.

## 7. Non-Functional Requirements

### Reliability

- Invalid or missing sessions must produce a controlled error.
- Empty questions must be rejected.
- LLM failures must be handled without exposing secrets.
- Provider fallback must not be presented as successful cloud generation.

### Security

- Secrets must not be committed to source control.
- API credentials must remain server-side.
- Retrieved transcript text must not be trusted as system instructions.
- Generated HTML must be sanitized or isolated before rendering.

### Maintainability

- API, persistence, retrieval, prompt construction, and generation responsibilities should remain separated into services.
- Configuration should be environment-driven.
- The setup and architecture should be documented.

### Performance

- Retrieval should use vector search rather than scanning all transcript text in application memory.
- The system should avoid retrieving more chunks than needed for a response.
- Response latency depends on database performance, model choice, and available compute.

## 8. User Interface Requirements

- A chat area for questions and answers.
- A session list for accessing previous conversations.
- A visible local/cloud provider selector.
- A source or artifact viewer for examining supporting transcript material.
- Clear handling of loading states and request errors.

## 9. Acceptance Criteria

- [ ] A user can create a chat session and submit a question.
- [ ] Messages persist in PostgreSQL and can be retrieved by session.
- [ ] Relevant transcript chunks are retrieved from the vector database.
- [ ] Responses include source references when evidence is available.
- [ ] The application reports insufficient evidence rather than inventing transcript support.
- [ ] The local provider works with a configured Ollama model.
- [ ] The cloud provider uses the Claude Agent SDK when configured.
- [ ] Cloud failure triggers the documented local fallback path.
- [ ] A Ship 30 for 30 request activates the dedicated skill.
- [ ] The frontend displays session history, provider selection, and source information.
- [ ] Configuration instructions and required environment variables are documented.
- [ ] Automated tests cover the implemented API, retrieval, routing, and persistence behavior.

## 10. Out of Scope

Unless separately implemented and verified, the following are not promised:

- User accounts, authentication, or multi-tenant access control.
- Real-time podcast ingestion.
- Guaranteed answers for topics absent from the transcript corpus.
- Guaranteed cloud availability or a cloud-only deployment.
- Unrestricted execution of generated HTML or code.
- Production-scale performance guarantees.

## 11. Dependencies and Constraints

- PostgreSQL and pgvector for persistent storage and vector retrieval.
- A compatible embedding model for indexing and queries.
- Ollama and a locally available model for local generation.
- Claude Agent SDK and a valid API key for cloud generation.
- Access to a suitable transcript corpus.
- A compatible Python and Node.js environment.

## 12. Risks

| Risk | Mitigation |
|---|---|
| Relevant evidence is not retrieved | Tune chunking, embeddings, and retrieval thresholds using representative queries. |
| Generated claims exceed source evidence | Require citations and explicit uncertainty in prompts. |
| Cloud provider is unavailable | Document and verify local fallback. |
| Local inference is slow | Use a suitable model and set realistic expectations for local hardware. |
| Transcript redistribution is restricted | Review source terms and avoid publishing raw transcript files without permission. |
| Generated HTML is unsafe | Sanitize output or render it in an appropriately isolated context. |

## 13. Success Measures

For the assignment demonstration, success means that a user can ask a question, receive a source-grounded response, inspect the supporting episode information, resume a saved session, change providers, and invoke the essay-writing workflow.

These measures describe intended demonstration behavior; they are not claims of independently measured production performance.
