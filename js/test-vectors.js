const fs = require("fs");
const path = require("path");
const { canonicalBody, bodyHash } = require("./cairn");

const vectors = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "test-vectors", "hash-vectors.json"), "utf8"));

for (const vector of vectors) {
  const body = canonicalBody(vector.document);
  if (body !== vector.canonical_body) {
    throw new Error(`${vector.name}: canonical body mismatch`);
  }
  const digest = bodyHash(body);
  if (digest !== vector.sha256) {
    throw new Error(`${vector.name}: hash mismatch ${digest} !== ${vector.sha256}`);
  }
}

console.log(`ok ${vectors.length} hash vectors`);
