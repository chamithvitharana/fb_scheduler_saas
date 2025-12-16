import { useState } from "react";
import Layout from "../components/Layout";
import { LoginForm, SignupForm } from "../components/AuthForms";

export default function Home() {
  const [mode, setMode] = useState("login");

  return (
    <Layout>
      <div className="max-w-4xl mx-auto mt-10 grid gap-4 justify-items-center">
        {mode === "login" ? <LoginForm /> : <SignupForm />}
        <button className="text-blue-600 underline text-sm" onClick={() => setMode(mode === "login" ? "signup" : "login")}>
          {mode === "login" ? "Need an account? Sign up" : "Already have an account? Log in"}
        </button>
      </div>
    </Layout>
  );
}
