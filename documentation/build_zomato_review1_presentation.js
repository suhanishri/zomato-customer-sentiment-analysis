const PptxGenJS = require("pptxgenjs");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "OpenAI Codex";
pptx.company = "OpenAI";
pptx.subject = "Zomato sentiment analysis presentation";
pptx.title = "Sentiment Analysis of Zomato Play Store Reviews for Brand Strategy";
pptx.lang = "en-IN";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-IN",
};

const colors = {
  navy: "0F172A",
  slate: "334155",
  teal: "0F766E",
  orange: "EA580C",
  sky: "0284C7",
  green: "166534",
  light: "F8FAFC",
  muted: "E2E8F0",
  text: "111827",
  subtext: "475569",
  white: "FFFFFF",
};

function addHeader(slide, title, subtitle = "") {
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.65,
    fill: { color: colors.navy },
    line: { color: colors.navy },
  });
  slide.addText(title, {
    x: 0.45,
    y: 0.14,
    w: 8.2,
    h: 0.26,
    fontFace: "Aptos Display",
    fontSize: 24,
    bold: true,
    color: colors.white,
    margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 8.5,
      y: 0.16,
      w: 4.2,
      h: 0.22,
      align: "right",
      fontSize: 10,
      color: "D6E4F0",
      margin: 0,
    });
  }
  slide.addShape(pptx.ShapeType.line, {
    x: 0.4,
    y: 0.78,
    w: 12.45,
    h: 0,
    line: { color: colors.muted, pt: 1.5 },
  });
}

function addFooter(slide, pageNum) {
  slide.addText(`Review 1 | ${pageNum}`, {
    x: 11.7,
    y: 7.0,
    w: 1.0,
    h: 0.18,
    fontSize: 9,
    align: "right",
    color: "64748B",
    margin: 0,
  });
}

function addBullets(slide, items, opts = {}) {
  const x = opts.x ?? 0.8;
  const y = opts.y ?? 1.4;
  const w = opts.w ?? 11.7;
  const h = opts.h ?? 4.8;
  const fontSize = opts.fontSize ?? 20;
  const color = opts.color ?? colors.text;

  const runs = [];
  for (const item of items) {
    runs.push({
      text: item,
      options: { bullet: { indent: 18 } },
    });
  }
  slide.addText(runs, {
    x,
    y,
    w,
    h,
    fontFace: "Aptos",
    fontSize,
    color,
    breakLine: true,
    paraSpaceAfterPt: 16,
    valign: "top",
    margin: 0.03,
  });
}

function addPill(slide, text, x, y, w, fillColor, textColor = colors.white) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: 0.42,
    rectRadius: 0.08,
    fill: { color: fillColor },
    line: { color: fillColor },
  });
  slide.addText(text, {
    x: x + 0.08,
    y: y + 0.08,
    w: w - 0.16,
    h: 0.18,
    fontSize: 10,
    bold: true,
    align: "center",
    color: textColor,
    margin: 0,
  });
}

function addWorkflowStep(slide, num, title, body, x, y, color) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w: 2.35,
    h: 1.65,
    rectRadius: 0.06,
    fill: { color: "F8FAFC" },
    line: { color: color, pt: 1.5 },
    shadow: { type: "outer", color: "CBD5E1", angle: 45, blur: 1, distance: 1, opacity: 0.15 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: x + 0.14,
    y: y + 0.15,
    w: 0.45,
    h: 0.45,
    fill: { color },
    line: { color },
  });
  slide.addText(String(num), {
    x: x + 0.14,
    y: y + 0.23,
    w: 0.45,
    h: 0.14,
    align: "center",
    fontSize: 12,
    bold: true,
    color: colors.white,
    margin: 0,
  });
  slide.addText(title, {
    x: x + 0.68,
    y: y + 0.14,
    w: 1.45,
    h: 0.28,
    fontSize: 16,
    bold: true,
    color: colors.navy,
    margin: 0,
  });
  slide.addText(body, {
    x: x + 0.16,
    y: y + 0.68,
    w: 2.0,
    h: 0.72,
    fontSize: 10,
    color: colors.subtext,
    valign: "mid",
    margin: 0,
  });
}

