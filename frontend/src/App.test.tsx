import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("App", () => {
  it("keeps romaji and english hidden by default", () => {
    render(<App />);
    expect(screen.queryByLabelText("Romaji")).toBeNull();
    expect(screen.queryByLabelText("English")).toBeNull();
  });

  it("shows analyze button and accepts user input", () => {
    render(<App />);
    const input = screen.getByPlaceholderText("例: 断る");
    fireEvent.change(input, { target: { value: "断る" } });
    expect((input as HTMLInputElement).value).toBe("断る");
    expect(screen.getByRole("button", { name: "Analyze" })).not.toBeNull();
  });
});
