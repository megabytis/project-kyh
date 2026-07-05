import mongoose from "mongoose";

const sessionSchema = new mongoose.Schema(
  {
    userId: { type: String, required: true },
    date: { type: String, required: true },
    conversationStage: { type: String, default: "idle" },
    chosenMeal: { type: String, default: "" },
    loggedMeals: { type: [String], default: [] },
    meals: { type: mongoose.Schema.Types.Mixed, default: {} },
    workout: { type: mongoose.Schema.Types.Mixed, default: {} },
    chosenWorkoutType: { type: String, default: "" },
    others: { type: mongoose.Schema.Types.Mixed, default: {} },
    chosenOthersType: { type: String, default: "" },
    dailyTotals: { type: mongoose.Schema.Types.Mixed, default: {} },
    messages: { type: [Object], default: [] },
    botReply: { type: String, default: "" },
    feedback: { type: String, default: "" },
    plan: { type: String, default: "" },
  },
  { timestamps: true },
);

// Compound index: one session per user per day
sessionSchema.index({ userId: 1, date: 1 }, { unique: true });

export default mongoose.model("Session", sessionSchema);
