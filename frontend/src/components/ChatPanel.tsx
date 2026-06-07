import { useState } from "react";

import {
  chat,
  generateMockExam,
  type ChatMessage,
  type MockExamQuestion,
  type ReviewReport,
} from "../api/client";

type ChatPanelProps = {
  reviewReport: ReviewReport | null;
};

const QUICK_PROMPTS = ["生成背诵卡片", "生成模拟题", "分析高频考点", "推荐优先复习章节"];

export function ChatPanel({ reviewReport }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [mockQuestions, setMockQuestions] = useState<MockExamQuestion[]>([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage(content: string) {
    if (!content.trim()) return;
    const nextMessages: ChatMessage[] = [...messages, { role: "user", content }];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);
    setStatus("");

    try {
      if (content === "生成模拟题" && reviewReport) {
        const result = await generateMockExam(reviewReport);
        setMockQuestions(result.questions);
        setMessages([
          ...nextMessages,
          { role: "assistant", content: result.message },
        ]);
      } else {
        const result = await chat({
          message: content,
          review_report: reviewReport,
          history: messages,
        });
        setMessages([...nextMessages, { role: "assistant", content: result.reply }]);
      }
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "请求失败，请稍后重试。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel chat-panel">
      <div className="section-header">
        <div>
          <p className="eyebrow">复习助手</p>
          <h2>交互式复习追问</h2>
        </div>
      </div>

      <div className="quick-actions">
        {QUICK_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            className="secondary"
            type="button"
            onClick={() => sendMessage(prompt)}
            disabled={loading}
          >
            {prompt}
          </button>
        ))}
      </div>

      <div className="chat-history">
        {messages.length === 0 ? (
          <p className="muted">生成报告后可以继续追问：怎么背、先复习哪里、哪些题型最容易考。</p>
        ) : (
          messages.map((message, index) => (
            <div className={`message ${message.role}`} key={index}>
              <span>{message.role === "user" ? "我" : "复习助手"}</span>
              <p>{message.content}</p>
            </div>
          ))
        )}
      </div>

      {mockQuestions.length > 0 && (
        <div className="mock-exam">
          <h3>模拟题</h3>
          {mockQuestions.map((item, index) => (
            <article key={`${item.chapter}-${index}`}>
              <strong>{index + 1}. {item.question}</strong>
              <p>答案：{item.answer}</p>
              <p>章节：{item.chapter}；考点：{item.concept}</p>
            </article>
          ))}
        </div>
      )}

      <form
        className="chat-form"
        onSubmit={(event) => {
          event.preventDefault();
          sendMessage(input);
        }}
      >
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="输入追问，例如：帮我安排 3 天冲刺计划"
        />
        <button type="submit" disabled={loading}>
          {loading ? "发送中..." : "发送"}
        </button>
      </form>
      {status && <p className="error-text">{status}</p>}
    </section>
  );
}
