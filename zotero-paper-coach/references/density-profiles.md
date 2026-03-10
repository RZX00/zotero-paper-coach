# Density profiles

Use density to control annotation coverage and note frequency.

## Density model

Judge density primarily by **highlight anchors**, not by total annotation objects.
A run with 15 highlights + 15 text notes is still only 15 marked passages, not "30-density".

Do **not** decide density from a fixed global count alone.
Compute it dynamically from the document itself:

1. **body_pages**: count body pages only when possible
   - exclude references, appendices, index-like pages when identifiable
2. **body_words**: estimate total words in body text
3. **paragraph_density**: estimate average meaningful paragraphs per body page
4. **paper_type_adjustment**:
   - philosophy / theory / legal argument / dense humanities prose -> increase target
   - formula-heavy or figure-heavy papers -> moderate target if prose is thin

### Dynamic targeting principle

Use both page length and word volume.
If they disagree, prefer the **larger implied target**, then adjust for paragraph density.

A practical baseline:

- page_signal = body_pages × page_multiplier
- word_signal = body_words ÷ word_divisor
- raw_target = max(page_signal, word_signal)
- then adjust ±10% to ±25% based on paragraph density and paper type

This is the thing to optimize, not a fixed summary count.

### Recommended baseline parameters

- `light`: page_multiplier ≈ 0.8, word_divisor ≈ 1800
- `medium`: page_multiplier ≈ 1.2, word_divisor ≈ 1300
- `heavy`: page_multiplier ≈ 1.6, word_divisor ≈ 950
- `teaching`: page_multiplier ≈ 2.0, word_divisor ≈ 800

### Reading the result

For example, a medium-length philosophy paper with:

- 12 body pages
- ~7200 body words
- dense argumentative paragraphs

would imply roughly:

- page_signal for teaching ≈ 24
- word_signal for teaching ≈ 9
- choose the larger signal -> 24
- then increase for dense philosophy prose if needed

So a teaching run landing at 17 highlights would be under target.

### Hard rule

When reporting density to the user, describe it in relation to:

- body pages
- body word count or wordiness
- paragraph density
- actual highlight anchors written

Do not call something "dense" just because the absolute number sounds big.

## light

Goal: fast orientation.

Target:
- usually about 6-12 highlight anchors total
- dynamically computed, but often around 0.5 to 1 anchor per body page

Rules:
- annotate only section backbone
- add notes only where they materially improve understanding
- prefer abstract, gap, contribution, one result anchor, one limitation, conclusion

## medium

Goal: useful study copy without clutter.

Target:
- usually about 10-18 highlight anchors total
- dynamically computed, but often around 1 to 1.4 anchors per body page

Rules:
- annotate backbone plus key evidence sentences
- add 1 to 2 notes per major section
- include at least one limitation highlight in results/discussion
- suitable default for most users

## heavy

Goal: deep self-study and review writing.

Target:
- usually about 15-25 highlight anchors total
- dynamically computed, but often around 1.4 to 1.8 anchors per body page
- this is the first mode that should feel clearly dense

Rules:
- include evidence chains, methods anchors, and limitation details
- add notes where a novice would likely stumble
- use paragraph coverage, not just section token markers
- for argument-dense philosophy or theory papers, prefer the upper half of the range

## teaching

Goal: turn the paper into a guided lesson.

Target:
- usually about 18-35 highlight anchors total
- dynamically computed, but often around 1.8 to 2.5 anchors per body page
- for medium-length philosophy papers, often 20+ anchors is more honest
- do not call it dense if it ends up below 15 highlight anchors

Rules:
- include reading-order notes
- include plain-language translations
- include “why this matters” notes
- include selective prompts like “compare this claim to the evidence in Figure 2”
- annotate enough paragraphs that the reader feels actively guided, not merely signposted
- best for beginners, but can become visually busy

## Anti-patterns

Do not:
- mark consecutive sentences when one sentence can anchor the paragraph
- annotate formula boilerplate unless it matters to the user goal
- mark citations unless the surrounding sentence carries argument value
- flood methods with blue highlights if the user wants only quick understanding
