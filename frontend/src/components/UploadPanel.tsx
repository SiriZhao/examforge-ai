import { useState } from "react";

import { uploadFiles } from "../api/client";

export function UploadPanel() {
  const [files, setFiles] = useState<File[]>([]);
  const [status, setStatus] = useState("请选择文件开始。");

  async function handleUpload() {
    if (files.length === 0) {
      setStatus("请先选择至少一个文件。");
      return;
    }

    setStatus("正在上传...");

    try {
      const result = await uploadFiles(files);
      setStatus(result.message);
    } catch {
      setStatus("上传失败，请检查后端是否正在运行。");
    }
  }

  return (
    <section className="panel">
      <h2>上传学习材料</h2>
      <label className="dropzone">
        <span>
          {files.length > 0
            ? files.map((file) => file.name).join("、")
            : "拖拽或选择考试资料"}
        </span>
        <input
          hidden
          multiple
          type="file"
          accept=".pptx,.pdf,.docx,.png,.jpg,.jpeg"
          onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
        />
      </label>
      <div className="actions">
        <button type="button" onClick={handleUpload}>
          上传
        </button>
        <button className="secondary" type="button" onClick={() => setFiles([])}>
          清空
        </button>
      </div>
      <p>{status}</p>
    </section>
  );
}

