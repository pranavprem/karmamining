import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import OneRingToRuleThemAll from "./js/pages/OneRingToRuleThemAll.jsx";
import "./index.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <OneRingToRuleThemAll />
  </StrictMode>
);
