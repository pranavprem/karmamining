import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import OneRingToRuleThemAll from "./js/pages/OneRingToRuleThemAll.jsx";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

test("shows the class project shell", () => {
  render(<OneRingToRuleThemAll />);
  expect(
    screen.getByRole("heading", { name: "CMPE 255 Project" })
  ).toBeTruthy();
  expect(screen.getByText("Hit me with your Post ID")).toBeTruthy();
  expect(screen.getByText("CMPE 255 Project by Pranav")).toBeTruthy();
});

test("renders comments returned for a post id", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    text: async () =>
      JSON.stringify([{ comment: "excellent explanation", score: 12 }]),
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<OneRingToRuleThemAll />);
  fireEvent.change(screen.getByLabelText("Reddit post ID"), {
    target: { value: "abc123" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Show Me What you Got" }));
  expect(await screen.findByText("excellent explanation")).toBeTruthy();
  expect(screen.getByText("12")).toBeTruthy();
  expect(fetchMock).toHaveBeenCalledWith(
    "http://localhost:8080/combined/abc123"
  );
});

test("sample button calls the demo route", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    text: async () => JSON.stringify([{ comment: "sample row", score: 4 }]),
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<OneRingToRuleThemAll />);
  fireEvent.click(screen.getByRole("button", { name: "Try sample comments" }));
  expect(await screen.findByText("sample row")).toBeTruthy();
  expect(fetchMock).toHaveBeenCalledWith("http://localhost:8080/combined/demo");
  expect(screen.getByRole("heading", { name: "Sample comments" })).toBeTruthy();
});

test("shows the API error message", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      text: async () =>
        JSON.stringify({ error: "Missing Reddit credentials: REDDIT_CLIENT_ID" }),
    })
  );
  render(<OneRingToRuleThemAll />);
  fireEvent.change(screen.getByLabelText("Reddit post ID"), {
    target: { value: "abc123" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Show Me What you Got" }));
  expect(await screen.findByText(/Missing Reddit credentials/)).toBeTruthy();
});
