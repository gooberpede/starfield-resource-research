# Known Facts

This file contains observations established by direct extraction, runtime testing, or repeated dataset validation. It should not contain unproven explanations of why those observations occur.

## Data Relationships

### PNDT references BIOM

Planet records (`PNDT`) contain biome references.

### PNDT contains RSCS

Planet records contain a Resource Creation Seed (`RSCS`). The seed participates in deterministic resource-generation behaviour.

### BIOM references RSGD

Biome records (`BIOM`) reference Resource Generation (`RSGD`) data.

### RSGD describes resource-generation possibility space

RSGD records contain resource-related generation data and references used by the game's resource-generation system. Changing relevant RSGD data can alter resource-generation outcomes.

## Runtime Resource Results

### Final planetary resources are determined at runtime

The complete final planet/resource set is not represented in `Starfield.esm` as a simple static planet-to-resource table suitable for authoritative extraction.

Runtime engine logic can be queried to obtain the final resource set.

### SurveyAggregator exposes final planet-wide resources

A native function referred to in this project as `SurveyAggregator`, RE ID `1016657`, can enumerate forms associated with a planet's completed survey/resource state.

Filtering its aggregated forms identifies authoritative final inorganic and organic planetary resources.

This function provides planet-wide results; it does not expose biome identity in the current implementation.

## Canonical Inorganic Dataset

An authoritative runtime-derived planet/resource dataset was built by joining runtime resource output to PNDT records from `Starfield.esm`.

Relevant counts from the analysed dataset:

- 5,999 inorganic planet/resource rows;
- 1,436 distinct bodies with inorganic resources;
- 45 distinct inorganic resource EditorIDs in the canonical inorganic export.

## Resource Families

Eight ordinary inorganic resource families are currently modelled.

### Aluminium family

Root: `Aluminum`

Known members:
- Aluminum
- Beryllium
- Neodymium
- Europium
- Indicite

### Nickel family

Root: `Nickel`

Known members:
- Nickel
- Cobalt
- Platinum
- Palladium
- Tasine

### Lead family

Root: `Lead`

Known members:
- Lead
- Tungsten
- Titanium
- Dysprosium
- Silver
- Mercury

### Uranium family

Root: `Uranium`

Known members:
- Uranium
- Iridium
- Vanadium
- Plutonium
- Vytinium

### Copper family

Root: `Copper`

Known members:
- Copper
- Fluorine
- Tetrafluorides
- IonicLiquids
- Gold
- Antimony

### Chlorine family

Root: `Chlorine`

Known members:
- Chlorine
- Chlorosilanes
- Lithium
- Caesium
- Xenon
- Aldumite

### Iron family

Root: `Iron`

Known members:
- Iron
- Alkanes
- Tantalum
- Ytterbium
- Rothicite

### Argon family

Root: `Argon`

Known members:
- Argon
- Benzene
- CarboxylicAcids
- Neon
- Veryl

### Standalone inorganic resources

The current family model treats these as standalone rather than members of the eight families:

- Water
- Helium3

## Root Invariant

For every analysed planet/family case containing at least one non-root family member, the family root was also present.

| Family | Bodies with descendant | Descendant occurrences | Missing root |
|---|---:|---:|---:|
| Aluminium | 242 | 320 | 0 |
| Nickel | 212 | 281 | 0 |
| Lead | 193 | 242 | 0 |
| Uranium | 144 | 195 | 0 |
| Copper | 225 | 311 | 0 |
| Chlorine | 206 | 283 | 0 |
| Iron | 163 | 219 | 0 |
| Argon | 164 | 213 | 0 |

Totals:

- 1,549 body/family cases;
- 2,064 descendant occurrences;
- 0 observed root violations.

This establishes a planet-level invariant in the analysed canonical data:

> If a planet contains a known descendant of an inorganic resource family, it also contains that family's root.

This does not by itself establish that the root and descendant are located in the same biome.

## Intermediate Members Are Not Mandatory

A planet can contain a deeper family member while skipping one or more intermediate family members.

Therefore the resource-family hierarchy is not simply a rule that all ancestors of an observed member must also be present.

The exception is the observed root invariant described above.

## Authoritative Biome Dataset

A dedicated xEdit exporter was built to extract planet-to-biome relationships from PNDT records.

For each PNDT biome entry it exports:

- PlanetFormID
- PlanetEditorID
- PlanetName
- BiomeIndex
- BiomeFormID
- BiomeEditorID
- BiomeName
- Chance

The full exported dataset contains 3,192 biome rows.

### Montara Luna validation

The exporter reproduced all six known Montara Luna biomes and their composition percentages, matching Creation Kit observations.

This validated the PNDT-to-BIOM extraction approach.

## Family Count Versus Biome Count

The canonical inorganic resource dataset was joined to the authoritative biome export by PlanetFormID.

For each body:

1. represented resource families were counted;
2. Water and Helium3 were excluded from the family count;
3. distinct biome records were counted.

Across all 1,436 analysed bodies with inorganic family resources:

> resource-family count was never greater than biome count.

Observed violations:

- 0

The minimum value of `BiomeCount - FamilyCount` was 0.

### Difference distribution

| BiomeCount - FamilyCount | Bodies |
|---|---:|
| 0 | 1,038 |
| 1 | 229 |
| 2 | 99 |
| 3 | 45 |
| 4 | 18 |
| 5 | 7 |

Thus 1,038 of 1,436 analysed bodies have exactly as many biomes as represented resource families.

### Single-biome bodies

Among the analysed family-bearing bodies:

- 880 bodies have exactly 1 represented family and exactly 1 biome;
- no single-biome body has more than 1 represented family.

This is a strong empirical constraint, but it does not by itself prove a universal one-family-per-biome rule.

## Unique Resources and Family Association

Treating certain unique resources as standalone families causes family-count/biome-count violations.

### Katydid III

When Indicite is treated as part of the Aluminium family:

```text
4 represented families
4 biomes
```

When Indicite is treated as its own family:

```text
5 represented families
4 biomes
```

### Decaran VII-b

When Vytinium is treated as part of the Uranium family:

```text
1 represented family
1 biome
```

When Vytinium is treated as its own family:

```text
2 represented families
1 biome
```

This independently supports modelling these unique resources as endpoints or members of their associated resource families.

## Creation Kit / Ghidra Findings

A Creation Kit resource-preview path was traced from:

```text
ResourceViewWidget::OnApplySeed
    ↓
FUN_1431bc320
    ↓
FUN_140e457b0
```

The path eventually reaches generic leveled-list evaluation machinery.

A value derived from the resource seed appeared to behave like an effective level/input to leveled-list selection rather than simply exposing an obvious direct PRNG reseed.

Searches of global MT19937 reseed sites did not reveal a simple, confirmed pattern of:

```text
RSCS -> seed global PRNG -> roll resources
```

No complete per-biome resource-allocation algorithm has yet been identified.

## Downstream Placement Lists

`LL_ResourceSurfaceFlora_*` leveled lists were investigated.

They appear to be downstream surface-placement machinery using conditions such as resource availability and rarity weighting.

They are not currently believed to be the primary mechanism that assigns a planet's resource families to biomes.
