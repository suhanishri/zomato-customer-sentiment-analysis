const PptxGenJS = require("pptxgenjs");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_4x3";
pptx.author = "OpenAI Codex";
pptx.company = "OpenAI";
pptx.subject = "Project Review 2 presentation for Zomato sentiment analysis";
pptx.title = "Project Review 2 - Zomato Sentiment Analysis";
pptx.lang = "en-IN";
pptx.theme = {
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  lang: "en-IN",
};

const colors = {
  text: "000000",
  footer: "4F81BD",
  white: "FFFFFF",
  muted: "666666",
};

function addFooter(slide, pageNum) {
  slide.addText("VIT ONLINE MBA", {
    x: 3.25,
    y: 6.8,
    w: 3.5,
    h: 0.22,
    fontFace: "Calibri",
    fontSize: 10,
    color: colors.footer,
    align: "center",
    margin: 0,
  });

  slide.addText(`Slide ${String(pageNum).padStart(2, "0")}`, {
    x: 0.18,
    y: 7.02,
    w: 0.8,
    h: 0.16,
    fontFace: "Calibri",
    fontSize: 5.5,
    color: colors.muted,
    margin: 0,
  });
}

function addTitle(slide, title) {
  slide.addText(title, {
    x: 0.5,
    y: 0.32,
    w: 9,
    h: 0.7,
    fontFace: "Calibri",
    fontSize: 24,
    bold: false,
    color: colors.text,
    align: "center",
    margin: 0,
  });
}

function addBodyBullets(slide, bullets, opts = {}) {
  const runs = [];
  bullets.forEach((bullet, index) => {
    runs.push({
      text: bullet,
      options: {
        bullet: { indent: 16 },
        breakLine: index < bullets.length - 1,
      },
    });
  });

  slide.addText(runs, {
    x: opts.x ?? 0.85,
    y: opts.y ?? 1.55,
    w: opts.w ?? 8.25,
    h: opts.h ?? 4.9,
    fontFace: "Calibri",
    fontSize: opts.fontSize ?? 18,
    color: colors.text,
    margin: 0.05,
    breakLine: true,
    paraSpaceAfterPt: opts.paraSpaceAfterPt ?? 14,
    valign: "top",
  });
}

function addBodyText(slide, text, opts = {}) {
  slide.addText(text, {
    x: opts.x ?? 0.85,
    y: opts.y ?? 1.55,
    w: opts.w ?? 8.2,
    h: opts.h ?? 4.8,
    fontFace: "Calibri",
    fontSize: opts.fontSize ?? 18,
    color: colors.text,
    margin: 0.05,
    breakLine: true,
    paraSpaceAfterPt: opts.paraSpaceAfterPt ?? 12,
    valign: "top",
  });
}

function addStatBox(slide, title, lines, x, y, w, h) {
  slide.addShape(pptx.ShapeType.rect, {
    x,
    y,
    w,
    h,
    fill: { color: "F7F7F7" },
    line: { color: "D9D9D9", pt: 1 },
  });

  slide.addText(title, {
    x: x + 0.14,
    y: y + 0.12,
    w: w - 0.28,
    h: 0.24,
    fontFace: "Calibri",
    fontSize: 12,
    bold: true,
    color: colors.footer,
    margin: 0,
    align: "left",
  });

  slide.addText(lines.join("\n"), {
    x: x + 0.14,
    y: y + 0.42,
    w: w - 0.28,
    h: h - 0.56,
    fontFace: "Calibri",
    fontSize: 11.5,
    color: colors.text,
    margin: 0,
    breakLine: true,
    valign: "top",
  });
}

