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

    const today = new Date().toISOString().split("T")[0];

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
    const state = {
      user_id: session.userId,
      date: session.date,
      user_input: message,
      conversation_stage: session.conversationStage,
      chosen_meal: session.chosenMeal,
      logged_meals: session.loggedMeals,
      meals: session.meals,
      workout: session.workout,
      others: session.others,
      daily_totals: session.dailyTotals,
      messages: session.messages,
      bot_reply: session.botReply,
      feedback: session.feedback,
      plan: session.plan,
      weekly_report: "",
    };

    delete state._id;
    delete state.__v;
    delete state.updatedAt;
    delete state.createdAt;
    console.log(state);

    // now sending state to FastAPI endpoint
    const response = await axios.post(`${FASTAPI_URL}/process`, state, {
      timeout: 30000,
    });
    const result = response.data;

    // now saving the updated state to MongoDB
    Object.assign(session, {
      conversationStage: result.conversation_stage || "idle",
      chosenMeal: result.chosen_meal || "",
      loggedMeals: result.logged_meals || [],
      meals: result.meals || {},
      workout: result.workout || {},
      others: result.others || {},
      dailyTotals: result.daily_totals || {},
      messages: result.messages || [],
      botReply: result.bot_reply || "",
      feedback: result.feedback || "",
      plan: result.plan || "",
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
