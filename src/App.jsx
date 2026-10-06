import { Suspense, useEffect } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { routes } from "./routes.js";

function ScrollToTop() {
  const { pathname, hash } = useLocation();
  useEffect(() => { if (!hash) window.scrollTo(0, 0); }, [pathname, hash]);
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