function addTableCell(slide, text, x, y, w, h, opts = {}) {
  slide.addShape(pptx.ShapeType.rect, {
    x,
    y,
    w,
    h,
    fill: { color: opts.fill || "FFFFFF" },
    line: { color: opts.lineColor || "D9D9D9", pt: 1 },
  });

  slide.addText(text, {
    x: x + 0.05,
    y: y + 0.04,
    w: w - 0.1,
    h: h - 0.08,
    fontFace: "Calibri",
    fontSize: opts.fontSize || 10,
    bold: opts.bold || false,
    color: opts.color || colors.text,
    align: opts.align || "center",
    valign: opts.valign || "mid",
    margin: 0.02,
    breakLine: true,
    fit: "shrink",
  });
}

function addFlowCard(slide, title, lines, x, y, w, h) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    fill: { color: "FFFFFF" },
    line: { color: "B8CCE4", pt: 1.2 },
  });

  slide.addShape(pptx.ShapeType.rect, {
    x: x + 0.22,
    y: y + 0.12,
    w: w - 0.44,
    h: 0.08,
    fill: { color: "DCE6F1" },
    line: { color: "DCE6F1", pt: 0.5 },
  });

  slide.addText(title, {
    x: x + 0.1,
    y: y + 0.28,
    w: w - 0.2,
    h: 0.24,
    fontFace: "Calibri",
    fontSize: 10.5,
    bold: true,
    color: colors.footer,
    align: "center",
    margin: 0,
  });

  slide.addText(lines.join("\n"), {
    x: x + 0.12,
    y: y + 0.58,
    w: w - 0.24,
    h: h - 0.7,
    fontFace: "Calibri",
    fontSize: 9.2,
    color: colors.text,
    align: "left",
    margin: 0.02,
    breakLine: true,
    fit: "shrink",
  });
}

// Slide 1
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };

  slide.addText("Project Review Presentation", {
    x: 1.25,
    y: 0.38,
    w: 7.5,
    h: 0.6,
    fontFace: "Calibri",
    fontSize: 28,
    color: colors.text,
    align: "center",
    margin: 0,
  });

  slide.addText("Sentiment Analysis of Zomato Play Store Reviews for Brand Strategy", {
    x: 1.35,
    y: 2.1,
    w: 7.25,
    h: 0.95,
    fontFace: "Calibri",
    fontSize: 22,
    color: colors.text,
    align: "center",
    margin: 0,
    fit: "shrink",
  });

  slide.addText("Name:\nSuhani Shrivastava\n\nRoll Number:\n24EMBA1442", {
    x: 0.7,
    y: 4.0,
    w: 2.35,
    h: 1.6,
    fontFace: "Calibri",
    fontSize: 14,
    color: colors.text,
    margin: 0,
    breakLine: true,
  });

  addFooter(slide, 1);
}

// Slide 2
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Project Work (Overall)");
  addBodyBullets(slide, [
    "Collected Zomato app reviews from the Google Play Store under relevant, rating-based, and newest retrieval modes.",
    "Merged the raw review pulls into one cleaned dataset after normalization, filtering, and duplicate removal.",
    "Assigned weak sentiment labels from ratings and standardized reviews into business themes such as delivery, refunds, pricing, support, and trust.",
    "Applied TF-IDF with Logistic Regression to study sentiment patterns at scale and compare class-level performance.",
    "Interpreted theme-wise results to identify the main customer pain points and the strongest brand-supporting experiences."
  ], { x: 0.82, y: 1.58, w: 8.15, h: 4.9, fontSize: 18 });
  addFooter(slide, 2);
}

