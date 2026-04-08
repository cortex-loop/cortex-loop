export type ThreadStatus = "open" | "waiting" | "closed";

export type Thread = {
  id: string;
  customer: string;
  subject: string;
  status: ThreadStatus;
  needsFollowUp: boolean;
  tags: string[];
};

export const initialThreads: Thread[] = [
  {
    id: "acme-renewal",
    customer: "Acme",
    subject: "Renewal questions",
    status: "open",
    needsFollowUp: true,
    tags: ["billing", "priority"],
  },
  {
    id: "northwind-export",
    customer: "Northwind",
    subject: "CSV export issue",
    status: "waiting",
    needsFollowUp: false,
    tags: ["bug"],
  },
  {
    id: "orbit-demo",
    customer: "Orbit",
    subject: "Demo follow-up",
    status: "closed",
    needsFollowUp: false,
    tags: ["sales"],
  },
];

export const savedViews = [
  { id: "all", label: "All conversations" },
  { id: "needs-follow-up", label: "Needs follow-up" },
  { id: "waiting", label: "Waiting on customer" },
];

export function getThreadById(threads: Thread[], id: string): Thread | undefined {
  return threads.find((thread) => thread.id === id);
}

export function filterThreads(threads: Thread[], viewId: string): Thread[] {
  if (viewId === "all") {
    return threads;
  }
  return threads;
}
