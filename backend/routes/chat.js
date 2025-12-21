const express = require("express");
const axios = require("axios");
const path = require("path");
const Chat = require("../models/chat");
const auth = require("../middleware/auth");
const router = express.Router();

/**
 * GET /api/chat
 * Load latest conversations for the logged in user
 */
router.get("/", auth, async (req, res) => {
  try {
    const chat = await Chat.findOne({ userId: req.user.userId });
    res.json(chat || { conversations: [] });
  } catch (error) {
    console.error("Fetch chat error:", error);
    res.status(500).json({ error: "Could not fetch chats" });
  }
});

/**
 * POST /api/chat
 * Process message via AI server
 */
router.post("/", async (req, res) => {
  try {
    const { query, persona, language, imagePath } = req.body;

    if (!query) {
      return res.status(400).json({ error: "Query is required" });
    }

    // Resolve image path safely if present
    let absoluteImagePath = null;
    if (imagePath) {
      try {
        absoluteImagePath = path.resolve(imagePath);
      } catch (err) {
        console.error("Path resolution failed:", err.message);
      }
    }

    // Call Python AI server
    const aiUrl = "http://127.0.0.1:8000/ai";
    console.log(`[DEBUG] Calling AI Server at: ${aiUrl}`);

    const response = await axios.post(
      aiUrl,
      {
        query,
        persona: persona || "tourism",
        language: language || "en",
        image_path: absoluteImagePath,
      },
      {
        headers: { "Content-Type": "application/json" },
        timeout: 60000,
      }
    );

    const aiData = response.data;
    console.log(`[DEBUG] AI Response received. Intent: ${aiData.intent}`);
    let replyText = aiData.answer || aiData.reply || "No response from AI";

    // Format object responses (Weather, Monument, Toilet, Yoga)
    if (typeof replyText === "object") {
      if (aiData.intent === "weather") {
        replyText = `Weather in ${replyText.location}: ${replyText.temperature}, ${replyText.condition}. Humidity: ${replyText.humidity}.`;
      } else if (aiData.intent === "monument") {
        replyText = `Identified Monument: ${replyText.monument} (Confidence: ${replyText.confidence}%).`;
      } else if (aiData.intent === "toilet") {
        replyText = "Nearby toilets found: " + replyText.toilets.map(t => t.name).join(", ");
      } else if (aiData.intent === "yoga") {
        replyText = `Detected Pose: ${replyText.pose}. Feedback: ${replyText.feedback?.join(" ")}`;
      } else {
        replyText = JSON.stringify(replyText);
      }
    }

    return res.json({
      reply: replyText,
      ...aiData
    });

  } catch (error) {
    console.error("AI SERVER ERROR:", error.response?.data || error.message);
    return res.status(503).json({
      error: "AI service unavailable",
    });
  }
});

module.exports = router;