// Slide 3
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Data Collection");

  slide.addText("Google Play review pulls were collected in parallel and then merged into one cleaned Zomato dataset.", {
    x: 0.72,
    y: 1.12,
    w: 8.0,
    h: 0.24,
    fontFace: "Calibri",
    fontSize: 11,
    color: colors.muted,
    align: "center",
    margin: 0,
  });

  addFlowCard(slide, "Relevant Reviews", [
    "Source folder:",
    "output_playstore_relevant_en",
    "",
    "Volume: 22,773",
    "Captures commonly surfaced feedback",
  ], 0.48, 1.5, 1.65, 1.7);

  addFlowCard(slide, "Rating-Sorted", [
    "Source folder:",
    "output_playstore_rating_en",
    "",
    "Volume: 15,942",
    "Captures high and low rating extremes",
  ], 2.35, 1.5, 1.65, 1.7);

  addFlowCard(slide, "Newest Pulls", [
    "Source folders:",
    "newest_en + newest_hi",
    "",
    "Volume: 2,882",
    "Adds recent and mixed-language feedback",
  ], 4.22, 1.5, 1.65, 1.7);

  slide.addShape(pptx.ShapeType.line, {
    x: 1.3,
    y: 3.38,
    w: 3.75,
    h: 0,
    line: { color: "B8CCE4", pt: 1.2 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 4.25,
    y: 3.38,
    w: 0,
    h: 0.2,
    line: { color: "B8CCE4", pt: 1.2 },
  });

  addFlowCard(slide, "Merge + Clean", [
    "Normalize text",
    "Remove duplicates",
    "Filter low-value noise",
    "Keep rating, year, theme, sentiment-ready fields",
  ], 3.22, 3.55, 2.05, 1.55);

  addFlowCard(slide, "Final Dataset", [
    "41,597 cleaned reviews",
    "26,277 pre-2024",
    "15,320 from 2024+",
    "41,419 English/mixed; 178 Hindi/mixed Hindi",
  ], 6.85, 1.75, 2.05, 1.85);

  addTableCell(slide, "Stage", 0.48, 5.25, 1.55, 0.36, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 10,
  });
  addTableCell(slide, "Tabular Explanation", 2.03, 5.25, 6.87, 0.36, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 10,
  });

  const collectionRows = [
    ["Collection", "Google Play Store reviews were collected under relevant, rating-based, and newest retrieval modes to reduce single-sort bias."],
    ["Cleaning", "Merged review pulls were deduplicated and normalized before analysis, preserving rating, text, year, recency bucket, and theme fields."],
    ["Outcome", "The result was one analysis-ready Zomato review base that could support sentiment modeling and later interpretation."],
  ];

  collectionRows.forEach((row, index) => {
    const y = 5.61 + index * 0.36;
    addTableCell(slide, row[0], 0.48, y, 1.55, 0.36, {
      fill: "F3F6FA",
      bold: true,
      align: "left",
      fontSize: 9.4,
    });
    addTableCell(slide, row[1], 2.03, y, 6.87, 0.36, {
      fill: "FFFFFF",
      align: "left",
      fontSize: 9.2,
    });
  });

  addFooter(slide, 3);
}

// Slide 4
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Data Pre-processing");

  slide.addText("The merged Play Store review pool was cleaned in stages before modeling and interpretation.", {
    x: 0.72,
    y: 1.02,
    w: 8.0,
    h: 0.24,
    fontFace: "Calibri",
    fontSize: 11,
    color: colors.muted,
    align: "center",
    margin: 0,
  });

  addTableCell(slide, "Step", 0.5, 1.45, 1.35, 0.42, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 10,
  });
  addTableCell(slide, "What We Did", 1.85, 1.45, 4.95, 0.42, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 10,
  });
  addTableCell(slide, "Effect on Data", 6.8, 1.45, 2.15, 0.42, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 10,
  });

  const prepRows = [
    ["Merge", "Combined cleaned review pulls from relevant, rating-based, newest English, and newest Hindi folders into one working file.", "46,193 rows before dedupe"],
    ["Normalize", "Converted text to lowercase, removed punctuation and special characters, and compacted repeated whitespace.", "Created comparable normalized text"],
    ["Dedupe by ID", "Removed exact repeated reviews using source review IDs after sorting by relevance score, thumbs-up count, and rating.", "41,657 rows after ID dedupe"],
    ["Dedupe by Text", "Removed repeated content using normalized text so the same review wording was not counted multiple times.", "41,597 rows after final dedupe"],
    ["Structure", "Retained rating, review text, year, recency bucket, theme label, and sentiment-ready fields for downstream analysis.", "Final analysis-ready dataset"],
  ];

  prepRows.forEach((row, index) => {
    const y = 1.87 + index * 0.68;
    addTableCell(slide, row[0], 0.5, y, 1.35, 0.68, {
      fill: "F3F6FA",
      bold: true,
      align: "left",
      fontSize: 9.8,
    });
    addTableCell(slide, row[1], 1.85, y, 4.95, 0.68, {
      fill: "FFFFFF",
      align: "left",
      fontSize: 9.3,
    });
    addTableCell(slide, row[2], 6.8, y, 2.15, 0.68, {
      fill: "FFFFFF",
      align: "center",
      fontSize: 9.3,
    });
  });

  addStatBox(slide, "Deduplication Logic", [
    "Priority sort:",
    "relevance score",
    "thumbs-up count",
    "rating score",
    "This kept the stronger row when duplicates appeared."
  ], 6.7, 5.1, 2.2, 1.45);

  addFooter(slide, 4);
}

