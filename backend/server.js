import express from "express";
import cors from "cors";
import dotenv from "dotenv";
dotenv.config();

import chatRoute from "./routes/chat.js";
import sessionRoute from "./routes/session.js";
import reportRoute from "./routes/report.js";
import connectDB from "./db/mongo.js";

const app = express();
app.use(cors());
app.use(express.json());

// routes
app.use("/api/chat", chatRoute);
app.use("/api/session", sessionRoute);
app.use("/api/report", reportRoute);

const PORT = process.env.PORT || 3000;
connectDB()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`✅ Backend running on port ${PORT}`);
    });
  })
  .catch((err) => {
    console.log("MongoDB conneciton error:", err);
  });
