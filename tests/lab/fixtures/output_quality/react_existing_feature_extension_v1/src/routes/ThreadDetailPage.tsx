import { Link } from "react-router-dom";

import type { Thread } from "../data/threads";

type Props = {
  thread: Thread | undefined;
};

export function ThreadDetailPage({ thread }: Props) {
  if (!thread) {
    return (
      <main className="content">
        <section className="panel stack">
          <h1>Conversation not found</h1>
          <Link to="/inbox">Back to inbox</Link>
        </section>
      </main>
    );
  }

  return (
    <main className="content">
      <section className="panel stack">
        <p>{thread.customer}</p>
        <h1>{thread.subject}</h1>
        <span className="pill">{thread.status}</span>
        <p>Tags: {thread.tags.join(", ")}</p>
        <p>Needs follow-up: {thread.needsFollowUp ? "Yes" : "No"}</p>
        <Link to="/inbox">Back to inbox</Link>
      </section>
    </main>
  );
}
