const path = require("path");
const PptxGenJS = require("pptxgenjs");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_4x3";
pptx.author = "OpenAI Codex";
pptx.company = "OpenAI";
pptx.subject = "Consolidated final presentation for Zomato sentiment analysis project";
pptx.title = "End-to-End Zomato Sentiment Analysis Project";
pptx.lang = "en-IN";
pptx.theme = {
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  lang: "en-IN",
};

const ROOT = "C:/Users/sshrivastava/Downloads/mba-project";
const FIG = (file) => path.join(ROOT, "documentation", "figures", file).replace(/\\/g, "/");

const colors = {
  text: "000000",
  footer: "4F81BD",
  white: "FFFFFF",
  muted: "666666",
  lightBlue: "DCE6F1",
  softBlue: "F3F6FA",
  line: "D9D9D9",
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

function addTitle(slide, title, subtitle = "") {
  slide.addText(title, {
    x: 0.5,
    y: 0.28,
    w: 9,
    h: 0.72,
    fontFace: "Calibri",
    fontSize: 24,
    color: colors.text,
    align: "center",
    margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.85,
      y: 0.98,
      w: 8.3,
      h: 0.2,
      fontFace: "Calibri",
      fontSize: 10.8,
      italic: true,
      color: colors.muted,
      align: "center",
      margin: 0,
    });
  }
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
    x: opts.x ?? 0.8,
    y: opts.y ?? 1.45,
    w: opts.w ?? 8.0,
    h: opts.h ?? 4.9,
    fontFace: "Calibri",
    fontSize: opts.fontSize ?? 17,
    color: colors.text,
    margin: 0.04,
    breakLine: true,
    paraSpaceAfterPt: opts.paraSpaceAfterPt ?? 12,
    valign: "top",
  });
}

function addBodyText(slide, text, opts = {}) {
  slide.addText(text, {
    x: opts.x ?? 0.8,
    y: opts.y ?? 1.45,
    w: opts.w ?? 8.0,
    h: opts.h ?? 4.9,
    fontFace: "Calibri",
    fontSize: opts.fontSize ?? 16.5,
    color: colors.text,
    margin: 0.04,
    breakLine: true,
    paraSpaceAfterPt: opts.paraSpaceAfterPt ?? 10,
    valign: "top",
    fit: opts.fit ?? "shrink",
  });
}

function addTableCell(slide, text, x, y, w, h, opts = {}) {
  slide.addShape(pptx.ShapeType.rect, {
    x,
    y,
    w,
    h,
    fill: { color: opts.fill || colors.white },
    line: { color: opts.lineColor || colors.line, pt: 1 },
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
    fill: { color: colors.white },
    line: { color: "B8CCE4", pt: 1.2 },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: x + 0.18,
    y: y + 0.11,
    w: w - 0.36,
    h: 0.08,
    fill: { color: colors.lightBlue },
    line: { color: colors.lightBlue, pt: 0.5 },
  });
  slide.addText(title, {
    x: x + 0.08,
    y: y + 0.27,
    w: w - 0.16,
    h: 0.24,
    fontFace: "Calibri",
    fontSize: 10.4,
    bold: true,
    color: colors.footer,
    align: "center",
    margin: 0,
  });
  slide.addText(lines.join("\n"), {
    x: x + 0.12,
    y: y + 0.56,
    w: w - 0.24,
    h: h - 0.66,
    fontFace: "Calibri",
    fontSize: 9.1,
    color: colors.text,
    align: "left",
    margin: 0.02,
    breakLine: true,
    fit: "shrink",
  });
}

function addStatBox(slide, title, lines, x, y, w, h) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w, h,
    fill: { color: "F7F7F7" },
    line: { color: colors.line, pt: 1 },
  });
  slide.addText(title, {
    x: x + 0.12,
    y: y + 0.12,
    w: w - 0.24,
    h: 0.22,
    fontFace: "Calibri",
    fontSize: 11.5,
    bold: true,
    color: colors.footer,
    margin: 0,
  });
  slide.addText(lines.join("\n"), {
    x: x + 0.12,
    y: y + 0.4,
    w: w - 0.24,
    h: h - 0.48,
    fontFace: "Calibri",
    fontSize: 10.3,
    color: colors.text,
    margin: 0,
    breakLine: true,
    fit: "shrink",
  });
}

function addImagePanel(slide, title, imagePath, x, y, w, h, caption = "") {
  slide.addText(title, {
    x,
    y,
    w,
    h: 0.22,
    fontFace: "Calibri",
    fontSize: 12,
    bold: true,
    color: colors.footer,
    margin: 0,
    align: "left",
  });
  slide.addShape(pptx.ShapeType.rect, {
    x,
    y: y + 0.28,
    w,
    h: h - 0.28,
    fill: { color: "FFFFFF" },
    line: { color: colors.line, pt: 1 },
  });
  slide.addImage({
    path: imagePath,
    x: x + 0.06,
    y: y + 0.34,
    w: w - 0.12,
    h: h - 0.5,
    sizing: { type: "contain", x: x + 0.06, y: y + 0.34, w: w - 0.12, h: h - 0.5 },
  });
  if (caption) {
    slide.addText(caption, {
      x: x + 0.08,
      y: y + h - 0.16,
      w: w - 0.16,
      h: 0.12,
      fontFace: "Calibri",
      fontSize: 8.5,
      italic: true,
      color: colors.muted,
      align: "center",
      margin: 0,
      fit: "shrink",
    });
  }
}

