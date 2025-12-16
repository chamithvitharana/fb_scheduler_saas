import { useState } from "react";
import { useRouter } from "next/router";
import { login, register } from "../lib/api";

export function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const router = useRouter();

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    try {
      const res = await login(username, password);
      localStorage.setItem("accessToken", res.data.access);
      localStorage.setItem("refreshToken", res.data.refresh);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      router.push("/dashboard");
    } catch {
      setErr("Login failed. Check username/password.");
    }
  }

  return (
    <form onSubmit={onSubmit} className="w-full max-w-md bg-white p-6 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Login</h2>
      {err ? <p className="text-red-600 mb-3">{err}</p> : null}
      <label className="block mb-2 text-sm">Username</label>
      <input className="w-full border px-3 py-2 rounded mb-4" value={username} onChange={(e)=>setUsername(e.target.value)} />
      <label className="block mb-2 text-sm">Password</label>
      <input type="password" className="w-full border px-3 py-2 rounded mb-5" value={password} onChange={(e)=>setPassword(e.target.value)} />
      <button className="w-full bg-blue-600 text-white py-2 rounded">Log in</button>
    </form>
  );
}

export function SignupForm() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const router = useRouter();

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    try {
      const res = await register(username, email, password);
      localStorage.setItem("accessToken", res.data.access);
      localStorage.setItem("refreshToken", res.data.refresh);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      router.push("/dashboard");
    } catch {
      setErr("Signup failed. Username may already exist.");
    }
  }

  return (
    <form onSubmit={onSubmit} className="w-full max-w-md bg-white p-6 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Create account</h2>
      {err ? <p className="text-red-600 mb-3">{err}</p> : null}
      <label className="block mb-2 text-sm">Username</label>
      <input className="w-full border px-3 py-2 rounded mb-4" value={username} onChange={(e)=>setUsername(e.target.value)} />
      <label className="block mb-2 text-sm">Email</label>
      <input className="w-full border px-3 py-2 rounded mb-4" value={email} onChange={(e)=>setEmail(e.target.value)} />
      <label className="block mb-2 text-sm">Password</label>
      <input type="password" className="w-full border px-3 py-2 rounded mb-5" value={password} onChange={(e)=>setPassword(e.target.value)} />
      <button className="w-full bg-blue-600 text-white py-2 rounded">Sign up</button>
    </form>
  );
}
