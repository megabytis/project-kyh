import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

dotenv.config();

import chatRoute from "./routes/chat.js";
import sessionRoute from "./routes/session.js";
import reportRoute from "./routes/report.js";
import connectDB from "./db/mongo.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json());

// Serve static client files
app.use(express.static(path.join(__dirname, "../client")));

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
