import { useEffect, useState } from "react";
import { fetchPages, getUploadUrl, createScheduledPost } from "../lib/api";

export default function ScheduleForm({ onDone }) {
  const [pages, setPages] = useState([]);
  const [pageId, setPageId] = useState("");
  const [content, setContent] = useState("");
  const [linkUrl, setLinkUrl] = useState("");
  const [scheduledTime, setScheduledTime] = useState("");
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    (async () => {
      const res = await fetchPages();
      setPages(res.data);
      if (res.data.length) setPageId(res.data[0].id);
    })();
  }, []);

  async function submit(e) {
    e.preventDefault();
    setMsg("");
    if (!pageId || !scheduledTime) {
      setMsg("Please select a page and schedule time.");
      return;
    }
    setBusy(true);
    try {
      let mediaId = null;
      if (file) {
        const u = await getUploadUrl(file.name, file.type);
        const { presigned_url, media_id, upload_headers } = u.data;
        await fetch(presigned_url, { method: "PUT", headers: upload_headers, body: file });
        mediaId = media_id;
      }

      const payload = {
        page_id: Number(pageId),
        content,
        link_url: linkUrl || null,
        scheduled_time: scheduledTime,
      };
      if (mediaId) payload.media_id = mediaId;

      await createScheduledPost(payload);
      setMsg("Scheduled ✅");
      setContent("");
      setLinkUrl("");
      setScheduledTime("");
      setFile(null);
      onDone?.();
    } catch (e) {
      setMsg("Failed to schedule. Check backend logs / config.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="bg-white rounded shadow p-5 mb-5">
      <h3 className="font-semibold mb-3">Schedule a Post</h3>
      {msg ? <p className="text-sm mb-3">{msg}</p> : null}
      <form onSubmit={submit} className="grid gap-3">
        <div>
          <label className="text-sm block mb-1">Page</label>
          <select className="border rounded w-full px-3 py-2" value={pageId} onChange={(e)=>setPageId(e.target.value)}>
            {pages.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
        <div>
          <label className="text-sm block mb-1">Text</label>
          <textarea className="border rounded w-full px-3 py-2" rows={3} value={content} onChange={(e)=>setContent(e.target.value)} placeholder="Write your post..." />
        </div>
        <div>
          <label className="text-sm block mb-1">Link (optional)</label>
          <input className="border rounded w-full px-3 py-2" value={linkUrl} onChange={(e)=>setLinkUrl(e.target.value)} placeholder="https://..." />
        </div>
        <div>
          <label className="text-sm block mb-1">Media (optional)</label>
          <input type="file" onChange={(e)=>setFile(e.target.files?.[0] || null)} />
        </div>
        <div>
          <label className="text-sm block mb-1">Schedule time</label>
          <input type="datetime-local" className="border rounded w-full px-3 py-2" value={scheduledTime} onChange={(e)=>setScheduledTime(e.target.value)} />
        </div>
        <button disabled={busy} className="bg-green-600 text-white px-4 py-2 rounded">
          {busy ? "Scheduling..." : "Schedule"}
        </button>
      </form>
    </div>
  );
}
