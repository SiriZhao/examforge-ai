import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

vi.mock("./api/client", async () => {
  const actual = await vi.importActual<typeof import("./api/client")>("./api/client");
  return { ...actual, ensureReviewWorkspace: vi.fn().mockResolvedValue(undefined), reviewApi: vi.fn(async () => ({})) };
});

afterEach(cleanup);

describe("ExamForge AI focused flow", () => {
  it("starts with review settings instead of a generic workspace", () => {
    render(<App />);
    expect(screen.getAllByText("创建复习项目").length).toBeGreaterThan(0);
    expect(screen.getByText("面向大学生期末考试的 AI 复习资料生成器")).toBeInTheDocument();
    expect(screen.queryByText("登录")).not.toBeInTheDocument();
  });

  it("offers browser-local BYOK configuration", () => {
    render(<App />);
    expect(screen.getByText("你的 AI 模型")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "测试连接" })).toBeInTheDocument();
    fireEvent.change(screen.getByPlaceholderText("例如：概率论"), { target: { value: "概率论" } });
    expect(screen.getByRole("button", { name: "创建复习项目" })).not.toBeDisabled();
  });
});
