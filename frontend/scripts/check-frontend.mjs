import { readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const htmlFiles = readdirSync(root)
  .filter((file) => file.endsWith(".html"))
  .map((file) => join(root, file));
const jsFiles = [];
const errors = [];

function walk(directory) {
  for (const entry of readdirSync(directory)) {
    const current = join(directory, entry);
    const stats = statSync(current);
    if (stats.isDirectory()) {
      walk(current);
    } else if (current.endsWith(".js")) {
      jsFiles.push(current);
    }
  }
}

function fail(message) {
  errors.push(message);
}

function isExternal(reference) {
  return /^(https?:|tel:|mailto:|#)/.test(reference);
}

function assertLocalReference(htmlPath, reference) {
  if (isExternal(reference) || !/\.(html|css|js|json)$/i.test(reference)) return;

  const cleanReference = reference.split("?")[0].split("#")[0];
  const target = normalize(join(dirname(htmlPath), cleanReference));
  if (!target.startsWith(root)) {
    fail(`${htmlPath}: reference outside frontend folder: ${reference}`);
    return;
  }
  try {
    statSync(target);
  } catch {
    fail(`${htmlPath}: missing local reference: ${reference}`);
  }
}

function checkHtml(htmlPath) {
  const html = readFileSync(htmlPath, "utf8");
  if (!/<title>[^<]+<\/title>/i.test(html)) {
    fail(`${htmlPath}: missing <title>`);
  }
  if (!/name="viewport"/i.test(html)) {
    fail(`${htmlPath}: missing viewport meta`);
  }

  const references = [...html.matchAll(/(?:src|href)="([^"]+)"/g)].map(
    (match) => match[1]
  );
  references.forEach((reference) => assertLocalReference(htmlPath, reference));

  if (!references.some((reference) => reference.endsWith("assets/js/config.js"))) {
    fail(`${htmlPath}: missing config.js include`);
  }
  if (!references.some((reference) => reference.endsWith("assets/js/api.js"))) {
    fail(`${htmlPath}: missing api.js include`);
  }
  if (!references.some((reference) => reference.endsWith("assets/js/ui.js"))) {
    fail(`${htmlPath}: missing ui.js include`);
  }
}

function checkJs(jsPath) {
  const source = readFileSync(jsPath, "utf8");
  try {
    new vm.Script(source, { filename: jsPath });
  } catch (error) {
    fail(`${jsPath}: ${error.message}`);
  }
}

walk(join(root, "assets"));
for (const htmlPath of htmlFiles) checkHtml(htmlPath);
for (const jsPath of jsFiles) checkJs(jsPath);

if (!htmlFiles.length) fail("No HTML page found in frontend folder.");

if (errors.length) {
  console.error("Frontend check failed:");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(
  `Frontend check OK: ${htmlFiles.length} HTML page(s), ${jsFiles.length} JS file(s).`
);
