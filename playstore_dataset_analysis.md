# Play Store Dataset Analysis for Zomato Sentiment Project

## Files analyzed
- `output_playstore_newest_en`
- `output_playstore_relevant_en`
- `output_playstore_rating_en`
- `output_playstore_newest_hi`
- `output_playstore_relevant_hi`
- `output_playstore_rating_hi`

## Big picture
These six Play Store exports are strong enough to become the main base for your sentiment dataset.

- Cleaned English union across all three sorts: 41,310 unique reviews
- Cleaned Hindi union across all three sorts: 353 unique reviews
- Cleaned total union across all six exports: 41,663 unique reviews
- Cleaned YouTube comments previously analyzed: 1,408
- Current combined cleaned Zomato dataset size from Play Store + YouTube: about 43,071

This means Zomato-only cleaned data is already substantial, but still below your target of 50,000 if you want a single final cleaned dataset. Competitor data such as Swiggy will likely be useful both for comparison and for reaching the target.

## Raw vs cleaned capacity
- Raw English union across the three sorts: 71,783 unique reviews
- Raw Hindi union across the three sorts: 6,722 unique reviews
- Raw total union across all six exports: 78,505 unique reviews

So the raw review pool is large enough, but the current relevance filters reduce it significantly.

## Export-by-export summary

### 1. `output_playstore_newest_en`
- Raw rows: 20,000
- Cleaned rows: 2,565
- Retention: 12.83%
- Date range: 2026-03-08 to 2026-03-29
- Average score: 2.83
- Main value:
  Very recent reviews, good for current brand pulse
- Main weakness:
  Much smaller than the other English datasets

### 2. `output_playstore_relevant_en`
- Raw rows: 30,000
- Cleaned rows: 24,064
- Retention: 80.21%
- Date range: 2018-09-12 to 2026-03-28
- Average score: 1.86
- Main value:
  Largest and richest issue-focused dataset
- Main weakness:
  Strong negative skew because “most relevant” tends to surface complaints and highly engaged problem reviews

### 3. `output_playstore_rating_en`
- Raw rows: 30,000
- Cleaned rows: 19,217
- Retention: 64.06%
- Date range: 2018-09-12 to 2026-03-28
- Average score: 5.00
- Main value:
  Strong positive set for comparison and class balancing
- Main weakness:
  Entire cleaned set is 5-star, so it is highly biased and should not be treated as a natural sample

### 4. Hindi exports
- `newest_hi`: 347 cleaned
- `relevant_hi`: 340 cleaned
- `rating_hi`: 347 cleaned

Main finding:
- Hindi exports add very little unique data
- They are almost complete duplicates of each other
- Together they add only 353 unique cleaned reviews

## Overlap across exports

### English overlap
- `newest_en` vs `relevant_en`: 1,282 shared cleaned reviews
- `newest_en` vs `rating_en`: 588 shared cleaned reviews
- `relevant_en` vs `rating_en`: 3,025 shared cleaned reviews

### Hindi overlap
- `newest_hi` vs `relevant_hi`: 95.73% Jaccard overlap
- `newest_hi` vs `rating_hi`: 96.60% Jaccard overlap
- `relevant_hi` vs `rating_hi`: 96.85% Jaccard overlap

Interpretation:
- English exports are complementary enough to merge after deduplication
- Hindi exports are nearly redundant, so keeping all three separately does not add much value

## Rating distribution in deduplicated cleaned union
- 1-star: 17,401
- 2-star: 1,526
- 3-star: 1,187
- 4-star: 1,777
- 5-star: 19,772

This is much more balanced than any one export alone.

## Theme distribution in deduplicated cleaned union
- Delivery: 15,549
- App UX: 7,541
- Refund: 5,208
- Customer support: 3,858
- Other: 4,148
- Trust / reviews: 1,650
- Order issue: 1,526
- Pricing / fees: 959
- Competitor comparison: 899
- Food quality: 325

The strongest business themes for Zomato’s app-review brand analysis are therefore:
- delivery reliability
- app usability / technical friction
- refunds
- customer support
- trust and review transparency
- pricing and fees

## Time coverage of deduplicated cleaned union
- 2018: 1,357
- 2019: 9,510
- 2020: 2,999
- 2021: 4,888
- 2022: 4,166
- 2023: 3,380
- 2024: 2,758
- 2025: 5,920
- 2026: 6,684

Recent subset counts:
- 2024 and later: 15,362
- 2025 and later: 12,604
- 2026 only: 6,684

Interpretation:
- If you want “current brand perception,” the newest export is useful but too small alone
- If you want a large training dataset, the combined union is strong
- If you want a recent analytics dashboard, you may want a filtered dashboard view for 2024+ or 2025+

## Important quality caution: rating is not perfect sentiment ground truth
Some high-rating reviews contain negative complaint text, and some low-rating reviews mention positive words while still being clearly dissatisfied overall.

Examples found:
- 5-star review text complaining about no refund, poor food quality, hidden charges
- 5-star review text calling the app “fraud”
- 1-star review text beginning with “Previously the app was good” or “I loved Zomato”

Implication:
- App star rating is useful as a weak label
- But it should not be treated as perfectly clean sentiment ground truth without text-based validation

## Best use of these datasets

### For final training dataset
Best candidate:
- Merge `relevant_en`, `rating_en`, `newest_en`
- Deduplicate by `source_id`
- Add only the union of Hindi reviews once, not all three Hindi exports

Why:
- This gives maximum unique coverage
- It also gives a mix of strongly negative, strongly positive, and recent reviews

### For dashboard analytics
Best candidate:
- Keep the merged master dataset
- Add filters for:
  - source = Play Store / YouTube
  - year
  - score
  - theme
  - language
  - competitor mention

### For current brand strategy interpretation
Strongest app-review signals are:
- delivery delays and failures
- poor or inaccessible support
- refund dissatisfaction
- app bugs and usability pain
- pricing and hidden-charge frustration

## Recommendation for next step
Build one master cleaned Play Store dataset with:
- `source_id`-based deduplication
- source folder metadata such as `sort_mode` and `lang`
- normalized sentiment label from star score
- theme label from `theme_hint`
- date-based recency bucket

After that, combine it with the YouTube dataset using a common schema and then start the dashboard layer.
