import fs from "node:fs/promises";
import satori from "satori";
import sharp from "sharp";
import path from "node:path";

async function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => {
      try {
        resolve(JSON.parse(data));
      } catch (err) {
        reject(new Error(`Invalid JSON on stdin: ${err.message}`));
      }
    });
    process.stdin.on("error", reject);
  });
}

async function generateImage(data) {
  const {
    title = "Hello Satori!",
    subtitle = "",
    backgroundColor = "#ffffff",
    textColor = "#000000",
    width = 1200,
    height = 630,
    outputFile = "output.png",
    fontFile = "node_modules/geist/dist/fonts/geist-sans/Geist-Regular.ttf",
  } = data;

  const fontData = await fs.readFile(path.resolve(process.cwd(), fontFile));

  const svg = await satori(
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        width: "100%",
        backgroundColor,
        alignItems: "center",
        justifyContent: "center",
        padding: "40px",
        boxSizing: "border-box",
      }}
    >
      <h1
        style={{
          fontSize: 60,
          color: textColor,
          margin: 0,
          textAlign: "center",
        }}
      >
        {title}
      </h1>
      {subtitle && (
        <p
          style={{
            fontSize: 30,
            color: textColor,
            opacity: 0.7,
            marginTop: 20,
            textAlign: "center",
          }}
        >
          {subtitle}
        </p>
      )}
    </div>,
    {
      width,
      height,
      fonts: [
        {
          name: "Geist",
          data: fontData,
          weight: 400,
          style: "normal",
        },
      ],
    },
  );

  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  await fs.writeFile(outputFile, pngBuffer);
  console.error(`Image saved to ${outputFile}`);
}

readStdin()
  .then(generateImage)
  .catch((err) => {
    console.error(err.message);
    process.exit(1);
  });
