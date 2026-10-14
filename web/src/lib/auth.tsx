import { createContext, useContext, useState, type ReactNode } from "react";
import { authGoogle } from "./api";

/** 토큰·이메일은 localStorage에 보관 — 게스트 흐름(분석·샘플)은 로그인 없이 그대로 동작한다. */

const TOKEN_KEY = "swinglab_token";
const EMAIL_KEY = "swinglab_email";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

interface AuthContextValue {
  email: string | null;
  isLoggedIn: boolean;
  loginWithGoogle: (credential: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(localStorage.getItem(EMAIL_KEY));

  function store(token: string, mail: string) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(EMAIL_KEY, mail);
    setEmail(mail);
  }

  async function loginWithGoogle(credential: string) {
    const res = await authGoogle(credential);
    store(res.token, res.email);
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EMAIL_KEY);
    setEmail(null);
  }

  return (
    <AuthContext.Provider value={{ email, isLoggedIn: email !== null, loginWithGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
