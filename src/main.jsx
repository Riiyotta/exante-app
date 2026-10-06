import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./index.css";
import "./styles/sheets.css.js";

createRoot(document.getElementById("root")).render(<BrowserRouter><App /></BrowserRouter>);
