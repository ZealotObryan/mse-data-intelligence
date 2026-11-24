import Link from "next/link";
import { Suspense } from "react";
import { signInAction } from "@/app/auth/actions";
import { hasSupabaseAuthConfig } from "@/lib/supabase/server";
import styles from "./page.module.css";

type Props = {
  searchParams: Promise<{ error?: string; signedOut?: string; next?: string }>;
};

const errorMessages: Record<string, string> = {
  "invalid-input": "Enter a valid email address and password.",
  "sign-in-failed": "Sign-in failed. Check your details or contact the project administrator.",
  "callback-failed": "The sign-in link could not be completed. Please try again.",
  "not-configured": "Authentication is not connected yet. The public demonstration remains available.",
};

function safeReturnPath(value?: string): string {
  if (!value || !value.startsWith("/") || value.startsWith("//") || value.includes("\\")) return "/";
  return value;
}

async function LoginContent({ searchParams }: Props) {
  const params = await searchParams;
  const configured = hasSupabaseAuthConfig();
  const error = params.error ? errorMessages[params.error] : undefined;

  return (
    <main className={styles.page}>
      <section className={styles.card} aria-labelledby="login-title">
        <Link href="/" className={styles.brand}>MSE <span>/</span> ANALYTICS</Link>
        <p className={styles.eyebrow}>RESEARCH WORKSPACE</p>
        <h1 id="login-title">Sign in</h1>
        <p className={styles.intro}>Access is managed by the project team. Public market demonstrations and learning content remain open.</p>

        {!configured ? (
          <div className={styles.notice} role="status">
            <b>Authentication setup pending</b>
            <p>The secure sign-in foundation is in place, but the Supabase project URL and publishable key have not yet been configured for this deployment.</p>
          </div>
        ) : (
          <form action={signInAction} className={styles.form}>
            <input type="hidden" name="next" value={safeReturnPath(params.next)} />
            <label htmlFor="email">Email address</label>
            <input id="email" name="email" type="email" autoComplete="email" required maxLength={254} />
            <label htmlFor="password">Password</label>
            <input id="password" name="password" type="password" autoComplete="current-password" required maxLength={1024} />
            <button type="submit">Sign in securely</button>
          </form>
        )}

        {error && <p className={styles.error} role="alert">{error}</p>}
        {params.signedOut && <p className={styles.success} role="status">You have been signed out.</p>}
        <div className={styles.footer}><Link href="/">← Back to market overview</Link><span>Data integrity first</span></div>
      </section>
    </main>
  );
}

export default function LoginPage(props: Props) {
  return (
    <Suspense fallback={<main className={styles.page}><section className={styles.card}>Loading sign-in…</section></main>}>
      <LoginContent {...props} />
    </Suspense>
  );
}
