import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

function openIteration1() {
  fireEvent.click(
    screen.getByRole("button", { name: /Iteration 1 — Word context/i })
  );
}

describe("App", () => {
  it("shows prototype hub with iteration buttons", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Douyatte" })).not.toBeNull();
    expect(
      screen.getByRole("button", { name: /Iteration 1 — Word context/i })
    ).not.toBeNull();
    expect(
      screen.getByRole("button", { name: /Iteration 2 — New feature/i })
    ).not.toBeNull();
  });

  it("opens iteration 1 from the hub", () => {
    render(<App />);
    openIteration1();
    expect(screen.getByRole("heading", { name: "Word context" })).not.toBeNull();
    expect(screen.getByPlaceholderText("例: 断る")).not.toBeNull();
  });

  it("keeps romaji and english hidden by default in iteration 1", () => {
    render(<App />);
    openIteration1();
    expect(screen.queryByLabelText("Romaji")).toBeNull();
    expect(screen.queryByLabelText("English")).toBeNull();
  });

  it("shows analyze button and accepts user input in iteration 1", () => {
    render(<App />);
    openIteration1();
    const input = screen.getByPlaceholderText("例: 断る");
    fireEvent.change(input, { target: { value: "断る" } });
    expect((input as HTMLInputElement).value).toBe("断る");
    expect(screen.getByRole("button", { name: "Analyze" })).not.toBeNull();
  });

  it("returns to hub from iteration 1", () => {
    render(<App />);
    openIteration1();
    fireEvent.click(screen.getByRole("button", { name: "Back" }));
    expect(screen.getByRole("heading", { name: "Douyatte" })).not.toBeNull();
  });
});