// Slide 5
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Examples: Duplicates and Normalized Text");

  slide.addText("Real project examples from the merged Google Play review files and final master dataset.", {
    x: 0.7,
    y: 1.0,
    w: 8.1,
    h: 0.22,
    fontFace: "Calibri",
    fontSize: 10.8,
    color: colors.muted,
    align: "center",
    margin: 0,
  });

  slide.addText("Text Normalization Examples", {
    x: 0.58,
    y: 1.35,
    w: 3.1,
    h: 0.22,
    fontFace: "Calibri",
    fontSize: 12,
    bold: true,
    color: colors.footer,
    margin: 0,
  });

  addTableCell(slide, "Raw Review Text", 0.5, 1.62, 4.15, 0.38, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 9.6,
  });
  addTableCell(slide, "Normalized Text", 4.65, 1.62, 4.3, 0.38, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 9.6,
  });

  const normExamples = [
    [
      "I loved this app so much i loved its delivery and all.Its probably the best app to order the food...",
      "i loved this app so much i loved its delivery and all its probably the best app to order the food...",
    ],
    [
      "Such a bad customer service .....my order got cancelled and they didn't refund.....",
      "such a bad customer service my order got cancelled and they didn t refund ...",
    ],
  ];

  normExamples.forEach((row, index) => {
    const y = 2.0 + index * 0.78;
    addTableCell(slide, row[0], 0.5, y, 4.15, 0.78, {
      fill: "FFFFFF",
      align: "left",
      fontSize: 8.8,
    });
    addTableCell(slide, row[1], 4.65, y, 4.3, 0.78, {
      fill: "FFFFFF",
      align: "left",
      fontSize: 8.8,
    });
  });

  slide.addText("Duplicate Removal Examples", {
    x: 0.58,
    y: 3.72,
    w: 3.0,
    h: 0.22,
    fontFace: "Calibri",
    fontSize: 12,
    bold: true,
    color: colors.footer,
    margin: 0,
  });

  addTableCell(slide, "Duplicate Type", 0.5, 3.98, 1.45, 0.38, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 9.4,
  });
  addTableCell(slide, "Observed Example", 1.95, 3.98, 4.65, 0.38, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 9.4,
  });
  addTableCell(slide, "Decision", 6.6, 3.98, 2.35, 0.38, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 9.4,
  });

  const dupExamples = [
    [
      "Same review ID",
      "Record ID c9c028a3-4be2-44fd-934b-56a7aae70b10 appeared in newest_en, relevant_en, and rating_en with the same review content.",
      "Keep one row after priority sorting; remove repeated IDs.",
    ],
    [
      "Same normalized text",
      "\"Best app for food delivery\", \"Best app for food delivery...\", and \"Best app for food delivery\" from different pulls normalized to the same string.",
      "Keep one representative row; remove repeated wording.",
    ],
  ];

  dupExamples.forEach((row, index) => {
    const y = 4.36 + index * 0.9;
    addTableCell(slide, row[0], 0.5, y, 1.45, 0.9, {
      fill: "F3F6FA",
      align: "left",
      bold: true,
      fontSize: 9.1,
    });
    addTableCell(slide, row[1], 1.95, y, 4.65, 0.9, {
      fill: "FFFFFF",
      align: "left",
      fontSize: 8.9,
    });
    addTableCell(slide, row[2], 6.6, y, 2.35, 0.9, {
      fill: "FFFFFF",
      align: "left",
      fontSize: 8.9,
    });
  });

  slide.addText("Removal summary: 46,193 merged rows -> 41,657 after review-ID dedupe -> 41,597 after normalized-text dedupe.", {
    x: 0.62,
    y: 6.35,
    w: 8.1,
    h: 0.2,
    fontFace: "Calibri",
    fontSize: 10,
    bold: true,
    color: colors.text,
    align: "center",
    margin: 0,
  });

  addFooter(slide, 5);
}

