/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta Neumórfica de Alta Fidelidad — Beige Suave & Verde Botánico
        neu: {
          bg: "#EFECE6",          // Fondo general cálido
          "bg-card": "#F5F3EF",   // Superficie de tarjetas
          "bg-dark": "#E5E1D8",   // Elementos hundidos / inputs
          "shadow-light": "#FFFFFF",
          "shadow-dark": "#C8C2B7",
          green: "#24533C",       // Verde bosque elegante
          "green-light": "#347253", // Verde esmeralda hover
          "green-accent": "#4E9B73", // Acentos brillantes
          "green-subtle": "#E2ECE6", // Fondos suaves de botones
          text: "#2C3430",        // Texto principal
          "text-light": "#68736C",
          success: "#2E7D32",     // Solvente / Aprobado
          danger: "#C62828",      // Moroso / Rechazado
          warning: "#EF6C00",     // Parcial / En revisión
          info: "#0277BD",        // Informativo
        },
      },
      boxShadow: {
        // Sombras Neumórficas Suaves y Convexas
        neu: "8px 8px 16px #C8C2B7, -8px -8px 16px #FFFFFF",
        "neu-sm": "4px 4px 10px #C8C2B7, -4px -4px 10px #FFFFFF",
        "neu-pill": "6px 6px 12px #C8C2B7, -6px -6px 12px #FFFFFF",
        "neu-inset": "inset 4px 4px 8px #C8C2B7, inset -4px -4px 8px #FFFFFF",
        "neu-inset-sm": "inset 2px 2px 5px #C8C2B7, inset -2px -2px 5px #FFFFFF",
        "neu-pressed": "inset 3px 3px 6px #C8C2B7, inset -3px -3px 6px #FFFFFF",
        "neu-glow": "0 0 15px rgba(36, 83, 60, 0.35)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
      borderRadius: {
        neu: "24px",
        "neu-md": "18px",
        "neu-sm": "14px",
        "neu-pill": "9999px",
      },
    },
  },
  plugins: [],
}
