import React, { createContext, useContext, useState, useCallback } from "react";
import * as api from "../api";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null); // respuesta completa del login
  const [user, setUser] = useState(null);

  const signIn = useCallback(async (username, password) => {
    const data = await api.login(username.trim(), password);
    api.setAccessToken(data.access_token);
    setSession(data);
    setUser(data.usuario);
    return data;
  }, []);

  const signOut = useCallback(() => {
    api.setAccessToken(null);
    setSession(null);
    setUser(null);
  }, []);

  const updateUsername = useCallback(async (nuevo) => {
    const data = await api.changeUsername(nuevo.trim());
    setUser((u) => ({ ...u, username: data.username }));
    return data;
  }, []);

  return (
    <AuthContext.Provider
      value={{
        session,
        user,
        isSignedIn: !!session,
        signIn,
        signOut,
        updateUsername,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
