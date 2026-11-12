import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve("src/app");
const extensions = new Set([".tsx", ".ts", ".jsx", ".js"]);
const offenders = [];
const literalSlashN = String.fromCharCode(92) + "n";

async function scan(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const filePath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      await scan(filePath);
      continue;
    }
    if (!extensions.has(path.extname(entry.name))) continue;
    const source = await readFile(filePath, "utf8");
    const hasLiteralTextNode = source.includes(">" + literalSlashN + "<");
    const hasLiteralExpression =
      source.includes('{"' + literalSlashN + '"}') ||
      source.includes("{'" + literalSlashN + "'}");
    if (hasLiteralTextNode || hasLiteralExpression) {
      offenders.push(path.relative(process.cwd(), filePath));
    }
  }
}

await scan(root);
if (offenders.length) {
  console.error("Literal \\n text found in application JSX:", offenders.join(", "));
  process.exitCode = 1;
} else {
  console.log("No literal \\n text nodes found in application source.");
}
