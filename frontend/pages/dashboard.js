import { useState } from "react";
import Layout from "../components/Layout";
import PageList from "../components/PageList";
import ScheduleForm from "../components/ScheduleForm";
import PostList from "../components/PostList";

export default function Dashboard() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <Layout>
      <div className="max-w-5xl mx-auto grid gap-5">
        <PageList />
        <ScheduleForm onDone={() => setRefreshKey((x) => x + 1)} />
        <PostList refreshKey={refreshKey} />
      </div>
    </Layout>
  );
}
