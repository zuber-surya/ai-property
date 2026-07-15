// Colours, radii, spacing and type all come from ./tailwind.tokens.cjs, which
// is GENERATED FROM docs/DESIGN.md by scripts/gen_tokens.py.
//
// Do not add a colour here. DESIGN.md is the only file that defines one
// (OWNERSHIP.md §3), and check_drift.py will fail a hex literal in src/.
const tokens = require('./tailwind.tokens.cjs');

module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: { extend: tokens },
  plugins: [],
};