// Slide 1
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  slide.addText("End-to-End Project Presentation", {
    x: 1.2, y: 0.38, w: 7.6, h: 0.58,
    fontFace: "Calibri", fontSize: 26, color: colors.text, align: "center", margin: 0,
  });
  slide.addText("Sentiment Analysis of Zomato Play Store Reviews for Brand Strategy", {
    x: 1.1, y: 1.95, w: 7.8, h: 1.0,
    fontFace: "Calibri", fontSize: 22, color: colors.text, align: "center", margin: 0, fit: "shrink",
  });
  slide.addText("Prepared by:\nSuhani Shrivastava\n\nRoll Number:\n24EMBA1442\n\nGuide:\nDr. Suraj PG", {
    x: 0.72, y: 3.75, w: 2.35, h: 2.1,
    fontFace: "Calibri", fontSize: 13.5, color: colors.text, margin: 0, breakLine: true,
  });
  addStatBox(slide, "Project Focus", [
    "Platform: Google Play Store",
    "Brand: Zomato",
    "Dataset: 41,597 cleaned reviews",
    "Best model: SentiLens",
    "Output: business insights for brand strategy",
  ], 6.35, 3.2, 2.2, 1.85);
  addFooter(slide, 1);
}

// Slide 2
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Project Overview", "Abstract-level summary of the complete study");
  addBodyBullets(slide, [
    "This project analyzes customer sentiment toward Zomato using Google Play Store reviews as a large-scale source of digital customer feedback.",
    "The review corpus was cleaned, deduplicated, standardized, and labeled using a rating-based sentiment proxy and rule-based theme classification.",
    "The study combines descriptive review analytics, NLP-based modeling, benchmark comparison, and dashboard-driven interpretation.",
    "The final goal is not only to classify sentiment, but to identify customer pain points and convert them into managerial actions for customer experience and brand strategy."
  ], { x: 0.78, y: 1.45, w: 5.55, h: 4.8, fontSize: 16.2 });
  addStatBox(slide, "Keywords", [
    "Zomato",
    "Sentiment analysis",
    "Google Play reviews",
    "NLP",
    "Customer experience",
    "Brand strategy",
  ], 6.6, 1.85, 2.1, 2.2);
  addStatBox(slide, "Study Contribution", [
    "Converts unstructured reviews",
    "into interpretable insights",
    "for service improvement,",
    "trust repair, and",
    "competitive positioning.",
  ], 6.6, 4.35, 2.1, 1.55);
  addFooter(slide, 2);
}

// Slide 3
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Problem and Research Gap");
  addTableCell(slide, "Problem / Gap", 0.55, 1.35, 2.0, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "Project Response", 2.55, 1.35, 6.35, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  const rows = [
    ["Large review volume is difficult to interpret manually.", "Use structured NLP workflow and sentiment/theme analysis to scale interpretation."],
    ["Star ratings alone do not explain why customers are satisfied or dissatisfied.", "Combine rating proxy with review text and theme classification."],
    ["Managers often lack evidence linking app reviews to action areas.", "Translate review patterns into brand, delivery, refund, and support recommendations."],
  ];
  rows.forEach((row, idx) => {
    const y = 1.77 + idx * 0.72;
    addTableCell(slide, row[0], 0.55, y, 2.0, 0.72, {
      fill: colors.softBlue, align: "left", bold: true, fontSize: 9.5,
    });
    addTableCell(slide, row[1], 2.55, y, 6.35, 0.72, {
      fill: colors.white, align: "left", fontSize: 9.4,
    });
  });
  addBodyText(slide, [
    "The central research gap is not lack of feedback, but lack of structured interpretation. Zomato receives a very large volume of app reviews, yet those reviews need an end-to-end analytical process before they become useful for customer-experience and brand decisions.",
    "This project addresses that gap by converting raw review text into measurable sentiment patterns, theme-level pain points, and managerially usable findings."
  ].join("\n\n"), { x: 0.78, y: 4.25, w: 8.0, h: 1.85, fontSize: 14.8 });
  addFooter(slide, 3);
}

// Slide 4
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Project Objectives");
  addFlowCard(slide, "Objective 1", [
    "Collect and preprocess",
    "Zomato-related Google Play",
    "reviews into a usable",
    "master dataset",
  ], 0.6, 1.75, 1.9, 1.7);
  addFlowCard(slide, "Objective 2", [
    "Classify reviews into",
    "positive, negative,",
    "and neutral sentiment",
    "categories",
  ], 2.7, 1.75, 1.9, 1.7);
  addFlowCard(slide, "Objective 3", [
    "Identify major themes such as",
    "delivery, refund/cancellation,",
    "support, pricing, and",
    "app experience",
  ], 4.8, 1.75, 1.95, 1.85);
  addFlowCard(slide, "Objective 4", [
    "Interpret the results for",
    "customer experience,",
    "service recovery, and",
    "brand strategy decisions",
  ], 6.95, 1.75, 1.75, 1.85);
  addStatBox(slide, "Objective Logic", [
    "The project moves from",
    "data collection to modeling,",
    "then from analysis to",
    "managerial interpretation.",
  ], 2.2, 4.45, 4.7, 1.2);
  addFooter(slide, 4);
}

