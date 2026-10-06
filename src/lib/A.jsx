import { Link } from "react-router-dom";
import { ROUTE_SET } from "../routes.js";

// Internal links go through the router when the target is one of the captured routes; everything else is a plain anchor.
export default function A({ href = "", children, ...props }) {
  const path = href.split(/[?#]/)[0].replace(/\/+$/, "") || "/";
  if (href.startsWith("/") && !href.startsWith("//") && ROUTE_SET.has(path)) return <Link to={href} {...props}>{children}</Link>;
  return <a href={href} {...props}>{children}</a>;
}
