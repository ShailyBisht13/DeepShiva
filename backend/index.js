require("dotenv").config();

const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const uploads = require("./routes/uploads")
const authRoutes = require("./routes/auth");
const chatRoutes = require("./routes/chat");
const chatStorageRoutes = require("./routes/chats");
const app = express();
/* middleware */
app.use(cors());
app.use(express.json());
app.use("/uploads", express.static("uploads"));

/* routes */
app.use("/auth", authRoutes);
app.use("/api/chat", chatRoutes);
app.use("/api/chats", chatStorageRoutes);
app.use("/api/upload", uploads);

app.get("/health", (req, res) => {
  res.json({ status: "Backend is running fine ✅" });
});

app.get("/", (req, res) => {
  res.send("✅ Backend is running");
});

/* MongoDB */
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB connected"))
  .catch((err) => console.error(err.message));

/* server */
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});
