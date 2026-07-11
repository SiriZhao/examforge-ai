import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { testLLMConnection } from "./api/client";
import { ReportView } from "./components/ReportView";
import type { GenerateReviewResponse } from "./api/client";

vi.mock("./api/client", async () => {
  const actual = await vi.importActual<typeof import("./api/client")>("./api/client");
  return {
    ...actual,
    testLLMConnection: vi.fn(),
    uploadFiles: vi.fn(),
    createGenerateReviewJob: vi.fn(),
    getGenerateReviewJob: vi.fn(),
  };
});

const baseResult: GenerateReviewResponse = {
  markdown: "# 示例",
  download_path: "/download/demo.md",
  download_links: { md: "/download/demo.md", docx: "/download/demo.docx" },
  anki_csv_download_path: "/download/demo-anki.csv",
  export_format: "md",
  report_source: "rule_based",
  llm_status: "disabled",
  fallback_used: false,
  llm_error: null,
  review_report: {
    title: "示例报告",
    summary: "已识别考试信号。",
    generated_at: "2026-06-07T00:00:00",
    chapters: [
      {
        chapter: "第一章",
        importance: 95,
        material_frequency: 8,
        past_exam_frequency: 5,
        weighted_score: 95,
        keywords: ["光合作用"],
        formulas: [],
        question_types: ["概念辨析题"],
        examples: [],
        frequency: 2,
        review_advice: "优先复习。",
      },
    ],
    study_units: [],
    question_types: [],
    past_exam_analysis: {
      summary: "识别出 1 个类似往年题的文件。",
      detected_files: [
        {
          filename: "demo_past_exam.md",
          confidence: 90,
          question_count: 4,
          question_types: ["概念辨析题"],
          matched_chapters: ["第一章"],
        },
      ],
      high_frequency_topics: [
        {
          topic: "光合作用",
          chapter: "第一章",
          frequency: 3,
          question_types: ["概念辨析题"],
          keywords: ["ATP"],
        },
      ],
    },
    review_order: [{ chapter: "第一章", importance: 95, reason: "往年题命中较多。" }],
    sprint_plans: [{ days: 1, title: "1 天冲刺", schedule: ["复习第一章。"] }],
    mock_exam: {
      title: "模拟卷",
      questions: [
        {
          question_type: "概念辨析题",
          question: "以下说法正确的是？",
          answer: "A",
          chapter: "第一章",
          concept: "光合作用",
        },
      ],
    },
    anki_cards: [{ front: "ATP 是什么？", back: "能量载体。", tags: "chapter_1" }],
    high_frequency_points: ["第一章：光合作用"],
    sprint_checklist: ["复习重点章节。"],
    low_priority: [],
    insufficient_materials: [],
  },
};

describe("App", () => {
  beforeEach(() => {
    vi.mocked(testLLMConnection).mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("首页可渲染，并默认使用 DeepSeek deepseek-v4-flash", () => {
    render(<App />);

    expect(screen.getByText("CampusForge")).toBeInTheDocument();
    fireEvent.click(screen.getAllByText(/高级设置|楂樼骇璁剧疆/)[0]);
    expect(screen.getByDisplayValue("deepseek-v4-flash")).toBeInTheDocument();
  });

  it("点击测试大模型连接会调用 /api/llm/test 并显示失败详情", async () => {
    vi.mocked(testLLMConnection).mockResolvedValue({
      ok: false,
      provider: "DeepSeek",
      model: "deepseek-v4-flash",
      error: {
        code: "MODEL_NOT_FOUND",
        message: "大模型调用失败：模型名称可能不存在或当前账号无权限。",
        suggestion: "当前 DeepSeek 模型名称可能不可用。建议尝试 deepseek-v4-flash。",
      },
    });

    render(<App />);
    fireEvent.click(screen.getAllByText(/高级设置|楂樼骇璁剧疆/)[0]);
    fireEvent.click(screen.getByRole("button", { name: /测试大模型连接|娴嬭瘯澶фā鍨嬭繛鎺/ }));

    await waitFor(() => expect(testLLMConnection).toHaveBeenCalledTimes(1));
    expect(await screen.findByText(/MODEL_NOT_FOUND/)).toBeInTheDocument();
    expect(screen.getAllByText(/deepseek-v4-flash/).length).toBeGreaterThan(0);
  });

  it("本地整理模式显示当前报告来源", () => {
    render(<ReportView exporting={null} onExport={() => undefined} result={baseResult} />);
    expect(screen.getByText("当前报告来源：本地整理模式")).toBeInTheDocument();
  });

  it("大模型成功显示 AI 深度整理", () => {
    render(
      <ReportView
        exporting={null}
        onExport={() => undefined}
        result={{ ...baseResult, report_source: "llm_enhanced", llm_status: "success" }}
      />,
    );
    expect(screen.getByText("当前报告来源：AI 深度整理")).toBeInTheDocument();
  });

  it("大模型失败显示本地安全底稿和结构化错误", () => {
    render(
      <ReportView
        exporting={null}
        onExport={() => undefined}
        result={{
          ...baseResult,
          report_source: "rule_based_with_llm_failed",
          llm_status: "failed",
          fallback_used: true,
          llm_error: {
            code: "TIMEOUT",
            message: "大模型请求超时。",
            suggestion: "请稍后重试。",
            provider: "DeepSeek",
            model: "deepseek-v4-flash",
          },
        }}
      />,
    );
    expect(screen.getByText("当前报告来源：本地安全底稿")).toBeInTheDocument();
    expect(screen.getByText("TIMEOUT")).toBeInTheDocument();
    expect(screen.getByText("请稍后重试。")).toBeInTheDocument();
  });

  it("点击去配置大模型会触发展开动作", () => {
    const open = vi.fn();
    render(<ReportView exporting={null} onExport={() => undefined} result={baseResult} onOpenLLMSettings={open} />);
    fireEvent.click(screen.getAllByRole("button", { name: "开启大模型增强" })[0]);
    expect(open).toHaveBeenCalledTimes(1);
  });
});
