import { Suspense, useEffect } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { routes } from "./routes.js";

function ScrollToTop() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    if (!hash) { window.scrollTo(0, 0); return; }
    // A <Link> to "/#section" is handled by the router, so the browser never performs its own
    // scroll-to-id. Without this the URL changes and the page stays put — which is what the header
    // dropdown's "/#outreach-agent" style links do. The target may belong to a route that is still
    // loading (lazy pages, Suspense), so retry briefly before giving up.
    const id = decodeURIComponent(hash.slice(1));
    if (!id) return;
    // On a cold load the browser runs its own scroll-to-id before layout has settled and can land
    // tens of pixels off, so the target is re-asserted here until it actually sits at the top rather
    // than trusting wherever the browser left it.
    let raf = 0, tries = 0, settled = 0;
    const seek = () => {
      const el = document.getElementById(id);
      if (el) {
        const off = Math.round(el.getBoundingClientRect().top);
        if (Math.abs(off) <= 1) {
          if (++settled > 2) return;            // in place across a few frames — done
        } else {
          settled = 0;
          el.scrollIntoView({ behavior: tries < 2 ? "auto" : "smooth", block: "start" });
        }
      }
      if (++tries < 120) raf = requestAnimationFrame(seek);
    };
    raf = requestAnimationFrame(seek);
    return () => cancelAnimationFrame(raf);
  }, [pathname, hash]);
  return null;
}

export default function App() {
  const Home = routes[0].Page;
  return (
    <Suspense fallback={null}>
      <ScrollToTop />
      <Routes>
        {routes.map((r) => <Route key={r.path} path={r.path} element={<r.Page />} />)}
        <Route path="*" element={<Home />} />
      </Routes>
    </Suspense>
  );
}
