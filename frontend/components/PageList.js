import { useEffect, useState } from "react";
import { fetchPages, getFacebookAuthURL } from "../lib/api";

export default function PageList() {
  const [pages, setPages] = useState([]);
  const [err, setErr] = useState("");

  async function load() {
    setErr("");
    try {
      const res = await fetchPages();
      setPages(res.data);
    } catch (e) {
      setErr("Failed to load pages. Connect Facebook first.");
    }
  }

  useEffect(() => { load(); }, []);

  async function connect() {
    const res = await getFacebookAuthURL();
    window.location.href = res.data.auth_url;
  }

  return (
    <div className="bg-white rounded shadow p-5 mb-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Connected Pages</h3>
        <button className="bg-blue-600 text-white px-3 py-1 rounded" onClick={connect}>Connect Facebook</button>
      </div>
      {err ? <p className="text-sm text-red-600 mb-3">{err}</p> : null}
      {pages.length === 0 ? (
        <p className="text-sm text-gray-600">No pages connected yet.</p>
      ) : (
        <ul className="list-disc list-inside text-sm">
          {pages.map(p => <li key={p.id}>{p.name}</li>)}
        </ul>
      )}
    </div>
  );
}
