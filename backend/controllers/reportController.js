import axios from "axios";
import Session from "../models/Session.js";

const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";

export const getWeeklyReport = async (req, res) => {
  try {
    const { userId } = req.query;
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    const sessions = await Session.find({
      userId,
      updatedAt: { $gte: sevenDaysAgo },
    }).sort({ date: 1 });

    const analysis = await axios.post(
      `${FASTAPI_URL}/analyze`,
      { sessions },
      {
        timeout: 30000,
      },
    );
    res.status(200).json(analysis.data);
  } catch (error) {
    console.error("Weekly report error:", error.message);
    res.status(500).json({ error: "Failed to generate weekly report" });
  }
};
