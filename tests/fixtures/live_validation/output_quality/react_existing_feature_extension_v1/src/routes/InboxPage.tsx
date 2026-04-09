import { Link } from "react-router-dom";

import type { Thread } from "../data/threads";

type Props = {
  threads: Thread[];
  activeViewId: string;
};

export function InboxPage({ threads, activeViewId }: Props) {
  return (
    <main className="content">
      <section className="panel stack">
        <p>Inbox</p>
        <h1>Conversations</h1>
        <p>Active view: {activeViewId}</p>
      </section>
      <section className="stack">
        {threads.map((thread) => (
          <article className="panel stack" key={thread.id}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem" }}>
              <div>
                <h2>{thread.customer}</h2>
                <p>{thread.subject}</p>
              </div>
              <span className="pill">{thread.status}</span>
            </div>
            <Link to={`/threads/${thread.id}`}>Open thread</Link>
          </article>
        ))}
      </section>
    </main>
  );
}