// Slide 5
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Literature and Research Framework");
  addBodyBullets(slide, [
    "The literature positions sentiment analysis as a practical way to extract structured insight from unstructured customer opinions.",
    "Online reviews act as both feedback and electronic word-of-mouth, shaping customer trust, trial, and purchase decisions.",
    "For food-delivery platforms, reviews reflect both service execution and digital interface quality.",
    "This study adopts a framework where reviews provide raw evidence, sentiment indicates emotional orientation, themes explain issue drivers, and managerial interpretation converts findings into business action."
  ], { x: 0.78, y: 1.45, w: 5.55, h: 4.7, fontSize: 15.7 });
  addFlowCard(slide, "Research Framework", [
    "1. Google Play reviews",
    "2. Sentiment labeling",
    "3. Theme identification",
    "4. Theme-wise interpretation",
    "5. Brand strategy implications",
  ], 6.55, 2.0, 2.15, 2.25);
  addStatBox(slide, "Literature Positioning", [
    "This project extends beyond",
    "pure classification by adding",
    "theme analysis, priority logic,",
    "dashboard interpretation, and",
    "benchmark comparison.",
  ], 6.55, 4.65, 2.15, 1.45);
  addFooter(slide, 5);
}

// Slide 6
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Research Methodology");
  addFlowCard(slide, "Research Design", [
    "Descriptive + exploratory",
    "Applied in nature",
    "Business-focused interpretation",
  ], 0.55, 1.55, 1.85, 1.45);
  addFlowCard(slide, "Data Source", [
    "Google Play Store",
    "Zomato app reviews",
    "Ratings + text + metadata",
  ], 2.6, 1.55, 1.85, 1.45);
  addFlowCard(slide, "Collection Modes", [
    "Newest",
    "Most relevant",
    "Rating-based",
    "Multi-pull strategy",
  ], 4.65, 1.55, 1.85, 1.65);
  addFlowCard(slide, "Processing", [
    "Cleaning",
    "Deduplication",
    "Theme mapping",
    "Sentiment modeling",
  ], 6.7, 1.55, 1.85, 1.65);
  slide.addShape(pptx.ShapeType.line, {
    x: 1.95, y: 3.55, w: 4.95, h: 0,
    line: { color: "B8CCE4", pt: 1.2 },
  });
  addTableCell(slide, "Method Layer", 0.55, 4.0, 2.0, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "Implementation", 2.55, 4.0, 6.3, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  const methodRows = [
    ["Sentiment logic", "Ratings 1-2 = negative, 3 = neutral, 4-5 = positive, with text mismatch used as a caution flag."],
    ["Theme logic", "Ordered first-match keyword rules with fallback to earlier theme hints when no clean rule match exists."],
    ["Tools", "Python scripts, scikit-learn, custom data pipelines, and Streamlit dashboard outputs for interpretation."],
  ];
  methodRows.forEach((row, idx) => {
    const y = 4.4 + idx * 0.55;
    addTableCell(slide, row[0], 0.55, y, 2.0, 0.55, {
      fill: colors.softBlue, align: "left", bold: true, fontSize: 9.4,
    });
    addTableCell(slide, row[1], 2.55, y, 6.3, 0.55, {
      fill: colors.white, align: "left", fontSize: 9.2,
    });
  });
  addFooter(slide, 6);
}

// Slide 7
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "End-to-End Analytical Flow");
  addFlowCard(slide, "Sample User Input", [
    "Review: \"Order got cancelled",
    "after one hour and support",
    "did not help at all\"",
    "Rating: 1 star",
  ], 0.45, 1.55, 1.7, 1.85);
  slide.addShape(pptx.ShapeType.chevron, {
    x: 2.15, y: 2.12, w: 0.42, h: 0.5,
    fill: { color: colors.lightBlue },
    line: { color: "B8CCE4", pt: 1 },
  });
  addFlowCard(slide, "Pre-processing", [
    "Lowercasing",
    "Noise removal",
    "Normalization",
    "Deduplication checks",
  ], 2.65, 1.55, 1.5, 1.85);
  slide.addShape(pptx.ShapeType.chevron, {
    x: 4.12, y: 2.12, w: 0.42, h: 0.5,
    fill: { color: colors.lightBlue },
    line: { color: "B8CCE4", pt: 1 },
  });
  addFlowCard(slide, "SentiLens Output", [
    "Sentiment: Negative",
    "High confidence score",
    "TF-IDF + Logistic",
    "Regression pipeline",
  ], 4.62, 1.55, 1.58, 1.85);
  slide.addShape(pptx.ShapeType.chevron, {
    x: 6.18, y: 2.12, w: 0.42, h: 0.5,
    fill: { color: colors.lightBlue },
    line: { color: "B8CCE4", pt: 1 },
  });
  addFlowCard(slide, "Final Business Output", [
    "Theme: refund/cancellation",
    "Priority flag: high",
    "Dashboard summary",
    "Managerial action point",
  ], 6.68, 1.55, 1.75, 1.85);
  addTableCell(slide, "Stage", 0.6, 4.25, 1.5, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.6,
  });
  addTableCell(slide, "Illustration", 2.1, 4.25, 6.55, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.6,
  });
  const flowRows = [
    ["Input layer", "A raw app review enters the pipeline with text and star rating metadata."],
    ["Modeling layer", "The cleaned text is transformed into TF-IDF features and classified by SentiLens."],
    ["Interpretation layer", "The review is linked to a dominant theme and aggregated into dashboard-level insight."],
  ];
  flowRows.forEach((row, idx) => {
    const y = 4.65 + idx * 0.55;
    addTableCell(slide, row[0], 0.6, y, 1.5, 0.55, {
      fill: colors.softBlue, align: "left", bold: true, fontSize: 9.0,
    });
    addTableCell(slide, row[1], 2.1, y, 6.55, 0.55, {
      fill: colors.white, align: "left", fontSize: 9.0,
    });
  });
  addFooter(slide, 7);
}

