import { API_URL } from "./config";

let accessToken = null;
export const setAccessToken = (t) => {
  accessToken = t;
};

export class ApiError extends Error {
  constructor(message, status = 0, data = null) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

function extractMessage(data, status) {
  if (!data) return `Error del servidor (${status}).`;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map((d) => d.msg || JSON.stringify(d)).join("\n");
  }
  if (data.mensaje) return data.mensaje;
  return `Error del servidor (${status}).`;
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
  if (auth && accessToken) headers.Authorization = `Bearer ${accessToken}`;

  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    throw new ApiError(
      "No se pudo conectar con el servidor. Revisa tu conexión.",
    );
  }

  let data = null;
  try {
    data = await res.json();
  } catch (e) {}

  if (!res.ok)
    throw new ApiError(extractMessage(data, res.status), res.status, data);
  return data;
}

// POST /api/auth/login
export const login = (username, password) =>
  request("/auth/login", {
    method: "POST",
    auth: false,
    body: { username, password },
  });

// GET /api/auth/me
export const getMe = () => request("/auth/me");

// POST /api/auth/register
export const register = (username, nombre_completo, password) =>
  request("/auth/register", {
    method: "POST",
    auth: false,
    body: { username, nombre_completo, password },
  });

// PATCH /api/auth/password
export const changePassword = (
  password_actual,
  nueva_password,
  confirmar_password,
) =>
  request("/auth/password", {
    method: "PATCH",
    body: { password_actual, nueva_password, confirmar_password },
  });

// PATCH /api/auth/username
export const changeUsername = (nuevo_username) =>
  request("/auth/username", { method: "PATCH", body: { nuevo_username } });
