import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

vi.mock("./api/client", async () => {
  const actual = await vi.importActual<typeof import("./api/client")>("./api/client");
  return { ...actual, platformRequest: vi.fn(async (path: string) => path === "/courses" || path === "/conversations" ? [] : {}) };
});

describe("Campus AI Workspace local mode", () => {
  beforeEach(() => localStorage.clear());
  afterEach(() => cleanup());
  it("opens without login and shows first-run guide", () => {
    render(<App />);
    expect(screen.getByText("你的个人 AI 学习与开发工作台")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "开始使用" }));
    expect(screen.getByRole("button", { name: "＋ 新建对话" })).toBeInTheDocument();
    expect(screen.queryByText("登录")).not.toBeInTheDocument();
  });
  it("offers browser-only BYOK settings", () => {
    localStorage.setItem("campus-ai-welcomed", "1");
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "设置" }));
    expect(screen.getAllByText(/API Key 只保存在当前浏览器/).length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "测试连接" })).toBeInTheDocument();
  });
});
