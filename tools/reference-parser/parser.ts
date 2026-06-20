import fs from "node:fs";
import yaml from "js-yaml";

type AnyMap = Record<string, any>;

function splitFrontmatter(text: string): [AnyMap, string] {
  const normalized = text.replace(/\r\n?/g, "\n");
  if (!normalized.startsWith("---\n")) return [{}, normalized];
  const end = normalized.indexOf("\n---\n", 4);
  if (end === -1) return [{}, normalized];
  const meta = (yaml.load(normalized.slice(4, end)) as AnyMap) || {};
  return [meta, normalized.slice(end + 5)];
}

export function parse(path: string) {
  const [meta, body] = splitFrontmatter(fs.readFileSync(path, "utf8"));
  return {
    path,
    type: meta.type,
    title: meta.title,
    aliases: meta.aliases || [],
    relations: meta.relations || [],
    frontmatter: meta,
    body,
  };
}

if (process.argv[1]?.endsWith("parser.ts")) {
  for (const file of process.argv.slice(2)) {
    console.log(JSON.stringify(parse(file), null, 2));
  }
}
