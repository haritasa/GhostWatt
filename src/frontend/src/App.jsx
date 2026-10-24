import { useEffect, useState } from "react";

export default function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    // Proxied to FastAPI (http://127.0.0.1:8000) by vite.config.js
    fetch("/api/hello")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("Could not reach the backend"));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-2">
      <h1 className="text-3xl font-bold">GhostWatt</h1>
      <p className="text-muted-foreground" aria-live="polite">
        {message}
      </p>
    </main>
  );
}
