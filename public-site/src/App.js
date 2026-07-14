import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Public site shell (public pages + the customer portal).
 *
 * Not tenant-branded in the MVP (ADR-0010) — one fixed palette for every tenant.
 */
export default function App() {
    return (_jsxs("main", { className: "min-h-screen p-10", children: [_jsx("h1", { className: "text-display-lg text-on-surface", children: "PropVista" }), _jsx("p", { className: "mt-3 text-body-lg text-on-surface-variant", children: "Scaffold is running. Sprint 0." })] }));
}
