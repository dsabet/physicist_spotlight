# Physicist Spotlight Project

## Objective

Find a scientist or mathematician whose work made a substantial contribution to physics, and whose life, education, career, or experiences illustrate diversity, equity, inclusion, persistence, discrimination, or a nontraditional path into science.

The person does not need to have formally held the title of "physicist."

Mathematicians and scientists from adjacent fields are eligible when their work had a clear and substantial influence on physics. Examples include mathematicians who developed mathematical structures, theorems, or methods that became foundational to physical theories.

A candidate should therefore satisfy at least one of the following:

- Primarily worked as a physicist.
- Made important contributions directly to a field of physics.
- Developed mathematical theories or methods that became foundational to important areas of physics.
- Worked in another scientific discipline but made a clearly documented contribution to physical theory or our understanding of physical phenomena.

For candidates who were primarily mathematicians or worked outside physics, the connection to physics must be explicitly documented by reliable sources. Do not select someone merely because their mathematics could theoretically be applied to physics.

Examples of appropriate cross-disciplinary candidates include figures such as Emmy Noether, whose mathematical work had a foundational and well-documented impact on theoretical physics.

## Important constraints

Never select someone already present in any CSV under `data/`.

Do not infer race, ethnicity, religion, disability, sexual orientation, socioeconomic background, or other personal characteristics from a name, photograph, nationality, or indirect evidence.

Any personal characteristic, barrier, discrimination, or unusual life experience mentioned in the spotlight must be explicitly supported by a reliable source.

Wikipedia may be used for candidate discovery, but important biographical claims and the candidate's connection to physics should be verified against an additional credible source whenever possible.

Prefer sources such as:
- university or laboratory biographies
- professional scientific societies
- oral history archives
- published interviews
- reputable museums or scientific institutions
- major encyclopedias

Do not use unsourced blogs or AI-generated pages as factual sources.

The final spotlight should explain both:

1. Why the person's scientific or mathematical work matters to physics.
2. What documented aspect of their life or career makes them relevant to the project's diversity, equity, inclusion, persistence, or nontraditional-path theme.

## Workflow

1. Read all historical CSVs and understand:
   - people already used
   - CSV schema
   - typical excerpt length
   - writing tone and structure

2. Delegate candidate discovery to candidate_researcher agents.
   Researchers must return evidence and URLs and must not modify files.

3. Select the strongest candidate who:
   - is clearly a physicist
   - is not already represented
   - has a well-sourced story relevant to the project
   - has sufficient reliable biographical evidence

4. Delegate verification to fact_checker.

5. If verification passes, delegate drafting to spotlight_writer.

6. Validate the proposed row with the scripts in `scripts/`.

7. Append exactly one row to `data/physicists.csv`.

Never overwrite or rewrite previous rows.

## Documentation

Selection rules:
`docs/selection-criteria.md`

Acceptable sources:
`docs/source-policy.md`

Writing examples and style:
`docs/writing-style.md`

CSV fields:
`docs/csv-schema.md`