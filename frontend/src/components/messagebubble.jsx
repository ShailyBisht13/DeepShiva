import React, { useEffect, useRef, useState } from "react";
import "./messagebubble.css";

const LANG_MAP = {
  en: "en-US",
  hi: "hi-IN",
  bn: "bn-IN",
  mr: "mr-IN",
};


export default function MessageBubble({ message, language, }) {
  const isUser = message.from === "user";
  const synthRef = useRef(window.speechSynthesis);
  const [voices, setVoices] = useState([]);

  /* ---------- SAFETY CHECK ---------- */
  if (!message || typeof message.text !== "string") {
    return null;
  }

  /* ---------- LOAD VOICES (important fix) ---------- */
  // useEffect(() => {
  //   if (!synthRef.current) return;

  //   const loadVoices = () => {
  //     setVoices(synthRef.current.getVoices());
  //   };

  //   loadVoices();
  //   synthRef.current.onvoiceschanged = loadVoices;

  //   return () => {
  //     synthRef.current.onvoiceschanged = null;
  //   };
  // }, []);

  /* ---------- SPEAK ---------- */
  const speakText = (text) => {
    if (message.audio_url) {
      // ✅ Use Server-Side TTS instead of browser synth
      const audio = new Audio(`http://localhost:5000${message.audio_url}`);
      audio.play().catch(err => console.error("Audio play failed:", err));
      return;
    }

    // Fallback to browser synthesis if no audio_url (rare now)
    if (!synthRef.current) return;
    const synth = synthRef.current;
    const langCode = LANG_MAP[language] || "en-US";
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    synth.cancel();
    synth.speak(utterance);
  };

  /* ---------- STOP ---------- */
  const stopSpeech = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
    }
  };

  return (

    <div className={`bubble-row ${isUser ? "user-row" : "bot-row"}`}>
      <div className={`bubble ${isUser ? "user" : "bot"}`}>
        <div className="bubble-text">{message.text}</div>


        {/* 🧘 Meditation Audio */}
        {message.audio_url && (
          <div className="meditation-player">
            <audio controls autoPlay src={`http://localhost:5000${message.audio_url}`}>
              Your browser does not support the audio element.
            </audio>
            <p className="meditation-hint">Enjoy your 1-minute meditation...</p>
          </div>
        )}

        {/* 🔊 TTS controls (bot only) */}
        {!isUser && !message.audio_url && (
          <div className="tts-controls">
            <button
              className="tts-btn"
              onClick={() => speakText(message.text)}
              title="Listen"
            >
              🔊
            </button>

            <button
              className="tts-btn stop"
              onClick={stopSpeech}
              title="Stop"
            >
              ⏹️
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
