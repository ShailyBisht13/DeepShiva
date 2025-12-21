import React, { useState } from "react";
import "./chatinput.css";
import QRScanner from "./qrscanner";

export default function ChatInput({ onSend, placeholder, language, onImageUpload }) {
  const [text, setText] = useState("");
  const [showQR, setShowQR] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  /* ---------- SEND MESSAGE ---------- */
  const send = () => {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  /* ---------- FILE UPLOAD ---------- */
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setUploadSuccess(false);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:5000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Server error");

      const data = await res.json();

      if (onImageUpload) {
        onImageUpload(data.filePath);
      }
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 3000);
    } catch (err) {
      alert("Upload failed: " + err.message);
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  /* ---------- VOICE INPUT ---------- */
  const handleMic = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Speech recognition not supported");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.lang =
      language === "hi"
        ? "hi-IN"
        : language === "bn"
          ? "bn-IN"
          : language === "mr"
            ? "mr-IN"
            : "en-US";

    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onresult = (event) => {
      setText(event.results[0][0].transcript);
    };

    recognition.start();
  };

  return (
    <>
      {showQR && (
        <QRScanner
          onScan={(data) => {
            if (!data) return;
            if (data.startsWith("http://") || data.startsWith("https://")) {
              window.open(data, "_blank");
            } else {
              setText(data);
            }
            setShowQR(false);
          }}
          onClose={() => setShowQR(false)}
        />
      )}

      <div className="chat-input-bar">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={placeholder}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />

        <label className="icon-btn" title="Attach Image">
          {isUploading ? "⏳" : uploadSuccess ? "✅" : "📎"}
          <input
            type="file"
            accept="image/*"
            hidden
            onChange={handleFileChange}
            disabled={isUploading}
          />
        </label>

        <button className="icon-btn" onClick={() => setShowQR(true)} title="Scan QR">
          📷
        </button>

        <button className="send-btn" onClick={send}>
          Send
        </button>

        <button
          className="icon-btn"
          onClick={handleMic}
          title="Speak"
        >
          🎤
        </button>
      </div>
    </>
  );
}