// Slide 6
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "SentiLens Model Architecture");

  slide.addText("SentiLens is the tuned TF-IDF + Logistic Regression pipeline used for the final sentiment predictions.", {
    x: 0.72,
    y: 1.02,
    w: 8.05,
    h: 0.22,
    fontFace: "Calibri",
    fontSize: 10.8,
    color: colors.muted,
    align: "center",
    margin: 0,
  });

  addFlowCard(slide, "1. Input Review Text", [
    "Raw review sentence",
    "from Google Play dataset",
    "",
    "Complaint, praise, or mixed opinion",
  ], 0.45, 1.62, 1.78, 1.7);

  addFlowCard(slide, "2. TF-IDF Vectorizer", [
    "lowercase = True",
    "strip_accents = unicode",
    "word n-grams = 1 to 2",
    "min_df = 2",
    "max_features = 40,000",
  ], 2.45, 1.62, 1.85, 2.0);

  addFlowCard(slide, "3. Sparse Features", [
    "Each review becomes a",
    "weighted word-feature vector",
    "",
    "More informative terms",
    "receive stronger weights",
  ], 4.52, 1.62, 1.72, 1.8);

  addFlowCard(slide, "4. Logistic Regression", [
    "C = 2.5",
    "max_iter = 1500",
    "class_weight = balanced",
    "random_state = 42",
  ], 6.45, 1.62, 1.78, 1.8);

  slide.addShape(pptx.ShapeType.line, {
    x: 2.23, y: 2.46, w: 0.22, h: 0,
    line: { color: "B8CCE4", pt: 1.4 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 4.3, y: 2.46, w: 0.22, h: 0,
    line: { color: "B8CCE4", pt: 1.4 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 6.24, y: 2.46, w: 0.21, h: 0,
    line: { color: "B8CCE4", pt: 1.4 },
  });

  addTableCell(slide, "Output Class", 0.55, 4.1, 1.5, 0.4, {
    fill: "DCE6F1", lineColor: "B8CCE4", bold: true, fontSize: 9.6,
  });
  addTableCell(slide, "What SentiLens Produces", 2.05, 4.1, 3.8, 0.4, {
    fill: "DCE6F1", lineColor: "B8CCE4", bold: true, fontSize: 9.6,
  });
  addTableCell(slide, "Typical Indicative Terms", 5.85, 4.1, 3.1, 0.4, {
    fill: "DCE6F1", lineColor: "B8CCE4", bold: true, fontSize: 9.6,
  });

  const architectureRows = [
    ["Negative", "Probability that the review expresses dissatisfaction", "worst, fraud, bad, horrible, support, order"],
    ["Neutral", "Probability that the review shows mixed or balanced opinion", "stars, but, late delivery, was not, good"],
    ["Positive", "Probability that the review expresses satisfaction", "great, best, amazing, love, quick, easy, thanks"],
  ];
  architectureRows.forEach((row, index) => {
    const y = 4.5 + index * 0.62;
    addTableCell(slide, row[0], 0.55, y, 1.5, 0.62, {
      fill: "F3F6FA", bold: true, align: "left", fontSize: 9.2,
    });
    addTableCell(slide, row[1], 2.05, y, 3.8, 0.62, {
      fill: "FFFFFF", align: "left", fontSize: 9.1,
    });
    addTableCell(slide, row[2], 5.85, y, 3.1, 0.62, {
      fill: "FFFFFF", align: "left", fontSize: 9.0,
    });
  });

  slide.addShape(pptx.ShapeType.rect, {
    x: 5.9,
    y: 3.62,
    w: 2.95,
    h: 0.28,
    fill: { color: "F7F7F7" },
    line: { color: "D9D9D9", pt: 0.8 },
  });
  slide.addText("SentiLens result: 90.17% accuracy | 90.40% weighted F1", {
    x: 6.0,
    y: 3.69,
    w: 2.75,
    h: 0.12,
    fontFace: "Calibri",
    fontSize: 9.2,
    bold: true,
    color: colors.footer,
    align: "center",
    margin: 0,
    fit: "shrink",
  });

  addFooter(slide, 6);
}

// Slide 7
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "SentiLens Example Prediction");

  addTableCell(slide, "Input Review", 0.55, 1.32, 8.35, 0.42, {
    fill: "DCE6F1", lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(
    slide,
    "I ordered food and I waited for an hour and then they cancelled the order because of no delivery man very bad experience I recommend not trusting this app",
    0.55,
    1.74,
    8.35,
    0.9,
    { fill: "FFFFFF", align: "left", fontSize: 9.6 }
  );

  addFlowCard(slide, "Signal Words Captured", [
    "waited for an hour",
    "cancelled the order",
    "no delivery man",
    "very bad experience",
    "not trusting this app",
  ], 0.72, 2.95, 2.05, 1.75);

  addFlowCard(slide, "Theme Context", [
    "Theme final:",
    "refund_cancellation",
    "",
    "Actual label: negative",
  ], 3.12, 3.0, 1.75, 1.52);

  addFlowCard(slide, "Predicted Class", [
    "SentiLens output:",
    "NEGATIVE",
    "",
    "High-confidence complaint prediction",
  ], 5.18, 3.0, 1.82, 1.52);

  addFlowCard(slide, "Probability Scores", [
    "Negative: 99.31%",
    "Neutral: 0.11%",
    "Positive: 0.58%",
  ], 7.2, 3.0, 1.35, 1.35);

  addTableCell(slide, "Why the Model Predicted Negative", 0.55, 5.0, 2.45, 0.4, {
    fill: "DCE6F1", lineColor: "B8CCE4", bold: true, fontSize: 9.6,
  });
  addTableCell(slide, "Explanation", 3.0, 5.0, 5.9, 0.4, {
    fill: "DCE6F1", lineColor: "B8CCE4", bold: true, fontSize: 9.6,
  });

  const exampleRows = [
    ["Complaint intensity", "Phrases such as \"very bad experience\" and \"not trusting this app\" align strongly with the negative class."],
    ["Service failure", "Cancellation and delivery failure are both frequent negative indicators in the training data."],
    ["Model behavior", "TF-IDF highlights recurring complaint terms, and balanced Logistic Regression converts those weights into class probabilities."],
  ];
  exampleRows.forEach((row, index) => {
    const y = 5.4 + index * 0.48;
    addTableCell(slide, row[0], 0.55, y, 2.45, 0.48, {
      fill: "F3F6FA", bold: true, align: "left", fontSize: 9.1,
    });
    addTableCell(slide, row[1], 3.0, y, 5.9, 0.48, {
      fill: "FFFFFF", align: "left", fontSize: 9.0,
    });
  });

  addFooter(slide, 7);
}

// Slide 8
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Analysis & Interpretation");
  addBodyBullets(slide, [
    "The tuned TF-IDF + Logistic Regression model achieved 90.17% accuracy and 90.40% weighted F1, making it reliable for large-scale sentiment reading.",
    "Predicted sentiment distribution was positive 20,587, negative 19,505, and neutral 1,505, showing a highly polarized customer voice with very few neutral reviews.",
    "Delivery generated the highest discussion volume with 16,106 reviews and remained mildly positive overall because positive delivery mentions still exceeded negative ones.",
    "Refund and cancellation emerged as the most critical pain point: 8,545 reviews in this theme, of which 88.3% were negative.",
    "Customer support was another major weakness with a 68.3% negative share, indicating service recovery issues harm trust even when the core ordering experience works well."
  ], { x: 0.76, y: 1.54, w: 5.9, h: 5.05, fontSize: 15.9, paraSpaceAfterPt: 11 });
  addStatBox(slide, "Interpretation", [
    "Brand strength comes from convenience, app utility, and delivery reach.",
    "Brand risk comes from refund handling, complaint resolution, and post-order support.",
    "Managerial priority: improve service recovery before it converts occasional failures into long-term trust damage."
  ], 6.72, 2.0, 2.5, 2.75);
  addFooter(slide, 8);
}