// Slide 8
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Data Collection Strategy");
  addFlowCard(slide, "Relevant Reviews", [
    "output_playstore_relevant_en",
    "22,773 reviews",
    "Captures commonly surfaced",
    "issue-oriented feedback",
  ], 0.55, 1.45, 1.8, 1.7);
  addFlowCard(slide, "Rating-Based Pulls", [
    "output_playstore_rating_en",
    "15,942 reviews",
    "Captures stronger positive",
    "and negative extremes",
  ], 2.55, 1.45, 1.8, 1.7);
  addFlowCard(slide, "Newest Pulls", [
    "Newest review pulls",
    "2,882 reviews",
    "Adds recent and",
    "time-based coverage",
  ], 4.55, 1.45, 1.8, 1.7);
  addFlowCard(slide, "Merged Corpus", [
    "All cleaned exports merged",
    "before deduplication",
    "to reduce sort bias",
  ], 6.55, 1.45, 1.8, 1.55);
  addTableCell(slide, "Selection Principle", 0.55, 3.55, 2.2, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "Explanation", 2.75, 3.55, 5.6, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  const selectionRows = [
    ["Multi-sort coverage", "A single Play Store retrieval mode can over-represent one type of feedback. Multi-sort pulls improved coverage across issue intensity and time."],
    ["Recency coverage", "Newest review pulls were included so the analysis captures both long-run patterns and more recent customer feedback."],
    ["Final selection", "After merging and cleaning, 41,597 unique Google Play reviews formed the final analytical dataset."],
  ];
  selectionRows.forEach((row, idx) => {
    const y = 3.95 + idx * 0.65;
    addTableCell(slide, row[0], 0.55, y, 2.2, 0.65, {
      fill: colors.softBlue, align: "left", bold: true, fontSize: 9.4,
    });
    addTableCell(slide, row[1], 2.75, y, 5.6, 0.65, {
      fill: colors.white, align: "left", fontSize: 9.2,
    });
  });
  addFooter(slide, 7);
}

// Slide 8
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Pre-processing and Dataset Construction");
  addTableCell(slide, "Step", 0.55, 1.35, 1.4, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "What Was Done", 1.95, 1.35, 4.95, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "Effect", 6.9, 1.35, 1.95, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  const prepRows = [
    ["Merge", "Combined cleaned exports from relevant, rating-based, and newest review files into one analytical corpus.", "46,193 rows before dedupe"],
    ["Normalize", "Applied lowercase conversion, punctuation cleanup, hyperlink/noise removal, and whitespace compaction.", "Comparable normalized text"],
    ["Dedup by ID", "Removed repeated reviews using review identifiers after priority sorting by relevance score, thumbs-up count, and rating.", "41,657 rows"],
    ["Dedup by Text", "Removed repeated content using normalized review text to avoid counting the same wording multiple times.", "41,597 rows"],
    ["Structure", "Retained fields such as text, normalized text, rating, year, recency bucket, sentiment label, and theme label.", "Final master dataset"],
  ];
  prepRows.forEach((row, idx) => {
    const y = 1.77 + idx * 0.74;
    addTableCell(slide, row[0], 0.55, y, 1.4, 0.74, {
      fill: colors.softBlue, align: "left", bold: true, fontSize: 9.5,
    });
    addTableCell(slide, row[1], 1.95, y, 4.95, 0.74, {
      fill: colors.white, align: "left", fontSize: 9.25,
    });
    addTableCell(slide, row[2], 6.9, y, 1.95, 0.74, {
      fill: colors.white, align: "center", fontSize: 9.2,
    });
  });
  addFooter(slide, 9);
}

