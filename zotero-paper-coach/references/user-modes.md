# User modes

Use this file to map real reader jobs to annotation behavior.

## Interaction rule

Ask for the user mode only when it is missing or ambiguous.
Do not dump every setting unless the user wants fine control.

Default user mode:

- goal: beginner-learning
- style: mentor
- density: medium
- note depth: explain

## Goal modes

### beginner-learning

Reader wants:

- to understand what the paper is asking
- to understand what the paper found
- help translating jargon into plain language

Prioritize:

- research question
- problem importance
- contribution framing
- main findings
- limitations
- reading-order hints

Avoid:

- drowning the user in method minutiae too early

### quick-read

Reader wants:

- the thesis fast
- only the highest-value lines

Prioritize:

- abstract
- contribution list
- strongest results
- one major caveat
- conclusion

Avoid:

- dense methods highlighting

### exam-prep

Reader wants:

- memorable structure
- likely testable definitions and contrasts

Prioritize:

- definitions
- framework terms
- compare/contrast lines
- result statements
- reusable restatement notes

### literature-review

Reader wants:

- field positioning
- novelty claim
- citable synthesis
- scope boundaries

Prioritize:

- gap statements
- novelty claims
- strongest evidence lines
- limitation statements
- orange reuse-worthy lines

### replication

Reader wants:

- implementation-critical detail
- evaluation setup
- things likely to break reproducibility

Prioritize:

- datasets and splits
- parameters and configuration
- metric definitions
- evaluation protocol
- caveats and hidden assumptions

### citation-harvest

Reader wants:

- reusable claims without overclaiming
- quotable definitions and bounded conclusions

Prioritize:

- precise scoped findings
- definition lines
- limitation lines that constrain reuse
- orange summary lines

## Style overlays

### mentor

- explain generously
- add `[人话]` and `[为什么重要]`
- teach reading order

### top-student

- compress aggressively
- mark high-yield lines
- add `[复述]` for recall

### critical-researcher

- look for overclaim risk
- highlight assumptions, baselines, and scope limits
- bias toward pink and orange when justified

### executive-brief

- annotate sparingly
- prefer only claims, strongest evidence, and one limitation
- keep notes short

## Density overlays

### light

- only backbone passages
- minimal notes

### medium

- backbone plus key evidence
- at least one caveat per major result section when available

### heavy

- include evidence chain and method anchors
- add notes where a capable but tired reader would stumble

### teaching

- include prompts, plain-language notes, and section guidance
- accept some extra visual load, but never yellow-wallpaper the PDF
- for medium-length philosophy/theory papers, this often means 20+ highlight anchors, not merely lots of side notes

## Hard rule

A high-value run should try to preserve all four when the paper allows it:

- one core claim
- one key evidence anchor
- one limitation or caveat
- one reusable conclusion-level line
