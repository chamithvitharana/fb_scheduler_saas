import { useEffect, useState } from "react";
import { useRouter } from "next/router";

export default function Layout({ children }) {
  const router = useRouter();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("accessToken") : null;
    const u = typeof window !== "undefined" ? localStorage.getItem("user") : null;

    if (!token && router.pathname !== "/") {
      router.push("/");
      return;
    }
    setUser(u ? JSON.parse(u) : null);
  }, [router.pathname]);

  function logout() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("user");
    router.push("/");
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="px-5 py-4 bg-blue-600 text-white flex items-center justify-between">
        <div className="font-bold">FB Scheduler</div>
        {user ? (
          <div className="flex items-center gap-4">
            <span className="text-sm opacity-90">{user.username}</span>
            <button className="bg-blue-800 px-3 py-1 rounded" onClick={logout}>Logout</button>
          </div>
        ) : null}
      </header>
      <main className="flex-1 p-5 bg-gray-50">{children}</main>
    </div>
  );
}
