import { NextResponse, type NextRequest } from "next/server";
import { createClient, hasSupabaseAuthConfig } from "@/lib/supabase/server";

function safeReturnPath(value: string | null): string {
  if (!value || !value.startsWith("/") || value.startsWith("//") || value.includes("\\")) {
    return "/";
  }
  return value;
}

export async function GET(request: NextRequest) {
  const url = request.nextUrl.clone();
  const code = url.searchParams.get("code");
  const returnTo = safeReturnPath(url.searchParams.get("next"));

  if (!hasSupabaseAuthConfig()) {
    url.pathname = "/login";
    url.search = "?error=not-configured";
    return NextResponse.redirect(url);
  }

  if (!code) {
    url.pathname = "/login";
    url.search = "?error=callback-failed";
    return NextResponse.redirect(url);
  }

  try {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (error) throw error;
    url.pathname = returnTo;
    url.search = "";
    return NextResponse.redirect(url);
  } catch {
    url.pathname = "/login";
    url.search = "?error=callback-failed";
    return NextResponse.redirect(url);
  }
}
