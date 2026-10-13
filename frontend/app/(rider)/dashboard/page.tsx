import DashboardClient from "./dashboard-client";

// Rider data is fetched after browser-side authentication is restored.
export const instant = false;

export default function DashboardPage() {
  return <DashboardClient />;
}
