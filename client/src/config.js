import { Platform } from "react-native";

// Si pruebas en un celular físico, escribe aquí la IP de tu PC (ej. '192.168.1.20').
const LAN_HOST = "";

const HOST =
  LAN_HOST || Platform.select({ android: "10.0.2.2", default: "127.0.0.1" });

export const API_URL = `http://${HOST}:8000/api`;

// Datos de los accesos del pie del login (reemplázalos por los reales).
export const CONTACT_PHONE = "tel:+59100000000";
export const LOCATION_URL = "https://maps.google.com/?q=Cochabamba,Bolivia";