// Slide 9
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Comparison with Reference Paper");

  const left = 0.42;
  const top = 1.88;
  const colWidths = [1.45, 2.45, 2.45, 2.45];
  const rowHeights = [0.62, 0.52, 0.52, 0.52, 0.52];
  const xPositions = [
    left,
    left + colWidths[0],
    left + colWidths[0] + colWidths[1],
    left + colWidths[0] + colWidths[1] + colWidths[2],
  ];
  const yPositions = [];
  let runningY = top;
  rowHeights.forEach((height) => {
    yPositions.push(runningY);
    runningY += height;
  });

  addTableCell(slide, "Metric", xPositions[0], 1.24, colWidths[0], 0.48, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 9.6,
  });
  addTableCell(slide, "Jonathan et al. (2019)", xPositions[1], 1.24, colWidths[1], 0.48, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 9.6,
  });
  addTableCell(slide, "Our Recreated Random Forest", xPositions[2], 1.24, colWidths[2], 0.48, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 9.3,
  });
  addTableCell(slide, "Our Best Model", xPositions[3], 1.24, colWidths[3], 0.48, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 9.6,
  });

  const rows = [
    [
      "Dataset / Base",
      "Kaggle Bangalore restaurant reviews",
      "Zomato Google Play holdout set\n(33,277 train / 8,320 test)",
      "Zomato Google Play holdout set\n(33,277 train / 8,320 test)",
    ],
    [
      "Model",
      "Random Forest",
      "TF-IDF + Random Forest",
      "TF-IDF + Logistic Regression",
    ],
    [
      "Accuracy",
      "92.44%",
      "88.58%",
      "90.17%",
    ],
    [
      "Average Precision / Recall",
      "0.93 / 0.87",
      "0.6519 / 0.6135",
      "0.6771 / 0.6868",
    ],
    [
      "Neutral Recall",
      "0.73",
      "0.0169",
      "0.2152",
    ],
  ];

  rows.forEach((row, rowIndex) => {
    const y = yPositions[rowIndex];
    row.forEach((cellText, colIndex) => {
      addTableCell(slide, cellText, xPositions[colIndex], y, colWidths[colIndex], rowHeights[rowIndex], {
        fill: colIndex === 0 ? "F3F6FA" : "FFFFFF",
        align: colIndex === 0 ? "left" : "center",
        bold: colIndex === 0,
        fontSize: 9.8,
      });
    });
  });

  slide.addText(
    "Takeaway: the published paper reports stronger Random Forest results on a different dataset, but on our Zomato Google Play data the tuned Logistic Regression model performs better than the recreated Random Forest benchmark.",
    {
      x: 0.52,
      y: 4.95,
      w: 8.45,
      h: 0.44,
      fontFace: "Calibri",
      fontSize: 10,
      color: colors.text,
      margin: 0,
      align: "left",
      breakLine: true,
      fit: "shrink",
    }
  );

  slide.addText(
    "Note: this is a methodological comparison only. The paper and our project use different data sources and label construction, so the scores are not directly equivalent.",
    {
      x: 0.52,
      y: 5.38,
      w: 8.65,
      h: 0.54,
      fontFace: "Calibri",
      fontSize: 9.5,
      italic: true,
      color: colors.muted,
      margin: 0,
      align: "left",
    }
  );

  addFooter(slide, 9);
}

