import * as couchbase from "couchbase";
import dotenv from "dotenv";

dotenv.config();

let collection: couchbase.Collection;

export async function initDB() {
  console.log("⏳ Connecting to Couchbase...");
  const cluster = await couchbase.connect(
    process.env.CB_CONNECTION!,
    {
      username: process.env.CB_USERNAME,
      password: process.env.CB_PASSWORD,
      configProfile: "wanDevelopment",
    }
  );

  console.log("⏳ Waiting for cluster to be ready...");

  const bucket = cluster.bucket(process.env.CB_BUCKET!);
  collection = bucket.defaultCollection();

  console.log("✅ Couchbase connected!");
}

export function getCollection() {
  if (!collection) throw new Error("Database not initialized");
  return collection;
}