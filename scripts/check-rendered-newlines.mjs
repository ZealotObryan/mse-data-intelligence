import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve("src/app");
const extensions = new Set([".tsx", ".ts", ".jsx", ".js"]);
const offenders = [];

async function scan(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const filePath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      await scan(filePath);
      continue;
    }
    if (!extensions.has(path.extname(entry.name))) continue;
    const source = await readFile(filePath, "utf8");
    // Catch the exact two-character escape sequence when it appears as
    // rendered JSX text, including standalone JSX expression strings.
    const hasLiteralTextNode = source.includes(">\\\\n<");
    const hasLiteralExpression = source.includes('{"\\\\n"}') || source.includes("{'\\\\n'}");
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