// Slide 9
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Real Examples from Cleaning");
  addTableCell(slide, "Raw Review Text", 0.5, 1.35, 4.15, 0.38, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.6,
  });
  addTableCell(slide, "Normalized Text", 4.65, 1.35, 4.2, 0.38, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.6,
  });
  const normRows = [
    [
      "I loved this app so much i loved its delivery and all.Its probably the best app to order the food...",
      "i loved this app so much i loved its delivery and all its probably the best app to order the food..."
    ],
    [
      "Such a bad customer service .....my order got cancelled and they didn't refund.....",
      "such a bad customer service my order got cancelled and they didn t refund ..."
    ]
  ];
  normRows.forEach((row, idx) => {
    const y = 1.73 + idx * 0.82;
    addTableCell(slide, row[0], 0.5, y, 4.15, 0.82, {
      fill: colors.white, align: "left", fontSize: 8.8,
    });
    addTableCell(slide, row[1], 4.65, y, 4.2, 0.82, {
      fill: colors.white, align: "left", fontSize: 8.8,
    });
  });
  addTableCell(slide, "Duplicate Type", 0.5, 3.6, 1.45, 0.38, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.4,
  });
  addTableCell(slide, "Observed Example", 1.95, 3.6, 4.9, 0.38, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.4,
  });
  addTableCell(slide, "Cleaning Decision", 6.85, 3.6, 2.0, 0.38, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.4,
  });
  const dupRows = [
    [
      "Same review ID",
      "Record ID c9c028a3-4be2-44fd-934b-56a7aae70b10 appeared in newest_en, relevant_en, and rating_en with the same review content.",
      "Kept one row after priority sorting; removed repeated IDs."
    ],
    [
      "Same normalized text",
      "\"Best app for food delivery\", \"Best app for food delivery...\", and \"Best app for food delivery\" normalized to the same final string.",
      "Kept one representative row; removed repeated wording."
    ]
  ];
  dupRows.forEach((row, idx) => {
    const y = 3.98 + idx * 0.95;
    addTableCell(slide, row[0], 0.5, y, 1.45, 0.95, {
      fill: colors.softBlue, align: "left", bold: true, fontSize: 9.1,
    });
    addTableCell(slide, row[1], 1.95, y, 4.9, 0.95, {
      fill: colors.white, align: "left", fontSize: 8.9,
    });
    addTableCell(slide, row[2], 6.85, y, 2.0, 0.95, {
      fill: colors.white, align: "left", fontSize: 8.8,
    });
  });
  slide.addText("Cleaning summary: 46,193 merged rows -> 41,657 after review-ID dedupe -> 41,597 after normalized-text dedupe.", {
    x: 0.62, y: 6.15, w: 8.1, h: 0.2,
    fontFace: "Calibri", fontSize: 10, bold: true, color: colors.text, align: "center", margin: 0,
  });
  addFooter(slide, 10);
}

// Slide 10
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Final Dataset Profile");
  addTableCell(slide, "Measure", 0.7, 1.45, 3.1, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "Value", 3.8, 1.45, 1.7, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  const datasetRows = [
    ["Total reviews in final dataset", "41,597"],
    ["Positive labeled reviews", "21,487"],
    ["Negative labeled reviews", "18,923"],
    ["Neutral labeled reviews", "1,187"],
    ["Recent reviews (2024+)", "15,320"],
    ["Average text length", "271.97 chars"],
    ["Median text length", "260 chars"],
  ];
  datasetRows.forEach((row, idx) => {
    const y = 1.87 + idx * 0.52;
    addTableCell(slide, row[0], 0.7, y, 3.1, 0.52, {
      fill: idx % 2 === 0 ? colors.softBlue : colors.white, align: "left", fontSize: 9.5,
    });
    addTableCell(slide, row[1], 3.8, y, 1.7, 0.52, {
      fill: idx % 2 === 0 ? colors.softBlue : colors.white, align: "center", fontSize: 9.5, bold: true,
    });
  });
  addStatBox(slide, "Largest Themes", [
    "Delivery: 16,106",
    "Refund/cancellation: 8,545",
    "App experience: 5,812",
    "Customer support: 3,191",
    "Pricing/fees: 3,100",
  ], 5.95, 1.9, 2.15, 2.15);
  addStatBox(slide, "Dataset Scope", [
    "Source: Google Play Store",
    "Recent subset: 15,320",
    "Average text: 271.97 chars",
    "App-review focused design",
  ], 5.95, 4.45, 2.15, 1.45);
  addFooter(slide, 11);
}

