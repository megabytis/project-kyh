import express from "express";
import { getWeeklyReport } from "../controllers/reportController.js";

const router = express.Router();

router.get("/", getWeeklyReport);

export default router;