// Slide 1
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.light };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 7.5,
    fill: { color: colors.light },
    line: { color: colors.light },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.55,
    fill: { color: colors.orange },
    line: { color: colors.orange },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.65,
    y: 1.05,
    w: 0.18,
    h: 3.8,
    fill: { color: colors.teal },
    line: { color: colors.teal },
  });
  slide.addText("Sentiment Analysis of Zomato Play Store Reviews for Brand Strategy", {
    x: 1.1,
    y: 1.15,
    w: 9.7,
    h: 1.45,
    fontFace: "Aptos Display",
    fontSize: 24,
    bold: true,
    color: colors.navy,
    margin: 0,
  });
  slide.addText("MBA Project Presentation | Review 1", {
    x: 1.12,
    y: 2.72,
    w: 4.4,
    h: 0.35,
    fontSize: 17,
    color: colors.teal,
    bold: true,
    margin: 0,
  });
  slide.addText("Prepared by: Suhani Shrivastava (24EMBA1442)\nGuide: Dr. Suraj PG\nVIT Online Learning Program | May 2026", {
    x: 1.12,
    y: 3.35,
    w: 5.4,
    h: 1.0,
    fontSize: 16,
    color: colors.subtext,
    breakLine: true,
    margin: 0,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 8.8,
    y: 1.2,
    w: 3.7,
    h: 4.55,
    rectRadius: 0.08,
    fill: { color: "E0F2FE" },
    line: { color: colors.sky, pt: 1.5 },
  });
  slide.addText("Project Focus", {
    x: 9.2,
    y: 1.55,
    w: 2.5,
    h: 0.3,
    fontSize: 18,
    bold: true,
    color: colors.navy,
    margin: 0,
  });
  addPill(slide, "Zomato only", 9.2, 2.1, 2.1, colors.teal);
  addPill(slide, "Google Play reviews", 9.2, 2.62, 2.8, colors.sky);
  addPill(slide, "NLP + theme analysis", 9.2, 3.14, 2.95, colors.orange);
  addPill(slide, "Brand strategy insights", 9.2, 3.66, 3.0, colors.green);
  slide.addText("Presentation updates the earlier broad “social media” framing and aligns the study with the final project scope.", {
    x: 9.2,
    y: 4.3,
    w: 2.8,
    h: 0.8,
    fontSize: 11,
    color: colors.subtext,
    margin: 0,
  });
  addFooter(slide, 1);
}

// Slide 2
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addHeader(slide, "Problem Statement", "Why this study matters");
  addBullets(slide, [
    "Zomato receives a large volume of app reviews that reflect real customer experiences with delivery, refunds, pricing, customer support, trust, and app usability.",
    "These reviews strongly influence brand perception and future customer decisions, but the data is unstructured and difficult to analyze manually at scale.",
    "A rating alone shows satisfaction level, but not the specific reasons behind praise, frustration, or repeated complaints.",
    "An NLP-based review analysis can convert this feedback into actionable insights for customer experience improvement and brand strategy."
  ], { x: 0.85, y: 1.35, w: 11.7, h: 4.9, fontSize: 20 });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 8.85, y: 5.8, w: 3.55, h: 0.72,
    rectRadius: 0.05, fill: { color: "FFF7ED" }, line: { color: colors.orange, pt: 1.3 }
  });
  slide.addText("Core challenge: turning raw reviews into strategic decisions", {
    x: 9.05, y: 6.03, w: 3.15, h: 0.2,
    fontSize: 11, bold: true, align: "center", color: colors.orange, margin: 0
  });
  addFooter(slide, 2);
}

// Slide 3
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addHeader(slide, "Aim and Research Question", "Study direction");
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.8, y: 1.3, w: 5.8, h: 4.8,
    rectRadius: 0.06, fill: { color: "F8FAFC" }, line: { color: colors.teal, pt: 1.5 }
  });
  slide.addText("Aim of the Project", {
    x: 1.1, y: 1.65, w: 2.5, h: 0.3, fontSize: 19, bold: true, color: colors.teal, margin: 0
  });
  slide.addText("To analyze customer sentiment toward Zomato through Google Play Store reviews and derive actionable insights that support stronger brand strategy and better customer experience decisions.", {
    x: 1.1, y: 2.2, w: 5.0, h: 2.2, fontSize: 18, color: colors.text, margin: 0
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 6.95, y: 1.3, w: 5.55, h: 4.8,
    rectRadius: 0.06, fill: { color: "F8FAFC" }, line: { color: colors.sky, pt: 1.5 }
  });
  slide.addText("Research Question", {
    x: 7.25, y: 1.65, w: 2.7, h: 0.3, fontSize: 19, bold: true, color: colors.sky, margin: 0
  });
  slide.addText("How can NLP-based analysis of Zomato app reviews help identify customer sentiment, dominant service issues, and improvement opportunities for brand strategy?", {
    x: 7.25, y: 2.2, w: 4.7, h: 2.0, fontSize: 18, color: colors.text, margin: 0
  });
  addFooter(slide, 3);
}

// Slide 4
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addHeader(slide, "Objectives", "What the project will deliver");
  addBullets(slide, [
    "Collect and preprocess Zomato-related Google Play Store reviews.",
    "Classify reviews into positive, negative, and neutral sentiment categories.",
    "Identify major themes such as delivery, refund and cancellation, app experience, customer support, pricing, and trust.",
    "Interpret theme-wise sentiment patterns to understand customer pain points and strengths.",
    "Translate the findings into practical recommendations for brand strategy and customer experience improvement."
  ], { x: 0.95, y: 1.35, w: 11.4, h: 5.2, fontSize: 20 });
  addFooter(slide, 4);
}

