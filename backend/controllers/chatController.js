import axios from "axios";
import Session from "../models/Session.js";

const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";

export const handleChat = async (req, res) => {
  try {
    const { userId, message } = req.body;
    if (!userId || !message) {
      return res
        .status(400)
        .json({ reply: "userId and message required", stage: "idle" });
    }

    const today = new Date().toIsoString().split("T")[0];

    // 1. load or create session
    let session = await Session.findOne({ userId, date: today });
    if (!session) {
      session = new Session({
        userId,
        date: today,
        conversationStage: "awaiting_category",
      });
    }

    // 2. now updating with current message
    const state = session.toObject();
    state.user_input = message;
    delete state._id;
    delete state.__v;
    delete state.updatedAt;
    delete state.createdAt;

    // now sending state to FastAPI endpoint
    const response = await axios.post(`${FASTAPI_URL}/process`, state, {
      timeout: 30000,
    });
    const result = response.data;

    // now saving the updated state to MongoDB
    Object.assign(session, {
      conversationStage: { type: String, default: "idle" },
      chosenMeal: { type: String, default: "" },
      loggedMeals: { type: [String], default: [] },
      meals: { type: mongoose.Schema.Types.Mixed, default: {} },
      workout: { type: mongoose.Schema.Types.Mixed, default: {} },
      others: { type: mongoose.Schema.Types.Mixed, default: {} },
      dailyTotals: { type: mongoose.Schema.Types.Mixed, default: {} },
      messages: { type: [Object], default: [] },
      botReply: { type: String, default: "" },
      feedback: { type: String, default: "" },
      plan: { type: String, default: "" },
    });
    await session.save();

    // now returning to browser
    res.json({
      reply: session.botReply,
      stage: session.conversationStage,
    });
  } catch (error) {
    console.error("Chat error:", error.message);
    if (error.code === "ECONNREFUSED") {
      return res.status(503).json({
        reply: "Agent service is offline. Start the Python FastAPI server.",
        stage: "idle",
      });
    }
    res.status(500).json({
      reply: "Something went wrong. Please try again.",
      stage: "idle",
    });
  }
};