// Slide 11
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "SentiLens Architecture");
  addFlowCard(slide, "Input Review Text", [
    "Cleaned Google Play",
    "review sentence",
    "with sufficient text length",
  ], 0.5, 1.55, 1.8, 1.45);
  addFlowCard(slide, "TF-IDF Vectorizer", [
    "Word n-grams: 1 to 2",
    "min_df = 2",
    "max_features = 40,000",
    "lowercase = True",
  ], 2.55, 1.55, 1.9, 1.75);
  addFlowCard(slide, "Sparse Feature Space", [
    "Transforms review text",
    "into weighted term features",
    "for model learning",
  ], 4.7, 1.55, 1.75, 1.55);
  addFlowCard(slide, "Logistic Regression", [
    "C = 2.5",
    "max_iter = 1500",
    "class_weight = balanced",
    "random_state = 42",
  ], 6.65, 1.55, 1.85, 1.75);
  addTableCell(slide, "Output Class", 0.6, 4.05, 1.45, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.4,
  });
  addTableCell(slide, "Model Meaning", 2.05, 4.05, 3.4, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.4,
  });
  addTableCell(slide, "Indicative Terms", 5.45, 4.05, 3.35, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.4,
  });
  const sentiRows = [
    ["Negative", "Probability that the review expresses dissatisfaction", "worst, fraud, bad, support, horrible, order"],
    ["Neutral", "Probability that the review is mixed or balanced", "stars, but, late delivery, was not, good"],
    ["Positive", "Probability that the review expresses satisfaction", "great, best, amazing, love, quick, easy, thanks"],
  ];
  sentiRows.forEach((row, idx) => {
    const y = 4.45 + idx * 0.62;
    addTableCell(slide, row[0], 0.6, y, 1.45, 0.62, {
      fill: colors.softBlue, align: "left", bold: true, fontSize: 9.1,
    });
    addTableCell(slide, row[1], 2.05, y, 3.4, 0.62, {
      fill: colors.white, align: "left", fontSize: 9.0,
    });
    addTableCell(slide, row[2], 5.45, y, 3.35, 0.62, {
      fill: colors.white, align: "left", fontSize: 8.9,
    });
  });
  slide.addText("SentiLens result: 90.17% accuracy | 90.40% weighted F1", {
    x: 5.55, y: 3.52, w: 3.05, h: 0.18,
    fontFace: "Calibri", fontSize: 9.5, bold: true, color: colors.footer, align: "center", margin: 0,
    fit: "shrink",
  });
  addFooter(slide, 12);
}

// Slide 12
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Model Example and Performance");
  addTableCell(slide, "Example Input Review", 0.55, 1.3, 8.35, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "I ordered food and I waited for an hour and then they cancelled the order because of no delivery man very bad experience I recommend not trusting this app", 0.55, 1.72, 8.35, 0.9, {
    fill: colors.white, align: "left", fontSize: 9.5,
  });
  addFlowCard(slide, "Theme Context", [
    "refund_cancellation",
    "Actual label: negative",
  ], 0.72, 2.95, 1.7, 1.15);
  addFlowCard(slide, "Predicted Class", [
    "NEGATIVE",
    "High-confidence output",
  ], 2.8, 2.95, 1.7, 1.15);
  addFlowCard(slide, "Probability Scores", [
    "Negative: 99.31%",
    "Neutral: 0.11%",
    "Positive: 0.58%",
  ], 4.88, 2.95, 1.8, 1.35);
  addFlowCard(slide, "Why It Works", [
    "Complaint terms such as",
    "\"cancelled\", \"waited\",",
    "\"very bad\", and",
    "\"not trusting\" drive",
    "the negative score upward.",
  ], 7.0, 2.85, 1.6, 1.8);
  addTableCell(slide, "Performance Metric", 0.55, 4.95, 3.15, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "Value", 3.7, 4.95, 1.35, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  const perfRows = [
    ["Accuracy", "90.17%"],
    ["Macro F1", "0.6811"],
    ["Weighted F1", "0.9040"],
    ["Negative recall", "0.9342"],
    ["Positive recall", "0.9109"],
    ["Neutral recall", "0.2152"],
  ];
  perfRows.forEach((row, idx) => {
    const y = 5.37 + idx * 0.23;
    addTableCell(slide, row[0], 0.55, y, 3.15, 0.23, {
      fill: idx % 2 === 0 ? colors.softBlue : colors.white, align: "left", fontSize: 8.8,
    });
    addTableCell(slide, row[1], 3.7, y, 1.35, 0.23, {
      fill: idx % 2 === 0 ? colors.softBlue : colors.white, align: "center", fontSize: 8.8, bold: true,
    });
  });
  addStatBox(slide, "Interpretation", [
    "SentiLens performs strongly",
    "on positive and negative classes.",
    "Neutral remains the hardest class,",
    "which is common in review datasets",
    "with limited middle-rating volume.",
  ], 5.45, 4.95, 3.35, 1.45);
  addFooter(slide, 13);
}

// Slide 13
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Overall Sentiment and Dashboard View");
  addImagePanel(
    slide,
    "Dashboard Overview",
    FIG("dashboard_overview.png"),
    0.55,
    1.35,
    4.75,
    4.85,
    "Headline KPIs and overall sentiment distribution"
  );
  addTableCell(slide, "Predicted Sentiment", 5.6, 1.55, 1.8, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "Count / Share", 7.4, 1.55, 1.45, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  const overallRows = [
    ["Positive", "20,587 | 49.49%"],
    ["Negative", "19,505 | 46.89%"],
    ["Neutral", "1,505 | 3.62%"],
  ];
  overallRows.forEach((row, idx) => {
    const y = 1.97 + idx * 0.55;
    addTableCell(slide, row[0], 5.6, y, 1.8, 0.55, {
      fill: colors.softBlue, align: "left", bold: true, fontSize: 9.4,
    });
    addTableCell(slide, row[1], 7.4, y, 1.45, 0.55, {
      fill: colors.white, align: "center", fontSize: 9.4,
    });
  });
  addStatBox(slide, "Key Takeaway", [
    "Positive and negative review",
    "volumes are both large, so",
    "overall sentiment alone does",
    "not explain the full story.",
  ], 5.6, 3.75, 3.25, 0.9);
  addStatBox(slide, "Managerial Read", [
    "Theme-level analysis is needed",
    "to separate operational pain",
    "points from broad brand loyalty.",
  ], 5.6, 4.9, 3.25, 0.85);
  addFooter(slide, 14);
}