// Slide 5 - new
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addHeader(slide, "Scope of the Study", "Added slide");
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.9, y: 1.4, w: 5.6, h: 4.9,
    rectRadius: 0.06, fill: { color: "F8FAFC" }, line: { color: colors.orange, pt: 1.4 }
  });
  slide.addText("Included in Scope", {
    x: 1.18, y: 1.72, w: 2.5, h: 0.3, fontSize: 18, bold: true, color: colors.orange, margin: 0
  });
  addBullets(slide, [
    "Zomato as the primary brand under study.",
    "Google Play Store reviews as the main data source.",
    "Three retrieval modes: newest, most relevant, and rating-based.",
    "English and Hindi review exports after cleaning and deduplication.",
    "Later-stage competitor comparison only as supporting context."
  ], { x: 1.15, y: 2.15, w: 4.9, h: 3.6, fontSize: 17 });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 6.85, y: 1.4, w: 5.6, h: 4.9,
    rectRadius: 0.06, fill: { color: "F8FAFC" }, line: { color: colors.teal, pt: 1.4 }
  });
  slide.addText("Outside Main Scope", {
    x: 7.13, y: 1.72, w: 2.8, h: 0.3, fontSize: 18, bold: true, color: colors.teal, margin: 0
  });
  addBullets(slide, [
    "Broad social media sources such as YouTube or Reddit are not part of the core study presentation.",
    "Campaign-effect evaluation is not the primary focus of this project.",
    "The presentation concentrates on customer perception through app review analytics."
  ], { x: 7.1, y: 2.15, w: 4.95, h: 3.3, fontSize: 17 });
  addFooter(slide, 5);
}

// Slide 6 - new
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addHeader(slide, "Research Methodology", "Added slide");
  slide.addText("Workflow used for the Play Store review analysis", {
    x: 0.9, y: 1.08, w: 5.0, h: 0.22, fontSize: 14, color: colors.subtext, margin: 0
  });
  addWorkflowStep(slide, 1, "Collect", "Extract reviews from Google Play under multiple sort settings.", 0.75, 1.55, colors.sky);
  addWorkflowStep(slide, 2, "Clean", "Remove low-value, duplicate, irrelevant, and noisy records.", 3.32, 1.55, colors.teal);
  addWorkflowStep(slide, 3, "Label", "Map ratings to sentiment and assign dominant service themes.", 5.89, 1.55, colors.orange);
  addWorkflowStep(slide, 4, "Analyze", "Study sentiment distribution and theme-level customer issues.", 8.46, 1.55, colors.green);
  addWorkflowStep(slide, 5, "Recommend", "Translate findings into brand and customer experience actions.", 11.03, 1.55, "7C3AED");
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.05, y: 4.25, w: 11.2, h: 1.35,
    rectRadius: 0.05, fill: { color: "EFF6FF" }, line: { color: colors.sky, pt: 1.1 }
  });
  slide.addText("Current dataset base: 41,597 unique cleaned Zomato Play Store reviews collected across multiple retrieval settings. Sentiment is derived using a rating proxy, and themes are assigned using transparent rule-based classification.", {
    x: 1.35, y: 4.67, w: 10.6, h: 0.52, fontSize: 15, color: colors.navy, align: "center", margin: 0
  });
  addFooter(slide, 6);
}

// Slide 7
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addHeader(slide, "Expected Outcomes", "What the study should reveal");
  addBullets(slide, [
    "A clear view of overall positive, negative, and neutral sentiment toward Zomato.",
    "Identification of the strongest drivers of dissatisfaction such as delivery, refunds, pricing, support, or app issues.",
    "Theme-wise understanding of customer expectations and recurring service pain points.",
    "Evidence-based managerial recommendations for improving customer experience and brand perception.",
    "A structured base for later competitor comparison and dashboard-driven interpretation."
  ], { x: 0.9, y: 1.35, w: 11.5, h: 4.9, fontSize: 20 });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 8.8, y: 5.78, w: 3.55, h: 0.76,
    rectRadius: 0.05, fill: { color: "ECFDF5" }, line: { color: colors.green, pt: 1.2 }
  });
  slide.addText("Outcome focus: practical business insight, not just model output", {
    x: 9.0, y: 6.02, w: 3.15, h: 0.2, fontSize: 11, bold: true, align: "center", color: colors.green, margin: 0
  });
  addFooter(slide, 7);
}

const outPath = "C:/Users/sshrivastava/Downloads/mba-project/documentation/Social Media Sentiment Analysis for Brand Strategy - revised.pptx";
pptx.writeFile({ fileName: outPath });
