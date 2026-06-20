#!/usr/bin/env node
const crypto = require("crypto");
const fs = require("fs");

function normalizeText(text) {
  return String(text).replace(/\r\n/g, "\n").replace(/\r/g, "\n");
}

function parseScalar(value) {
  const trimmed = value.trim();
  if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
    const body = trimmed.slice(1, -1).trim();
    return body ? body.split(",").map((item) => item.trim()) : [];
  }
  return trimmed.replace(/^"(.*)"$/, "$1");
}

function parseFrontmatter(text) {
  const normalized = normalizeText(text);
  if (!normalized.startsWith("---\n")) {
    return [{}, normalized];
  }
  const end = normalized.indexOf("\n---\n", 4);
  if (end === -1) {
    return [{}, normalized];
  }
  const meta = {};
  const lines = normalized.slice(4, end).split("\n");
  let current = null;
  for (const line of lines) {
    if (!line.trim()) continue;
    if (!line.startsWith(" ") && line.includes(":")) {
      const idx = line.indexOf(":");
      const key = line.slice(0, idx).trim();
      const value = line.slice(idx + 1);
      if (value.trim() === "") {
        meta[key] = [];
        current = key;
      } else {
        meta[key] = parseScalar(value);
        current = null;
      }
    } else if (current && line.trim().startsWith("- ")) {
      meta[current].push(parseScalar(line.trim().slice(2)));
    }
  }
  return [meta, normalized.slice(end + 5)];
}

function canonicalBody(text) {
  return parseFrontmatter(text)[1];
}

function bodyHash(body) {
  return crypto.createHash("sha256").update(normalizeText(body), "utf8").digest("hex");
}

function parseFile(path) {
  const [frontmatter, body] = parseFrontmatter(fs.readFileSync(path, "utf8"));
  return {
    path,
    type: frontmatter.type,
    title: frontmatter.title,
    aliases: frontmatter.aliases || [],
    relations: frontmatter.relations || [],
    frontmatter,
    body,
  };
}

function main(argv) {
  const [command, ...args] = argv;
  if (command === "parse") {
    for (const file of args) {
      console.log(JSON.stringify(parseFile(file), null, 2));
    }
    return 0;
  }
  if (command === "hash") {
    for (const file of args) {
      console.log(bodyHash(canonicalBody(fs.readFileSync(file, "utf8"))));
    }
    return 0;
  }
  console.error("usage: cairn-js <parse|hash> <file...>");
  return 2;
}

if (require.main === module) {
  process.exitCode = main(process.argv.slice(2));
}

module.exports = { parseFrontmatter, canonicalBody, bodyHash, parseFile, main };