// Slide 14
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Theme Analysis and Priority Areas");
  addImagePanel(
    slide,
    "Theme-Level Dashboard View",
    FIG("dashboard_theme_analysis.png"),
    0.55,
    1.35,
    4.7,
    4.85,
    "Theme-wise sentiment share and net sentiment"
  );
  addTableCell(slide, "Theme", 5.55, 1.35, 1.7, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.8,
  });
  addTableCell(slide, "Key Result", 7.25, 1.35, 1.6, 0.4, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.8,
  });
  const themeRows = [
    ["Refund/cancellation", "88.32% negative share"],
    ["Customer support", "68.29% negative share"],
    ["Delivery", "16,106 rows; largest theme"],
    ["App experience", "78.97% positive share"],
    ["Pricing/fees", "Mixed but mildly positive"],
  ];
  themeRows.forEach((row, idx) => {
    const y = 1.75 + idx * 0.48;
    addTableCell(slide, row[0], 5.55, y, 1.7, 0.48, {
      fill: idx % 2 === 0 ? colors.softBlue : colors.white, align: "left", fontSize: 9.0, bold: true,
    });
    addTableCell(slide, row[1], 7.25, y, 1.6, 0.48, {
      fill: idx % 2 === 0 ? colors.softBlue : colors.white, align: "center", fontSize: 8.9,
    });
  });
  addStatBox(slide, "Priority Interpretation", [
    "Highest priority: refund/cancellation and customer support.",
    "Largest discussion area: delivery.",
    "Relative strength: app experience.",
    "Pricing/fees remains mixed and should be monitored.",
  ], 5.6, 4.0, 3.25, 1.5);
  addFooter(slide, 15);
}

// Slide 15
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Recent Trends and Current Feedback");
  addImagePanel(
    slide,
    "Recent Theme View",
    FIG("dashboard_recent_theme_view.png"),
    0.55,
    1.35,
    4.2,
    3.9,
    "2024+ review subset"
  );
  addImagePanel(
    slide,
    "Trend Over Time",
    FIG("dashboard_trend_over_time.png"),
    5.0,
    1.35,
    3.85,
    3.9,
    "Sentiment share across years"
  );
  addBodyBullets(slide, [
    "The recent-period subset contains 15,320 reviews and confirms the same structural pain points seen in the full dataset.",
    "Refund/cancellation becomes even more negative in recent reviews, while customer support also worsens.",
    "Delivery remains high-volume with slightly weaker net sentiment than the full dataset.",
    "App experience stays comparatively strong, suggesting usability remains better than post-order resolution processes."
  ], { x: 0.78, y: 5.45, w: 8.0, h: 1.05, fontSize: 13.7, paraSpaceAfterPt: 8 });
  addFooter(slide, 16);
}

// Slide 16
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Benchmark Comparison with Prior Paper");
  addImagePanel(
    slide,
    "Benchmark Dashboard",
    FIG("dashboard_benchmark_overview.png"),
    0.55,
    1.35,
    4.25,
    3.8,
    "Paper result vs recreated benchmark vs SentiLens"
  );
  addTableCell(slide, "Model / Study", 4.95, 1.5, 1.9, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.2,
  });
  addTableCell(slide, "Acc.", 6.85, 1.5, 0.7, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.2,
  });
  addTableCell(slide, "Prec.", 7.55, 1.5, 0.65, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.2,
  });
  addTableCell(slide, "Rec.", 8.2, 1.5, 0.65, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.2,
  });
  const benchRows = [
    ["Paper RF (2019)", "92.44%", "0.9300", "0.8700"],
    ["Recreated TF-IDF + RF", "88.58%", "0.6519", "0.6135"],
    ["SentiLens", "90.17%", "0.6771", "0.6868"],
  ];
  benchRows.forEach((row, idx) => {
    const y = 1.92 + idx * 0.62;
    addTableCell(slide, row[0], 4.95, y, 1.9, 0.62, {
      fill: idx % 2 === 0 ? colors.softBlue : colors.white, align: "left", fontSize: 8.5, bold: idx === 2,
    });
    addTableCell(slide, row[1], 6.85, y, 0.7, 0.62, {
      fill: idx % 2 === 0 ? colors.softBlue : colors.white, align: "center", fontSize: 8.5, bold: true,
    });
    addTableCell(slide, row[2], 7.55, y, 0.65, 0.62, {
      fill: idx % 2 === 0 ? colors.softBlue : colors.white, align: "center", fontSize: 8.4,
    });
    addTableCell(slide, row[3], 8.2, y, 0.65, 0.62, {
      fill: idx % 2 === 0 ? colors.softBlue : colors.white, align: "center", fontSize: 8.4,
    });
  });
  addStatBox(slide, "Interpretation", [
    "This comparison is methodological, not strictly like-for-like, because the prior paper used a different dataset and labeling process.",
    "Within this project's holdout setting, SentiLens outperforms the recreated Random Forest baseline.",
    "That supports using a tuned linear text model for this Google Play-only Zomato dataset.",
  ], 4.95, 4.0, 3.9, 1.4);
  addFooter(slide, 17);
}

