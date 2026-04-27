const fs = require("fs");

const inputPath = "raw_prices.txt";
const outputPath = "real_estate_prices.csv";

let raw = fs.readFileSync(inputPath, "utf8");

// Répare le texte collé en une seule énorme ligne
raw = raw
  .replace(/(Prix de l'immobilier au m[²2]\s+)/g, "\n$1")
  .replace(/(Ces informations reflètent)/g, "\n$1")
  .replace(/(Quartier\s+Prix au m[²2])/g, "\n$1")
  .replace(/([a-zA-ZÀ-ÿ0-9')])\s+(-|[\d\s]+DH)\s+(-|[\d\s]+DH)/g, "$1\n$2 $3")
  .replace(/(-|[\d\s]+DH)\s+([A-ZÀ-Ý][a-zA-ZÀ-ÿ0-9'’() -]+)/g, "$1\n$2");

const lines = raw
  .split(/\r?\n/)
  .map(l => l.trim())
  .filter(Boolean);

let currentCity = "";
const rows = [];

function cleanPrice(value) {
  if (!value || value === "-") return "-";
  return value.replace(/\s/g, "").replace("DH", "").trim() || "-";
}

function isNoise(line) {
  return (
    line.includes("Ces informations") ||
    line.includes("Quartier") ||
    line.includes("Prix au m2") ||
    line.includes("Prix au m²") ||
    line.includes("Carte des prix au Maroc") ||
    line === "Ville"
  );
}

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];

  const cityMatch = line.match(/^Prix de l'immobilier au m[²2]\s+(.+)$/i);
  if (cityMatch) {
    currentCity = cityMatch[1].trim();
    continue;
  }

  if (!currentCity || isNoise(line)) continue;

  const next = lines[i + 1] || "";

  const twoPrices = next.match(/^(-|[\d\s]+DH)\s+(-|[\d\s]+DH)$/);
  if (twoPrices) {
    rows.push({
      city: currentCity,
      district: line,
      apartment: cleanPrice(twoPrices[1]),
      villa: cleanPrice(twoPrices[2]),
    });
    i++;
  }
}

const csv = [
  "city,district,apartment_price_per_m2,villa_price_per_m2",
  ...rows.map(r => {
    const city = `"${r.city.replace(/"/g, '""')}"`;
    const district = `"${r.district.replace(/"/g, '""')}"`;
    return `${city},${district},${r.apartment},${r.villa}`;
  })
].join("\n");

fs.writeFileSync(outputPath, csv, "utf8");

console.log("CSV créé :", outputPath);
console.log("Nombre de lignes :", rows.length);