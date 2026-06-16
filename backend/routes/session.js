import express from "express";
import { initSession } from "../controllers/sessionController.js";

const router = express.Router();

router.get("/", initSession);

export default router;
