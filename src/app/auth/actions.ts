"use server";

import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

function safeReturnPath(value: FormDataEntryValue | string | null): string {
  if (typeof value !== "string") return "/";
  if (!value.startsWith("/") || value.startsWith("//") || value.includes("\\")) return "/";
  return value;
}

export async function signInAction(formData: FormData) {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  const returnTo = safeReturnPath(formData.get("next"));

  if (!email || !password || email.length > 254 || password.length > 1024) {
    redirect("/login?error=invalid-input");
  }

  let supabase;
  try {
    supabase = await createClient();
  } catch {
    redirect("/login?error=not-configured");
  }

  const { error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) {
    // Avoid exposing provider details or confirming whether an account exists.
    redirect("/login?error=sign-in-failed");
  }

  redirect(returnTo);
}

export async function signOutAction() {
  try {
    const supabase = await createClient();
    await supabase.auth.signOut();
  } finally {
    redirect("/login?signed-out=1");
  }
}
