import { Navigate, Route, Routes, useParams } from "react-router-dom";
import { useMemo, useState } from "react";

import { Sidebar } from "./components/Sidebar";
import {
  filterThreads,
  getThreadById,
  initialThreads,
} from "./data/threads";
import { InboxPage } from "./routes/InboxPage";
import { SavedViewsPage } from "./routes/SavedViewsPage";
import { ThreadDetailPage } from "./routes/ThreadDetailPage";

function ThreadRoute({ threads }: { threads: typeof initialThreads }) {
  const { id = "" } = useParams();
  return <ThreadDetailPage thread={getThreadById(threads, id)} />;
}

export default function App() {
  const [activeViewId] = useState("all");
  const threads = useMemo(() => filterThreads(initialThreads, activeViewId), [activeViewId]);

  return (
    <div className="shell">
      <Sidebar />
      <Routes>
        <Route path="/" element={<Navigate to="/inbox" replace />} />
        <Route path="/inbox" element={<InboxPage activeViewId={activeViewId} threads={threads} />} />
        <Route path="/threads/:id" element={<ThreadRoute threads={initialThreads} />} />
        <Route path="/views" element={<SavedViewsPage />} />
        <Route path="*" element={<Navigate to="/inbox" replace />} />
      </Routes>
    </div>
  );
}
