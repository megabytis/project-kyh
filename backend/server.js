import express from "express";
import cors from "cors";
import mongoose from "mongoose";
require("dotenv").config();

import chatRoute from "./routes/chat.js";
import sessionRoute from "./routes/session.js";
import connectDB from "./db/mongo.js";

const app = express();
app.use(cors());
app.use(express.json());

// routes
app.use("/api/chat", chatRoute);
app.use("/api/chat", sessionRoute);

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
