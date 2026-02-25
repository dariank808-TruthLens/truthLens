import { Router } from "express";
import { getCollection } from "./db";

const router = Router();

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

export default router;