import { sendMessage } from "../services/chatService";
import React, { useEffect, useState } from "react";
import Sidebar from "../components/sidebar";
import ChatInput from "../components/chatinput";
import MessageBubble from "../components/messagebubble";
import "./chatpage.css";

/* ---------- TEXT DICTIONARY ---------- */
const TEXT = {
  en: {
    appName: "DeepShiva",
    newChat: "+ New Chat",
    chat: "Chat",
    title: "DeepShiva Chat",
    subtitle: "Spiritual tourism assistant",
    greeting: "🙏 Namaste, I am DeepShiva. How can I assist you?",
    placeholder:
      "Ask about temples, meditation, yoga, or your spiritual journey...",
    serverError: "Server error",
    typing: "DeepShiva is typing...",
  },

  hi: {
    appName: "दीपशिवा",
    newChat: "+ नया चैट",
    chat: "चैट",
    title: "दीपशिवा चैट",
    subtitle: "आध्यात्मिक पर्यटन सहायक",
    greeting: "🙏 नमस्ते, मैं दीपशिवा हूँ। मैं आपकी कैसे सहायता कर सकता हूँ?",
    placeholder:
      "मंदिर, ध्यान, योग या आध्यात्मिक यात्रा के बारे में पूछें...",
    serverError: "सर्वर से कनेक्शन नहीं हो पाया",
    typing: "दीपशिवा लिख रहा है...",
  },

  bn: {
    appName: "দীপশিবা",
    newChat: "+ নতুন চ্যাট",
    chat: "চ্যাট",
    title: "দীপশিবা চ্যাট",
    subtitle: "আধ্যাত্মিক পর্যটন সহকারী",
    greeting: "🙏 নমস্কার, আমি দীপশিবা। আমি কীভাবে আপনাকে সাহায্য করতে পারি?",
    placeholder:
      "মন্দির, ধ্যান, যোগ বা আধ্যাত্মিক যাত্রা সম্পর্কে জিজ্ঞাসা করুন...",
    serverError: "সার্ভারের সাথে সংযোগ ব্যর্থ হয়েছে",
    typing: "দীপশিবা টাইপ করছে...",
  },

  mr: {
    appName: "दीपशिवा",
    newChat: "+ नवीन चॅट",
    chat: "चॅट",
    title: "दीपशिवा चॅट",
    subtitle: "आध्यात्मिक पर्यटन सहाय्यक",
    greeting:
      "🙏 नमस्कार, मी दीपशिवा आहे. मी तुम्हाला कशी मदत करू शकतो?",
    placeholder:
      "मंदिरे, ध्यान, योग किंवा आध्यात्मिक प्रवासाबद्दल विचारा...",
    serverError: "सर्व्हरशी कनेक्शन अयशस्वी",
    typing: "दीपशिवा टाइप करत आहे...",
  },
};

/* ---------- SUGGESTED QUESTIONS ---------- */
const SUGGESTIONS = {
  en: [
    "Tell me about Kedarnath temple",
    "Guide me a short meditation",
    "Best spiritual places in Uttarakhand",
    "Explain Mahashivratri",
  ],
  hi: [
    "केदारनाथ मंदिर के बारे में बताइए",
    "एक छोटा ध्यान अभ्यास बताइए",
    "उत्तराखंड के प्रमुख तीर्थ स्थल",
    "महाशिवरात्रि का महत्व समझाइए",
  ],
  bn: ["নিকটবর্তী শিব মন্দির", "ধ্যানের উপকারিতা", "যোগ আসন", "তীর্থযাত্রা"],
  mr: ["जवळची शिव मंदिरे", "ध्यानाचे फायदे", "योग आसने", "तीर्थयात्रा"],
};

