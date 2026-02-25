import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import routes from "./routes";
import { initDB } from "./db";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

async function start() {
  try {
    console.log("🌐 Starting DB connection...");
    await initDB(); // connect to Couchbase
    console.log("✅ DB connected, starting server...");

    app.use("/api", routes);

    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
      console.log(`🚀 Server running on port ${PORT}`);
    });
  } catch (err) {
    console.error("❌ Failed to start server:", err);
  }
}

start();