// Slide 10
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Comparison Explanation");

  addTableCell(slide, "Aspect", 0.55, 1.35, 1.65, 0.42, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 10,
  });
  addTableCell(slide, "Tabular Explanation", 2.2, 1.35, 6.7, 0.42, {
    fill: "DCE6F1",
    lineColor: "B8CCE4",
    bold: true,
    fontSize: 10,
  });

  const explanationRows = [
    ["Data Source", "Jonathan et al. (2019) used Kaggle Bangalore restaurant reviews, while our project uses Google Play Store reviews for Zomato only. This means the comparison is useful for positioning, not for exact one-to-one replication."],
    ["Model Result", "The paper reports 92.44% Random Forest accuracy, but when we recreate a Random Forest-style benchmark on our own data it drops to 88.58%. Our tuned TF-IDF + Logistic Regression model improves that to 90.17% on the same split."],
    ["Class Insight", "Neutral sentiment remains the hardest class in our dataset. Neutral recall falls sharply for recreated Random Forest and improves under Logistic Regression, showing that the best model handles mixed reviews more effectively."],
    ["Presentation Meaning", "The comparison supports the argument that model choice should depend on the dataset. For this project, the linear text model is a better fit than the literature-aligned Random Forest baseline."],
  ];

  explanationRows.forEach((row, index) => {
    const y = 1.77 + index * 0.96;
    addTableCell(slide, row[0], 0.55, y, 1.65, 0.96, {
      fill: "F3F6FA",
      bold: true,
      align: "left",
      fontSize: 9.6,
    });
    addTableCell(slide, row[1], 2.2, y, 6.7, 0.96, {
      fill: "FFFFFF",
      align: "left",
      fontSize: 9.4,
    });
  });

  slide.addText(
    "This slide can be explained verbally as: the paper gives a benchmark, our recreated Random Forest gives a fair local baseline, and our tuned Logistic Regression gives the best performance for the actual Zomato dataset.",
    {
      x: 0.6,
      y: 5.75,
      w: 8.2,
      h: 0.48,
      fontFace: "Calibri",
      fontSize: 9.8,
      color: colors.muted,
      italic: true,
      margin: 0,
      breakLine: true,
      fit: "shrink",
    }
  );

  addFooter(slide, 10);
}

// Slide 11
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Relevance with Objectives");
  addBodyText(
    slide,
    [
      "1. Objective of collecting and preprocessing Zomato reviews was achieved through a unified dataset of 41,597 cleaned Google Play reviews.",
      "2. Objective of classifying sentiment was addressed through rating-based weak labels and a tuned Logistic Regression pipeline with 90.17% accuracy.",
      "3. Objective of identifying major customer perception themes was achieved by mapping reviews into delivery, refund/cancellation, app experience, customer support, pricing, trust, and related categories.",
      "4. Objective of understanding brand-impacting pain points was met by showing that refund handling and customer support produce the heaviest negative sentiment concentration.",
      "5. Objective of supporting brand strategy was met by translating review insights into action areas such as faster service recovery, clearer refund resolution, and more dependable customer communication."
    ].join("\n\n"),
    { x: 0.84, y: 1.5, w: 8.15, h: 5.4, fontSize: 15.4, paraSpaceAfterPt: 12 }
  );
  addFooter(slide, 11);
}

const outPath = "C:/Users/sshrivastava/Downloads/mba-project/documentation/Project_Review_2_Zomato_Updated_v5.pptx";

pptx.writeFile({ fileName: outPath });
