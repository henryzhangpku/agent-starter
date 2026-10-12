# The look the demo, report and pitch follow

Set this once from the team's own product (their site or app): the feel,
never their logo, name or artwork. The default below is a calm, neutral
enterprise look.

- **Palette**: near-white ground `#fafafa`, surface `#ffffff`, ink `#171717`,
  secondary text `#737373`, hairlines `#e5e5e5`, one soft accent `#e9d5ff`
  with a deeper accent for links and focus `#6d28d9`. Dark mode: ground
  `#0a0a0a`, surface `#171717`, ink `#fafafa`, secondary `#a3a3a3`.
- **Type**: headings in a light editorial serif (Newsreader 300, Google
  Fonts), body in a clean sans (Geist or system-ui), labels, numbers and
  code in a mono (JetBrains Mono). Large, light headlines; small mono
  eyebrows in uppercase with letter-spacing.
- **Layout**: generous whitespace, a single column up to about 72rem, cards
  with a 1px hairline and no heavy shadow, rounded corners of 10-12px,
  metrics as large light numerals with a mono label.
- **Theme**: light by default, like most enterprise products; dark only through
  a visible toggle, never forced by the viewer's system setting.
- **Tone**: plain, confident, enterprise; no gradients, no emoji.
- **Use the kit files, do not hand-roll the look**: copy `.claude/kit/look.css`
  and `.claude/kit/diagrams.js` into the product's static folder, link
  `look.css` from every page (demo, pitch, rendered docs) and include
  `diagrams.js` on every page with a diagram. `check_demo.py` fails without
  them, and fails on any `prefers-color-scheme: dark` rule.
- **Diagrams** (Mermaid): top-down (`flowchart TD`), boxes of 2-4 words,
  arrows of 1-3 words (at most 28 characters); every detail (latency,
  failure path, PII, contract) goes in the table under the diagram. Drawn
  at least 900px wide, click for full screen (diagrams.js does both).
- **Links between docs** go to the served page (`/integration`), never to a
  `.md` file or as raw markdown.
