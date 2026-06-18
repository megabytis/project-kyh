import Session from "../models/Session.js";

export const initSession = async (req, res) => {
  try {
    const { userId } = req.query;
    if (!userId) return res.status(400).json({ error: "userId required!" });

    const today = new Date().toISOString().split("T")[0];

    let session = await Session.findOne({ userId, date: today });
    if (!session) {
      session = new Session({
        userId,
        date: today,
        conversationStage: "awaiting_category",
      });
      await session.save();
    }

    res.json({
      sessionId: session._id,
      stage: session.conversationStage,
      loggedMeals: session.loggedMeals,
    });
  } catch (err) {
    console.log("Session init error:", err.message);
    res.status(500).json({ error: "Failed to initialize session" });
  }
};
