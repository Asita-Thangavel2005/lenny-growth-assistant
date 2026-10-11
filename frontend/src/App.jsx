
import { useEffect, useState } from "react";
import {
  Activity,
  ArrowUp,
  BookOpen,
  Check,
  ChevronDown,
  FileText,
  Globe,
  History,
  Layers3,
  LoaderCircle,
  MessageSquare,
  PanelRight,
  Plus,
  Sparkles,
  SquarePen,
} from "lucide-react";
import "./App.css";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function App() {
  const [provider, setProvider] = useState("local");
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  useEffect(() => {
  if (sessionId) {
    localStorage.setItem("lenny-active-session", sessionId);
  }
  }, [sessionId]);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [artifact, setArtifact] = useState("");
  const [artifactTitle, setArtifactTitle] = useState("Artifact preview");
  const [showArtifact, setShowArtifact] = useState(true);

  async function loadSessions() {
    try {
      const response = await fetch(`${API}/sessions`);
      if (!response.ok) return;
      const data = await response.json();
      setSessions(Array.isArray(data) ? data : data.value || []);
    } catch {
      setError("Cannot connect to the backend. Start FastAPI on port 8000.");
    }
  }

  async function createSession() {
    setError("");
    try {
      const response = await fetch(`${API}/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "New conversation" }),
      });
      if (!response.ok) throw new Error("Could not create a conversation.");
      const session = await response.json();
      setSessionId(session.id);
      setMessages([]);
      setSources([]);
      setArtifact("");
      setSessions((previous) => [session, ...previous]);
    } catch (err) {
      setError(err.message || "Could not connect to the backend.");
    }
  }

  async function openSession(id) {
    setError("");
    setSessionId(id);
    setMessages([]);
    setSources([]);
    try {
      const response = await fetch(`${API}/sessions/${id}/messages`);
      if (!response.ok) throw new Error("Could not load conversation history.");
      const data = await response.json();
      const loadedMessages = Array.isArray(data) ? data : data.value || [];

      setMessages(loadedMessages);

      const lastAssistant = [...loadedMessages]
        .reverse()
        .find((message) => message.role === "assistant");

      setSources(lastAssistant?.message_metadata?.sources || []);
    } catch (err) {
      setError(err.message || "Could not load conversation history.");
    }
  }

  async function sendMessage(event) {
    event.preventDefault();
    const text = question.trim();
    if (!text || loading) return;

    setError("");
    setQuestion("");
    setMessages((previous) => [
      ...previous,
      { id: crypto.randomUUID(), role: "user", content: text },
    ]);
    setLoading(true);

    try {
      let activeSession = sessionId;
      if (!activeSession) {
        const response = await fetch(`${API}/sessions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: text.slice(0, 60) }),
        });
        if (!response.ok) throw new Error("Could not create a conversation.");
        const session = await response.json();
        activeSession = session.id;
        setSessionId(activeSession);
        setSessions((previous) => [session, ...previous]);
      }

      const response = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: activeSession, question: text,provider, }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "The assistant could not answer.");
      }

      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.answer,
          message_metadata: { sources: data.sources || [] },
        },
      ]);
      setSources(data.sources || []);
      loadSessions();
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

    
  useEffect(() => {
    async function restoreConversation() {
      await loadSessions();

      const savedSessionId = localStorage.getItem("lenny-active-session");

      if (savedSessionId) {
        await openSession(savedSessionId);
      }
    }

    restoreConversation();
  }, []);


  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Sparkles size={19} /></div>
          <div>
            <strong>Lenny's</strong>
            <span>GROWTH ASSISTANT</span>
          </div>
        </div>

        <button className="new-chat" onClick={createSession}>
          <SquarePen size={16} /> New conversation <Plus size={16} />
        </button>

        <div className="side-label"><History size={14} /> RECENT CONVERSATIONS</div>
        <div className="session-list">
          {sessions.map((session) => (
            <button
              key={session.id}
              className={`session-item ${session.id === sessionId ? "selected" : ""}`}
              onClick={() => openSession(session.id)}
            >
              <MessageSquare size={15} />
              <span>{session.title || "New conversation"}</span>
            </button>
          ))}
          {sessions.length === 0 && <p className="empty-history">Your conversations will appear here.</p>}
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <span>Knowledge base connected</span>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="breadcrumb">
            <BookOpen size={17} />
            <span>Podcast knowledge</span>
            <span className="breadcrumb-divider">/</span>
            <strong>Growth advisor</strong>
          </div>
          <div className="top-actions">
            <label className="provider-label" htmlFor="provider">MODEL</label>
            <div className="provider-select">
              <Activity size={15} />
              <select id="provider" value={provider} onChange={(event) => setProvider(event.target.value)}>
                <option value="local">Local · Ollama</option>
                <option value="cloud">Cloud · Claude</option>
              </select>
              <ChevronDown size={13} />
            </div>
            <button className="icon-button" title="Toggle artifact viewer" onClick={() => setShowArtifact((value) => !value)}>
              <PanelRight size={18} />
            </button>
          </div>
        </header>

        {error && <div className="error-banner">{error}</div>}

        <div className={`main-grid ${showArtifact ? "" : "artifact-hidden"}`}>
          <section className="chat-panel">
            <div className="chat-scroll">
              {messages.length === 0 ? (
                <div className="welcome">
                  <div className="welcome-icon"><Sparkles size={24} /></div>
                  <span className="eyebrow">YOUR ON-DEMAND GROWTH ADVISOR</span>
                  <h1>Good ideas start<br />with <em>better questions.</em></h1>
                  <p>Explore product strategy, growth, leadership, and startup lessons grounded in Lenny's Podcast transcripts.</p>
                  <div className="suggestion-grid">
                    {[
                      "How should a startup prioritize product features?",
                      "How can a company improve user activation?",
                      "What makes a strong product-market fit?",
                    ].map((item) => (
                      <button key={item} className="suggestion" onClick={() => setQuestion(item)}>
                        <span>{item}</span><ArrowUp size={15} />
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="messages">
                  {messages.map((message) => (
                    <article key={message.id} className={`message ${message.role}`}>
                      <div className="message-avatar">
                        {message.role === "user" ? "Y" : <Sparkles size={16} />}
                      </div>
                      <div className="message-body">
                        <div className="message-name">{message.role === "user" ? "You" : "Lenny's Assistant"}</div>
                        <div className="message-content">{message.content}</div>
                        {message.role === "assistant" && message.message_metadata?.sources?.length > 0 && (
                          <div className="inline-sources">
                            <span><BookOpen size={13} /> {message.message_metadata.sources.length} transcript sources</span>
                          </div>
                        )}
                      </div>
                    </article>
                  ))}
                  {loading && <div className="loading-line"><LoaderCircle size={17} className="spin" /> Searching transcripts and thinking…</div>}
                </div>
              )}
            </div>

            <div className="composer-wrap">
              <form className="composer" onSubmit={sendMessage}>
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Ask about product, growth, or leadership..."
                  rows={2}
                  disabled={loading}
                />
                <div className="composer-bottom">
                  <span><Globe size={13} /> Answers grounded in podcast transcripts</span>
                  <button className="send-button" type="submit" disabled={loading || !question.trim()}>
                    {loading ? <LoaderCircle size={17} className="spin" /> : <ArrowUp size={18} />}
                  </button>
                </div>
              </form>
              <p className="disclaimer">AI can make mistakes. Check cited transcript evidence before acting.</p>
            </div>
          </section>

        
{showArtifact && (
  <aside className="artifact-panel">
    <div className="panel-heading">
      <div><Layers3 size={17} /><strong>Artifact viewer</strong></div>
      <span className="preview-badge">PREVIEW</span>
    </div>

    {sources.length > 0 ? (
      <div className="source-list">
        {sources.map((source, index) => (
          <article
            className="source-card"
            key={`${source.episode_title}-${index}`}
          >
            <span className="source-number">SOURCE {index + 1}</span>
            <strong>{source.episode_title || "Podcast episode"}</strong>
            <p>{source.content}</p>
            {source.episode_url && (
              <a
                href={source.episode_url}
                target="_blank"
                rel="noreferrer"
              >
                Watch or open episode ↗
              </a>
            )}
          </article>
        ))}
      </div>
    ) : (
      <div className="artifact-empty-state">
        <div className="artifact-illustration">
          <FileText size={27} />
        </div>
        <strong>Your workspace, side by side.</strong>
        <p>Ask a question to see cited podcast passages and episode links here.</p>
        <div className="artifact-tip">
          <Check size={14} /> Sources grounded in transcripts
        </div>
      </div>
    )}

    <div className="artifact-footer">
      <span><Check size={13} /> Transcript evidence</span>
      <span>{sources.length} sources</span>
    </div>
  </aside>
)}

        </div>
      </section>
    </main>
  );
}

export default App;
