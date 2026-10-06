import { lazy } from "react";

// One entry per captured page. Add a page by adding its component here.
export const routes = [
  { path: "/", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/HomePage.jsx")) },
  { path: "/about", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/About.jsx")) },
  { path: "/blog", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/Blog.jsx")) },
  { path: "/customers", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/Customers.jsx")) },
  { path: "/careers", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/Careers.jsx")) },
  { path: "/contact", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/Contact.jsx")) },
  { path: "/contact/sales", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/ContactSales.jsx")) },
  { path: "/legal/terms-of-service", title: "Terms of Service - Vectura", Page: lazy(() => import("./pages/LegalTermsOfService.jsx")) },
  { path: "/legal/privacy", title: "Privacy Policy - Vectura", Page: lazy(() => import("./pages/LegalPrivacy.jsx")) },
  { path: "/blog/what-we-hear-when-we-talk-to-finance-teams", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/BlogWhatWeHear.jsx")) },
  { path: "/blog/from-source-of-truth-to-source-of-action", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/BlogFromSourceOf.jsx")) },
  { path: "/blog/agents-that-learn-how-you-work", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/BlogAgentsThatLearn.jsx")) },
  { path: "/blog/from-aging-reports-to-cash-control", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/BlogFromAgingReports.jsx")) },
  { path: "/blog/when-software-becomes-a-teammate", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/BlogWhenSoftwareBecomes.jsx")) },
  { path: "/blog/how-to-choose-the-right-collections-software", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/BlogHowToChoose.jsx")) },
  { path: "/blog/why-collections-software-keeps-failing-finance-teams", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/BlogWhyCollectionsSoftware.jsx")) },
  { path: "/blog/how-ai-agents-are-transforming-ar-and-collections", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/BlogHowAiAgents.jsx")) },
  { path: "/contact/support", title: "Exante: AI Teammate for Collections", Page: lazy(() => import("./pages/ContactSupport.jsx")) },
];
export const ROUTE_SET = new Set(routes.map((r) => r.path));
