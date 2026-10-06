import { useEffect } from "react";

// Per-route <title>, <html> and <body> attributes as they were on the original page after its scripts ran.
export default function usePageChrome({ title, html = {}, body = {} }) {
  useEffect(() => {
    document.title = title;
    const apply = (el, attrs) => { for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v); };
    apply(document.documentElement, html);
    apply(document.body, body);
    const els = document.querySelectorAll("[data-reveal]");
    document.documentElement.classList.add("reveal-ready");
    if (!("IntersectionObserver" in window)) { els.forEach((e) => e.classList.add("is-in")); return; }
    const io = new IntersectionObserver((entries) => entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } }), { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    els.forEach((e) => io.observe(e));

    // Stat counters: a bare number that was mid-count-up when the original page was captured (its digits read
    // differently right after load than once settled). Counts from data-count-from to data-count-to the first time
    // the element scrolls into view, matching the original's digit grouping (1,200 vs 1200) and decimal places.
    // Off under reduced motion — the final value is already the element's own text, nothing further to do.
    const counters = document.querySelectorAll("[data-count-to]");
    let cio;
    if (counters.length && !window.matchMedia("(prefers-reduced-motion: reduce)").matches && "IntersectionObserver" in window) {
      const animate = (el) => {
        const to = el.getAttribute("data-count-to"), from = el.getAttribute("data-count-from") || "0";
        const toN = parseFloat(to.replace(/,/g, "")), fromN = parseFloat(from.replace(/,/g, ""));
        if (!isFinite(toN) || !isFinite(fromN)) return;
        const grouped = /,/.test(to), decimals = (to.split(".")[1] || "").length;
        const fmt = (n) => { let s = n.toFixed(decimals); if (grouped) s = s.replace(/\B(?=(\d{3})+(?!\d))/g, ","); return s; };
        const dur = 1200, t0 = performance.now();
        const step = (t) => {
          const p = Math.min(1, (t - t0) / dur), eased = 1 - Math.pow(1 - p, 3);
          el.textContent = fmt(fromN + (toN - fromN) * eased);
          if (p < 1) requestAnimationFrame(step); else el.textContent = to;
        };
        requestAnimationFrame(step);
      };
      cio = new IntersectionObserver((entries) => entries.forEach((en) => { if (en.isIntersecting) { animate(en.target); cio.unobserve(en.target); } }), { rootMargin: "0px 0px -8% 0px", threshold: 0.3 });
      counters.forEach((e) => cio.observe(e));
    }
    return () => { io.disconnect(); cio?.disconnect(); };
  }, [title]);
}
