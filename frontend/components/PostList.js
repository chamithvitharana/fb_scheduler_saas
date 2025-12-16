import { useEffect, useState } from "react";
import { fetchScheduledPosts, fetchPostStatus } from "../lib/api";

export default function PostList({ refreshKey }) {
  const [posts, setPosts] = useState([]);
  const [status, setStatus] = useState(null);

  async function load() {
    const res = await fetchScheduledPosts();
    setPosts(res.data.results || res.data); // DRF may paginate
  }

  useEffect(() => { load(); }, [refreshKey]);

  async function view(id) {
    const res = await fetchPostStatus(id);
    setStatus(res.data);
  }

  return (
    <div className="bg-white rounded shadow p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Scheduled Posts</h3>
        <button className="text-sm underline" onClick={load}>Refresh</button>
      </div>

      {posts.length === 0 ? <p className="text-sm text-gray-600">No posts yet.</p> : (
        <div className="overflow-auto">
          <table className="min-w-full text-sm border">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 border">Time</th>
                <th className="p-2 border">Page</th>
                <th className="p-2 border">Status</th>
                <th className="p-2 border">Text</th>
                <th className="p-2 border">Action</th>
              </tr>
            </thead>
            <tbody>
              {posts.map(p => (
                <tr key={p.id}>
                  <td className="p-2 border">{new Date(p.scheduled_time).toLocaleString()}</td>
                  <td className="p-2 border">{p.page?.name || "-"}</td>
                  <td className="p-2 border">{p.status}</td>
                  <td className="p-2 border">{(p.content || "").slice(0, 60)}</td>
                  <td className="p-2 border">
                    <button className="text-blue-600 underline" onClick={()=>view(p.id)}>Logs</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {status ? (
        <div className="mt-4 border rounded p-3 bg-gray-50">
          <div className="font-semibold mb-2">Post {status.post_id} — {status.status}</div>
          {status.logs?.length ? status.logs.map((l, idx) => (
            <div key={idx} className={`text-xs ${l.status === "failure" ? "text-red-700" : "text-green-700"}`}>
              [{new Date(l.timestamp).toLocaleString()}] attempt {l.attempt}: {l.message}
            </div>
          )) : <div className="text-xs text-gray-600">No logs yet.</div>}
        </div>
      ) : null}
    </div>
  );
}