export default function ChatPage() {
  /* ---------- STATE ---------- */
  const [language, setLanguage] = useState("en");
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);

  const t = TEXT[language] || TEXT.en;
  const token = localStorage.getItem("token");

  /* ---------- CREATE FIRST CHAT ---------- */
  const createFirstChat = () => {
    const id = Date.now().toString();
    setConversations([
      {
        id,
        title: "Chat 1",
        messages: [{ from: "bot", text: t.greeting }],
      },
    ]);
    setActiveId(id);
  };
  const [hasLoaded, setHasLoaded] = useState(false);

  useEffect(() => {
    if (!token) {
      // 👤 Guest → load from localStorage
      const local = JSON.parse(localStorage.getItem("guest_chats") || "[]");
      if (local.length > 0) {
        setConversations(local);
        setActiveId(local[0].id);
      } else {
        createFirstChat();
      }
      setHasLoaded(true);
      return;
    }

    // 🔐 Logged-in user → load from backend
    fetch("http://localhost:5000/api/chats/load", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Load failed");
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setConversations(data);
          setActiveId(data[0].id);
        } else {
          createFirstChat();
        }
        setHasLoaded(true); // 🟢 ONLY SAVE AFTER SUCCESSFUL LOAD
      })
      .catch((err) => {
        console.error("Load failed:", err);
        alert("Session expired or server down. Please log in again.");
        // Don't setHasLoaded(true) so auto-save won't wipe data
      });
    // eslint-disable-next-line
  }, [token]);

  // Create new chat
  const createNewChat = () => {
    const id = Date.now().toString();
    setConversations((prev) => [
      {
        id,
        title: `Chat ${prev.length + 1}`,
        messages: [{ from: "bot", text: t.greeting }],
      },
      ...prev,
    ]);
    setActiveId(id);
  };






  // Delete single conversation
  const deleteConversation = (id) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (id === activeId && conversations.length > 1) {
      setActiveId(conversations[1].id);
    }
  };

  // Auto-generate title from first user message
  const generateTitle = (text) =>
    text.split(" ").slice(0, 5).join(" ") + "...";
  /* ---------- AUTO SAVE CHATS ---------- */
  useEffect(() => {
    if (!hasLoaded) return; // 🔴 WAIT UNTIL INITIAL LOAD DONE

    if (!token) {
      // Guest → save to localStorage
      localStorage.setItem(
        "guest_chats",
        JSON.stringify(conversations)
      );
      return;
    }

    // Logged-in user → save to backend
    fetch("http://localhost:5000/api/chats/save", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ conversations }),
    }).catch((err) => {
      console.error("Auto-save failed:", err.message);
    });
  }, [conversations, token, hasLoaded]);


  /* ---------- SEND MESSAGE ---------- */
  const [attachedImage, setAttachedImage] = useState(null);

  const sendToBackend = async (text, imgPath = null) => {
    const active = conversations.find((c) => c.id === activeId);
    if (!active) return;

    // Use passed imgPath or the state variable
    const actualImage = imgPath || attachedImage;

    const userMsg = actualImage
      ? `${text} [Image attached]`
      : text;

    const updatedMessages = [...active.messages, { from: "user", text: userMsg }];

    setConversations((prev) =>
      prev.map((c) =>
        c.id === activeId ? { ...c, messages: updatedMessages } : c
      )
    );

    setIsTyping(true);

    try {
      const data = await sendMessage(text, language, actualImage);

      // Clear attached image after sending
      setAttachedImage(null);

      setConversations((prev) =>
        prev.map((c) =>
          c.id === activeId
            ? {
              ...c,
              messages: [
                ...updatedMessages,
                {
                  from: "bot",
                  text: data.reply,
                  audio_url: data.audio_url // ✅ Store audio URL for player
                },
              ],
            }
            : c
        )
      );
    } catch {
      setConversations((prev) =>
        prev.map((c) =>
          c.id === activeId
            ? {
              ...c,
              messages: [
                ...updatedMessages,
                { from: "bot", text: t.serverError },
              ],
            }
            : c
        )
      );
    } finally {
      setIsTyping(false);
    }
  };


  const activeConversation = conversations.find((c) => c.id === activeId);

  return (
    <div className="ds-layout">
      <Sidebar
        conversations={conversations}
        onSelectConversation={setActiveId}
        onNewChat={createNewChat}
        onDeleteConversation={deleteConversation}
        language={language}
        text={TEXT[language]}
      />

      <div className="ds-chat">
        <div className="ds-chat-header">
          <div>
            <h2>{t.title}</h2>
            <p>{t.subtitle}</p>
          </div>

          <select
            className="lang-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="bn">Bengali</option>
            <option value="mr">Marathi</option>
          </select>
        </div>

        <div className="ds-chat-messages">
          {activeConversation?.messages.map((m, i) => (
            <MessageBubble
              key={i}
              message={m}
              language={language}
            />
          ))}
          {isTyping && <div className="typing-indicator">{t.typing}</div>}
        </div>

        {activeConversation?.messages.length === 1 && (
          <div className="suggestions">
            {SUGGESTIONS[language].map((q, i) => (
              <button
                key={i}
                className="suggestion-btn"
                onClick={() => sendToBackend(q)}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {attachedImage && (
          <div className="attached-indicator">
            📎 Image attached: {attachedImage.split(/[\\/]/).pop()}
            <button onClick={() => setAttachedImage(null)}>✕</button>
          </div>
        )}

        <ChatInput
          onSend={sendToBackend}
          placeholder={t.placeholder}
          language={language}
          onImageUpload={setAttachedImage}
        />
      </div>
    </div>
  );
}
