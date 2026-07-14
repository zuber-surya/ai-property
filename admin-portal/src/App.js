import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Admin portal shell.
 *
 * NOT tenant-branded (ADR-0010) — it carries the PropVista brand.
 * Colours come from token classes only; a hex literal here fails check_drift.
 */
export default function App() {
    return (_jsxs("main", { className: "min-h-screen p-10", children: [_jsx("h1", { className: "text-headline-lg text-on-surface", children: "PropVista Admin" }), _jsx("p", { className: "mt-3 text-body-md text-on-surface-variant", children: "Scaffold is running. Sprint 0." }), _jsx("span", { className: "chip chip-success mt-6 inline-block", children: "Published" }), _jsx("span", { className: "chip chip-info mt-6 ml-2 inline-block", children: "Contacted" }), _jsx("span", { className: "chip chip-neutral mt-6 ml-2 inline-block", children: "New" })] }));
}
