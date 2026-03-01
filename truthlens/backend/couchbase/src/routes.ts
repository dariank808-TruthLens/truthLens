import { Router } from "express";
import { getCollection } from "./db";

const router = Router();

/**
 * Health check: service and DB availability
 */
router.get("/health", (_req, res) => {
  try {
    getCollection(); // throws if DB not initialized
    res.json({ status: "ok", db: "connected" });
  } catch {
    res.status(503).json({ status: "degraded", db: "disconnected" });
  }
});

/**
 * Save document
 */
router.post("/save", async (req, res) => {
  try {
    const { id, data } = req.body;

    await getCollection().upsert(id, data);

    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "save failed" });
  }
});

/**
 * Fetch document
 */
router.get("/get/:id", async (req, res) => {
  try {
    const result = await getCollection().get(req.params.id);
    res.json(result.content);
  } catch {
    res.status(404).json({ error: "not found" });
  }
});

/**
 * Delete document
 */
router.delete("/delete/:id", async (req, res) => {
  try {
    await getCollection().remove(req.params.id);
    res.json({ success: true });
  } catch (err: any) {
    console.error(err);

    // Couchbase SDK throws a DocumentNotFoundError when the key is missing.
    if (err?.name === "DocumentNotFoundError") {
      res.status(404).json({ error: "not found" });
    } else {
      res.status(500).json({ error: "delete failed" });
    }
  }
});

export default router;