// Slide 17
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Our Study vs Previous Zomato Research");
  addTableCell(slide, "Comparison Area", 0.5, 1.4, 1.75, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.5,
  });
  addTableCell(slide, "Previous Paper", 2.25, 1.4, 3.1, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.5,
  });
  addTableCell(slide, "Our Study", 5.35, 1.4, 3.25, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 9.5,
  });
  const compareRows = [
    ["Data source", "Kaggle Bangalore restaurant reviews", "Google Play Store app reviews for Zomato"],
    ["Customer context", "Restaurant opinion and dining-focused review text", "App and service journey covering delivery, refund, support, pricing, and app experience"],
    ["Research focus", "Primarily sentiment-classification performance", "End-to-end review analytics plus managerial interpretation"],
    ["Model emphasis", "Random Forest benchmark paper", "SentiLens with recreated Random Forest benchmark"],
    ["Output style", "Model-oriented findings", "Themes, trends, dashboard views, benchmark, and competitor context"],
  ];
  compareRows.forEach((row, idx) => {
    const y = 1.82 + idx * 0.78;
    addTableCell(slide, row[0], 0.5, y, 1.75, 0.78, {
      fill: colors.softBlue, align: "left", bold: true, fontSize: 8.9,
    });
    addTableCell(slide, row[1], 2.25, y, 3.1, 0.78, {
      fill: colors.white, align: "left", fontSize: 8.8,
    });
    addTableCell(slide, row[2], 5.35, y, 3.25, 0.78, {
      fill: colors.white, align: "left", fontSize: 8.8,
    });
  });
  slide.addText("Interpretation: the previous paper remains a useful benchmark, but our project studies a different feedback environment and extends the analysis from pure classification to decision-support insight.", {
    x: 0.68, y: 5.95, w: 8.0, h: 0.34,
    fontFace: "Calibri", fontSize: 10.2, italic: true, color: colors.muted, align: "center", margin: 0,
    fit: "shrink",
  });
  addFooter(slide, 18);
}

// Slide 18
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Competitor Context: Zomato vs Swiggy");
  addImagePanel(
    slide,
    "Brand-Level Comparison",
    FIG("dashboard_competitor_overview.png"),
    0.55,
    1.35,
    4.1,
    4.75,
    "Google Play-only sentiment benchmark"
  );
  addImagePanel(
    slide,
    "Theme-Level Comparison",
    FIG("dashboard_competitor_theme_comparison.png"),
    4.95,
    1.35,
    3.9,
    4.75,
    "Negative share and net sentiment by theme"
  );
  slide.addText("The competitor view adds market context by showing whether Zomato's brand-level and theme-level sentiment patterns are relatively stronger or weaker than a key food-delivery competitor under the same analytical framework.", {
    x: 0.7, y: 6.2, w: 8.0, h: 0.28,
    fontFace: "Calibri", fontSize: 9.8, color: colors.muted, italic: true, align: "center", margin: 0,
  });
  addFooter(slide, 19);
}

// Slide 19
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, "Managerial Implications, Limitations, and Conclusion");
  addTableCell(slide, "Managerial Implications", 0.55, 1.45, 2.6, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "Limitations", 3.15, 1.45, 2.4, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addTableCell(slide, "Conclusion", 5.55, 1.45, 3.3, 0.42, {
    fill: colors.lightBlue, lineColor: "B8CCE4", bold: true, fontSize: 10,
  });
  addBodyBullets(slide, [
    "Treat refund and cancellation as the highest strategic priority.",
    "Strengthen customer support as a service-recovery function.",
    "Maintain delivery reliability because it drives the largest feedback volume.",
    "Build on app experience as a relative digital strength.",
  ], { x: 0.65, y: 1.98, w: 2.4, h: 3.8, fontSize: 13.6, paraSpaceAfterPt: 8 });
  addBodyBullets(slide, [
    "Google Play-only dataset does not capture all customer voice channels.",
    "Rating-proxy sentiment is scalable but not a perfect representation of textual nuance.",
    "Rule-based theme assignment keeps only one final theme per review.",
    "Benchmark comparison with the prior paper is informative but not strictly like-for-like.",
  ], { x: 3.25, y: 1.98, w: 2.2, h: 3.8, fontSize: 13.3, paraSpaceAfterPt: 8 });
  addBodyBullets(slide, [
    "Objective 1 met: 41,597 Google Play reviews were collected, cleaned, normalized, and deduplicated into a final master dataset.",
    "Objective 2 met: sentiment was classified with SentiLens, which achieved 90.17% accuracy on the project holdout set.",
    "Objective 3 met: the analysis identified delivery, refund/cancellation, customer support, pricing/fees, and app experience as the main themes.",
    "Objective 4 met: the findings were translated into clear managerial priorities for service recovery and brand strategy."
  ], { x: 5.62, y: 1.98, w: 3.15, h: 3.95, fontSize: 12.4, paraSpaceAfterPt: 8 });
  addFooter(slide, 20);
}

const outPath = "C:/Users/sshrivastava/Downloads/mba-project/documentation/Zomato_Project_Final_Consolidated_Presentation.pptx";
pptx.writeFile({ fileName: outPath });
