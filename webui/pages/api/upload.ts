import type { NextApiRequest, NextApiResponse } from "next";
import formidable from "formidable";
import fs from "fs";

export const config = {
  api: { bodyParser: false },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }
  const form = formidable();
  form.parse(req, async (err, fields, files) => {
    if (err) {
      res.status(500).json({ error: "Failed to parse form" });
      return;
    }
    const file = Array.isArray(files.file) ? files.file[0] : files.file;
    if (!file) {
      res.status(400).json({ error: "No file uploaded" });
      return;
    }
    try {
      const stream = fs.createReadStream(file.filepath);
      const apiRes = await fetch(process.env.BACKEND_URL + "/rag/ingest/file", {
        method: "POST",
        headers: { "x-api-token": process.env.API_TOKEN || "" },
        body: stream,
      });
      const data = await apiRes.json();
      res.status(apiRes.status).json(data);
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });
}
