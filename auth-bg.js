(() => {
  const root = document.querySelector(".auth-page");
  if (!root) return;

  // Respect users who prefer reduced motion
  const reduceMotion =
    typeof window !== "undefined" &&
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Inject our custom SVG background (original artwork)
  const wrap = document.createElement("div");
  wrap.className = "auth-tech-bg";
  wrap.setAttribute("aria-hidden", "true");
  wrap.innerHTML = `
    <svg class="auth-tech-bg__svg" viewBox="0 0 1200 700" preserveAspectRatio="xMidYMid slice">
      <defs>
        <linearGradient id="beam" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#b721ff" stop-opacity="0.0"></stop>
          <stop offset="50%" stop-color="#21d4fd" stop-opacity="0.55"></stop>
          <stop offset="100%" stop-color="#ff0844" stop-opacity="0.0"></stop>
        </linearGradient>
        <radialGradient id="glow" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stop-color="#21d4fd" stop-opacity="0.25"></stop>
          <stop offset="55%" stop-color="#b721ff" stop-opacity="0.14"></stop>
          <stop offset="100%" stop-color="#000" stop-opacity="0"></stop>
        </radialGradient>
        <filter id="softBlur">
          <feGaussianBlur stdDeviation="6" />
        </filter>
      </defs>

      <!-- subtle grid -->
      <g opacity="0.22">
        ${Array.from({ length: 20 })
          .map((_, i) => {
            const y = 40 + i * 32;
            return `<line x1="0" y1="${y}" x2="1200" y2="${y}" stroke="#ffffff" stroke-opacity="0.08" />`;
          })
          .join("")}
        ${Array.from({ length: 30 })
          .map((_, i) => {
            const x = 40 + i * 38;
            return `<line x1="${x}" y1="0" x2="${x}" y2="700" stroke="#ffffff" stroke-opacity="0.06" />`;
          })
          .join("")}
      </g>

      <!-- diagonal energy beams -->
      <g id="beams" opacity="0.85">
        <path class="beam" d="M-200 640 L520 -80 L640 -80 L-80 640 Z" fill="url(#beam)" />
        <path class="beam" d="M120 760 L860 -120 L980 -120 L240 760 Z" fill="url(#beam)" opacity="0.55" />
      </g>

      <!-- glowing nodes + connecting lines -->
      <g id="net" opacity="0.9">
        <path id="netLines" d="M210 520 C320 420, 420 410, 520 330 S720 240, 810 190 S980 160, 1090 90"
              fill="none" stroke="#21d4fd" stroke-opacity="0.26" stroke-width="2"/>
        <circle class="node" cx="210" cy="520" r="5" fill="#21d4fd" opacity="0.75" />
        <circle class="node" cx="380" cy="420" r="4" fill="#b721ff" opacity="0.7" />
        <circle class="node" cx="520" cy="330" r="5" fill="#21d4fd" opacity="0.75" />
        <circle class="node" cx="720" cy="240" r="4" fill="#b721ff" opacity="0.7" />
        <circle class="node" cx="810" cy="190" r="5" fill="#21d4fd" opacity="0.75" />
        <circle class="node" cx="980" cy="160" r="4" fill="#b721ff" opacity="0.7" />
        <circle class="node" cx="1090" cy="90" r="5" fill="#21d4fd" opacity="0.75" />
      </g>

      <!-- soft ambient glow -->
      <circle id="ambient" cx="920" cy="220" r="260" fill="url(#glow)" filter="url(#softBlur)" />

      <!-- a moving scan line -->
      <rect id="scan" x="-200" y="0" width="1600" height="10" fill="#21d4fd" opacity="0.12" />
    </svg>
  `;

  root.prepend(wrap);

  if (reduceMotion) return;

  // Load GSAP from CDN (only on auth pages)
  const ensureGsap = () =>
    new Promise((resolve) => {
      if (window.gsap) return resolve(window.gsap);
      const s = document.createElement("script");
      s.src = "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js";
      s.onload = () => resolve(window.gsap);
      document.head.appendChild(s);
    });

  ensureGsap().then((gsap) => {
    const svg = wrap.querySelector("svg");
    if (!svg) return;

    const beams = svg.querySelectorAll(".beam");
    const nodes = svg.querySelectorAll(".node");
    const ambient = svg.querySelector("#ambient");
    const scan = svg.querySelector("#scan");
    const netLines = svg.querySelector("#netLines");

    gsap.set(beams, { transformOrigin: "50% 50%" });
    gsap.to(beams, {
      x: (i) => (i % 2 === 0 ? 40 : -30),
      y: (i) => (i % 2 === 0 ? -25 : 20),
      duration: 6,
      ease: "sine.inOut",
      yoyo: true,
      repeat: -1,
    });

    gsap.to(ambient, {
      attr: { cx: 840, cy: 260 },
      duration: 8,
      ease: "sine.inOut",
      yoyo: true,
      repeat: -1,
    });

    gsap.to(nodes, {
      opacity: (i) => (i % 2 ? 0.35 : 0.9),
      r: (i) => (i % 2 ? 3.2 : 6.2),
      duration: 1.6,
      ease: "sine.inOut",
      stagger: { each: 0.15, yoyo: true, repeat: -1 },
    });

    // Animate dash offset for the network line (data flow effect)
    gsap.set(netLines, { strokeDasharray: 10, strokeDashoffset: 0 });
    gsap.to(netLines, {
      strokeDashoffset: -160,
      duration: 6,
      ease: "none",
      repeat: -1,
    });

    // Moving scan line
    gsap.set(scan, { y: -30 });
    gsap.to(scan, {
      y: 730,
      duration: 4,
      ease: "none",
      repeat: -1,
    });
  });
})();

