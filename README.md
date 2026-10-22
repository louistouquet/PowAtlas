# PowAtlas

*[Version française](README.fr.md)*

PowAtlas is an open-source system to understand and forecast snow in the mountains, starting with the French Alps. It aims to tell how much snow will fall, where and at what elevation, and how the snowpack evolves — with every claim backed by public verification scores.

**Status:** SP1 in progress. The daily collection of open forecasts (ICON-D2, ICON-EU, AROME, ARPEGE, IFS, AIFS) and of observations that stay online only a few days runs on GitHub Actions since October 2026; the reference archive is kept on the maintainer's machine. **No forecast or score is published yet.**

## Principles

- **Open data only**: every data source is documented with its licence and attributed.
- **Zero euro**: free tiers only, for compute and hosting alike.
- **Public scores**: no quality claim without a published comparison against a reference.
- **No avalanche safety verdicts, ever.** PowAtlas informs and analyses; the official avalanche bulletin (BRA, Météo-France) remains the reference.

## Roadmap

| # | Sub-project | Content |
|---|---|---|
| SP0 | Foundations | Vision, method, tooling, public repository, initial research (R0), target and roadmap |
| SP1 | Archive and observations | Daily archive of open forecasts, observations, reanalyses, satellite; open publication |
| SP2 | Scoreboard | Automatic, public verification of forecasts against observations |
| SP3 | Forecast v1 | Terrain downscaling, machine-learning correction, model blending, probabilities, powder alerts |
| SP4 | Snowpack | Snow layers and snow quality by massif, elevation and aspect |
| SP5 | Advanced AI research | AI weather models, enters production only if it wins on the scoreboard |
| SP6 | Products | Open API, website, map, alerts, live resort conditions |

More in the vision document (French): [`docs/vision.md`](docs/vision.md). Documentation index: [`docs/README.md`](docs/README.md).

## Data collection

The `powatlas` Python package (`src/powatlas/`) collects, crops to the French Alps and archives each source as published, with a manifest per unit (sha256, producer's Last-Modified, missing fields). Sources and schedules: [`src/powatlas/catalogue.toml`](src/powatlas/catalogue.toml); workflow: [`.github/workflows/collect.yml`](.github/workflows/collect.yml); design (French): [`docs/specs/2026-10-22-sp1-archive-design.md`](docs/specs/2026-10-22-sp1-archive-design.md). No data is stored in Git.

## Contributing and licences

- How to contribute: [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Code: [Apache-2.0](LICENSE) (see also [`NOTICE`](NOTICE)).
- Data, models and documentation produced by the project: CC-BY-4.0; third-party data keeps its own licence — see [`DATA_LICENSES.md`](DATA_LICENSES.md).
