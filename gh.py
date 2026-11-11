#!/usr/bin/env python3
"""
Generate a GitHub repo list related to AI/ML + energy.

The script:
- Searches GitHub across many AI/ML + energy buckets.
- Adds LF Energy-inspired search terms.
- Deduplicates repos.
- Filters out generic AI/ML repos unless energy relevance is detected.
- Classifies repos by category and relevance.
- Exports Markdown and CSV.

Recommended:
  export GITHUB_TOKEN=github_pat_your_token_here

Run:
  python github_energy_ai_ml_repos.py \
    --limit 250 \
    --min-stars 100 \
    --max-pages-per-bucket 5 \
    --deep-readme \
    --include-weak

Strict 500-star run:
  python github_energy_ai_ml_repos.py \
    --limit 250 \
    --min-stars 500 \
    --max-pages-per-bucket 5 \
    --deep-readme \
    --include-weak
"""

from __future__ import annotations

import argparse
import base64
import csv
import os
import re
import sys
import time
from dataclasses import dataclass
from typing import Any

import requests


GITHUB_API = "https://api.github.com"


SEARCH_BUCKETS = [
    # Core AI/ML + energy buckets
    "energy forecasting",
    "load forecasting",
    "electricity forecasting",
    "power load forecasting",
    "electricity demand forecasting",
    "energy demand forecasting",
    "smart grid machine learning",
    "smart grid reinforcement learning",
    "power system machine learning",
    "power grid reinforcement learning",
    "optimal power flow machine learning",
    "renewable energy forecasting",
    "solar forecasting machine learning",
    "wind forecasting machine learning",
    "battery optimization machine learning",
    "energy management reinforcement learning",
    "building energy machine learning",
    "HVAC reinforcement learning",
    "non intrusive load monitoring",
    "NILM machine learning",
    "smart meter machine learning",
    "electric vehicle charging optimization",
    "demand response reinforcement learning",
    "energy price forecasting",
    "electricity price forecasting",
    "energy dataset machine learning",
    "power systems dataset machine learning",

    # LF Energy project-name inspired buckets
    "AINETUS grid AI",
    "AINETUS power grid",
    "Arras GridLAB-D smart grid",
    "HiPAS GridLAB-D renewable energy",
    "Battery Data Alliance battery data",
    "CDS Customer Data utility customer data",
    "CDS Power Systems Data grid emissions",
    "CDS Registration energy systems",
    "CitrineOS EV charging",
    "CoMPAS IEC 61850 power",
    "covXtreme extreme value model energy",
    "CUPID IEEE 2030.5 DER",
    "Dynawo power systems simulation",
    "EVerest EV charging",
    "FIDOpower power systems data model",
    "FlexMeasures energy flexibility",
    "GEISA grid edge computing",
    "Grid2Op power grid control",
    "GridVantage extreme weather grid",
    "GXF grid exchange fabric",
    "Hyphae microgrid",
    "NODE Collective energy incentives data",
    "OpenDSM energy usage prediction",
    "OpenEEmeter energy prediction",
    "OpenGridFM foundation models power grids",
    "openLEADR OpenADR demand response",
    "OpenSTEF machine learning load forecasting",
    "OpenSynth synthetic energy data AI",
    "OperatorFabric smart assistant grid operator",
    "ORES intelligent energy systems",
    "p-SWAMP AI assisted power system operations",
    "Power Grid Model distribution power system analysis",
    "PowSyBl power system simulation",
    "RTDIP real time data ingestion energy analytics",
    "Real Time Data Ingestion Platform energy analytics",
    "RTC-Tools energy optimization",
    "SC Decarbonisation Hub emissions data",
    "Semantic Energy Framework ontology energy",
    "Shapeshifter flexibility forecasting",
    "SOGNO data driven grid monitoring",
    "TROLIE transmission facility ratings",
    "URPX utility rate plan data",

    # Grid AI and decision support
    "AI based decision support grid operations",
    "AI assisted power system operations",
    "smart assistant grid operators",
    "foundation models power grids",
    "large language model power grid",
    "LLM power grid",
    "graph neural network power grid",
    "power grid anomaly detection",
    "power grid situational awareness",
    "power grid operator assistant",
    "grid operations decision support",
    "grid control reinforcement learning",
    "intelligent power grid control",
    "power system reinforcement learning",
    "power system deep learning",

    # Grid simulation and modeling
    "power system simulation machine learning",
    "grid simulation machine learning",
    "distribution grid simulation",
    "transmission grid simulation",
    "dynamic power system simulation",
    "steady state distribution power system",
    "power flow machine learning",
    "load flow machine learning",
    "optimal power flow deep learning",
    "security constrained optimal power flow machine learning",
    "modelica power systems",
    "gridlab-d machine learning",
    "gridlab-d smart grid",
    "digital twin power grid",
    "power grid digital twin",

    # DER, flexibility, OpenADR, IEEE 2030.5
    "distributed energy resources machine learning",
    "DER forecasting",
    "DER optimization",
    "DER communication IEEE 2030.5",
    "IEEE 2030.5 energy",
    "OpenADR demand response",
    "OpenADR machine learning",
    "energy flexibility forecasting",
    "energy flexibility optimization",
    "flexibility forecasting energy",
    "flexibility market energy",
    "virtual power plant optimization",
    "VPP optimization machine learning",
    "distributed energy resource management system",
    "DERMS optimization",
    "transactive energy machine learning",

    # EV charging and batteries
    "EV charging optimization machine learning",
    "EV charging load forecasting",
    "EV charging demand forecasting",
    "OCPP EV charging analytics",
    "OCPP machine learning",
    "battery data analytics",
    "battery state of charge machine learning",
    "battery state of health machine learning",
    "battery degradation machine learning",
    "battery energy storage optimization",
    "BESS optimization machine learning",
    "vehicle grid integration machine learning",
    "V2G optimization machine learning",

    # Grid edge, substations, IEC 61850, protection, control
    "grid edge computing AI",
    "grid edge analytics",
    "digital substation analytics",
    "IEC 61850 machine learning",
    "substation automation analytics",
    "protection automation control system",
    "virtualized protection automation control",
    "vPAC substation",
    "real time grid monitoring",
    "data driven grid monitoring",
    "wide area monitoring machine learning",
    "phasor measurement unit machine learning",
    "PMU anomaly detection",
    "power system stability assessment AI",

    # Energy data standards, semantics, ontology, ingestion
    "energy ontology machine learning",
    "semantic energy framework",
    "energy data model",
    "power systems data model",
    "utility customer data analytics",
    "utility data access",
    "energy data ingestion",
    "real time energy data ingestion",
    "process data energy analytics",
    "grid emissions data",
    "carbon emissions energy data",
    "scope 3 emissions data analytics",
    "utility rate data",
    "utility tariff data machine learning",

    # Weather, resilience, risk
    "extreme weather grid machine learning",
    "grid resilience machine learning",
    "grid outage prediction",
    "power outage prediction machine learning",
    "hazard risk analysis energy",
    "extreme event risk model energy",
    "environmental contour model energy",
    "climate risk power grid",
    "wildfire power grid machine learning",
    "storm outage prediction",

    # Microgrids and renewable systems
    "microgrid optimization machine learning",
    "microgrid reinforcement learning",
    "microgrid energy management",
    "renewable energy systems AI",
    "intelligent energy systems",
    "modular energy systems",
    "solar battery optimization",
    "wind power forecasting deep learning",
    "solar power forecasting deep learning",
    "renewable integration smart grid",
]


ENERGY_TERMS = [
    "energy",
    "electricity",
    "electric",
    "power",
    "grid",
    "smart grid",
    "load",
    "demand response",
    "hvac",
    "building energy",
    "solar",
    "wind",
    "renewable",
    "battery",
    "ev charging",
    "electric vehicle",
    "smart meter",
    "metering",
    "nilm",
    "non intrusive load",
    "non-intrusive load",
    "appliance disaggregation",
    "microgrid",
    "power system",
    "power systems",
    "optimal power flow",
    "opf",
    "electricity price",
    "energy price",
    "photovoltaic",
    "pv",

    # LF Energy-inspired terms
    "der",
    "distributed energy resource",
    "distributed energy resources",
    "derms",
    "openadr",
    "ieee 2030.5",
    "ocpp",
    "evse",
    "v2g",
    "bess",
    "substation",
    "digital substation",
    "iec 61850",
    "pmu",
    "phasor",
    "wide area monitoring",
    "grid edge",
    "gridlab-d",
    "gridlab d",
    "power flow",
    "load flow",
    "dynamic line rating",
    "transmission facility rating",
    "utility tariff",
    "utility rate",
    "grid emissions",
    "scope 3 emissions",
    "energy flexibility",
    "energy ontology",
    "energy data model",
    "virtual power plant",
    "vpp",
    "transactive energy",
    "distribution grid",
    "transmission grid",
    "power grid",
    "dso",
    "tso",
]


AI_ML_TERMS = [
    "ai",
    "artificial intelligence",
    "ml",
    "machine learning",
    "deep learning",
    "neural",
    "neural network",
    "forecast",
    "forecasting",
    "prediction",
    "predictive",
    "time series",
    "transformer",
    "lstm",
    "rnn",
    "gru",
    "xgboost",
    "catboost",
    "lightgbm",
    "reinforcement learning",
    "rl",
    "optimization",
    "bayesian",
    "anomaly detection",
    "classification",
    "regression",

    # LF Energy-inspired ML-ish terms
    "decision support",
    "smart assistant",
    "foundation model",
    "foundation models",
    "synthetic data",
    "counterfactual",
    "digital twin",
    "data driven",
    "data-driven",
    "analytics",
    "stability assessment",
    "risk analysis",
    "extreme value model",
    "anomaly",
    "self-correcting",
    "explainable",
    "inference",
    "agent",
    "llm",
    "large language model",
    "graph neural network",
    "gnn",
]


DATASET_TERMS = [
    "dataset",
    "benchmark",
    "data",
    "time series dataset",
    "smart meter dataset",
    "electricity dataset",
    "load dataset",
    "synthetic data",
]


CATEGORY_RULES = [
    (
        "NILM / smart meters",
        [
            "nilm",
            "non intrusive",
            "non-intrusive",
            "smart meter",
            "appliance disaggregation",
            "metering",
        ],
    ),
    (
        "Load / demand forecasting",
        [
            "load forecasting",
            "demand forecasting",
            "energy demand",
            "electricity demand",
            "load forecast",
            "openstef",
        ],
    ),
    (
        "Electricity price forecasting",
        [
            "price forecasting",
            "electricity price",
            "energy price",
        ],
    ),
    (
        "Solar / wind / renewables",
        [
            "solar",
            "wind",
            "renewable",
            "photovoltaic",
            " pv ",
        ],
    ),
    (
        "Grid / power systems",
        [
            "smart grid",
            "power grid",
            "power system",
            "power systems",
            "optimal power flow",
            "opf",
            "microgrid",
            "grid2op",
            "powsybl",
            "dynawo",
            "gridlab",
        ],
    ),
    (
        "Building energy / HVAC",
        [
            "building energy",
            "hvac",
            "thermal comfort",
            "opendsm",
            "openeemeter",
        ],
    ),
    (
        "Battery / EV charging",
        [
            "battery",
            "bess",
            "ev charging",
            "electric vehicle",
            "charging optimization",
            "ocpp",
            "v2g",
            "citrineos",
            "everest",
        ],
    ),
    (
        "Demand response / flexibility",
        [
            "demand response",
            "openadr",
            "energy flexibility",
            "flexibility forecasting",
            "flexmeasures",
        ],
    ),
    (
        "Grid edge / substations",
        [
            "substation",
            "iec 61850",
            "grid edge",
            "pmu",
            "phasor",
            "digital substation",
            "compas",
        ],
    ),
    (
        "Energy datasets / benchmarks",
        [
            "dataset",
            "benchmark",
            "synthetic data",
            "opensynth",
        ],
    ),
    (
        "Energy data / ontology / ingestion",
        [
            "ontology",
            "semantic energy",
            "data ingestion",
            "energy data model",
            "rtdip",
            "fidopower",
        ],
    ),
    (
        "Grid resilience / weather risk",
        [
            "extreme weather",
            "outage prediction",
            "grid resilience",
            "wildfire",
            "storm outage",
            "gridvantage",
            "covxtreme",
        ],
    ),
    (
        "Energy management / optimization",
        [
            "energy management",
            "optimization",
            "rtc-tools",
        ],
    ),
]


@dataclass
class RepoResult:
    full_name: str
    html_url: str
    stars: int
    description: str
    topics: list[str]
    bucket: str
    category: str
    relevance: str
    is_500_plus: bool


def normalize_text(value: str | None) -> str:
    if not value:
        return ""

    value = value.lower()
    value = re.sub(r"[_\-/.]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def term_in_text(term: str, text: str) -> bool:
    term = normalize_text(term)

    if term in {"ai", "ml", "rl", "pv", "ev", "der", "vpp", "v2g", "bess", "pmu", "gnn"}:
        return re.search(rf"(^|[^a-z0-9]){re.escape(term)}([^a-z0-9]|$)", text) is not None

    return term in text


def has_any_term(terms: list[str], text: str) -> bool:
    return any(term_in_text(term, text) for term in terms)


def classify_category(text: str) -> str:
    padded_text = f" {text} "
    for category, terms in CATEGORY_RULES:
        if has_any_term(terms, padded_text):
            return category
    return "General AI/ML + energy"


def classify_relevance(metadata_text: str, readme_text: str = "") -> tuple[str, str]:
    """
    Returns:
      - Direct
      - Dataset
      - Weak
      - Reject
    """
    metadata_text_norm = normalize_text(metadata_text)
    combined_text = normalize_text(metadata_text + " " + readme_text)

    has_energy = has_any_term(ENERGY_TERMS, combined_text)
    has_ai_ml = has_any_term(AI_ML_TERMS, combined_text)
    has_dataset = has_any_term(DATASET_TERMS, combined_text)

    metadata_has_energy = has_any_term(ENERGY_TERMS, metadata_text_norm)
    metadata_has_ai_ml = has_any_term(AI_ML_TERMS, metadata_text_norm)
    metadata_has_dataset = has_any_term(DATASET_TERMS, metadata_text_norm)

    if not has_energy:
        return "Reject", combined_text

    if has_dataset and has_energy:
        if metadata_has_dataset or metadata_has_energy:
            return "Dataset", combined_text

    if metadata_has_energy and metadata_has_ai_ml:
        return "Direct", combined_text

    if has_energy and has_ai_ml:
        return "Weak", combined_text

    return "Reject", combined_text


def github_headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "energy-ai-ml-repo-finder",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def request_json(
    url: str,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
    retries: int = 3,
) -> Any:
    for attempt in range(retries + 1):
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining")
            reset = response.headers.get("X-RateLimit-Reset")

            if remaining == "0" and reset:
                wait_seconds = max(1, int(reset) - int(time.time()) + 2)
                print(f"Rate limit hit. Sleeping for {wait_seconds}s...", file=sys.stderr)
                time.sleep(wait_seconds)
                continue

        if response.status_code in {502, 503, 504} and attempt < retries:
            wait_seconds = 5 * (attempt + 1)
            print(
                f"GitHub temporary error {response.status_code}. "
                f"Retrying in {wait_seconds}s...",
                file=sys.stderr,
            )
            time.sleep(wait_seconds)
            continue

        response.raise_for_status()
        return response.json()

    raise RuntimeError("Failed request after retries")


def search_repositories(
    bucket: str,
    min_stars: int,
    max_pages: int,
    headers: dict[str, str],
    sleep_seconds: float,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    # GitHub repository search supports in:name,description,readme.
    query = f"{bucket} in:name,description,readme stars:>={min_stars} archived:false"

    for page in range(1, max_pages + 1):
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page,
        }

        data = request_json(
            f"{GITHUB_API}/search/repositories",
            headers=headers,
            params=params,
        )

        items = data.get("items", [])
        if not items:
            break

        results.extend(items)

        print(
            f'Bucket "{bucket}" page {page}: {len(items)} repos',
            file=sys.stderr,
        )

        time.sleep(sleep_seconds)

        if len(items) < 100:
            break

    return results


def fetch_readme_text(owner: str, repo: str, headers: dict[str, str]) -> str:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"

    try:
        data = request_json(url, headers=headers)
    except requests.HTTPError:
        return ""

    content = data.get("content", "")
    encoding = data.get("encoding", "")

    if encoding != "base64" or not content:
        return ""

    try:
        decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
    except Exception:
        return ""

    return decoded[:30_000]


def collect_repos(
    min_stars: int,
    limit: int,
    max_pages_per_bucket: int,
    include_weak: bool,
    deep_readme: bool,
    sleep_seconds: float,
) -> list[RepoResult]:
    token = os.getenv("GITHUB_TOKEN")
    headers = github_headers(token)

    if not token:
        print(
            "Warning: GITHUB_TOKEN is not set. "
            "GitHub API rate limits will be much lower.",
            file=sys.stderr,
        )

    raw_by_full_name: dict[str, dict[str, Any]] = {}
    bucket_by_full_name: dict[str, str] = {}

    for bucket in SEARCH_BUCKETS:
        try:
            items = search_repositories(
                bucket=bucket,
                min_stars=min_stars,
                max_pages=max_pages_per_bucket,
                headers=headers,
                sleep_seconds=sleep_seconds,
            )
        except requests.HTTPError as exc:
            print(f'Failed bucket "{bucket}": {exc}', file=sys.stderr)
            continue

        for item in items:
            full_name = item["full_name"]
            existing = raw_by_full_name.get(full_name)

            if existing is None:
                raw_by_full_name[full_name] = item
                bucket_by_full_name[full_name] = bucket
            else:
                existing_stars = existing.get("stargazers_count", 0)
                item_stars = item.get("stargazers_count", 0)
                if item_stars > existing_stars:
                    raw_by_full_name[full_name] = item
                    bucket_by_full_name[full_name] = bucket

        print(f"Unique candidates so far: {len(raw_by_full_name)}", file=sys.stderr)

    filtered: list[RepoResult] = []

    candidates = sorted(
        raw_by_full_name.values(),
        key=lambda repo: repo.get("stargazers_count", 0),
        reverse=True,
    )

    readme_cache: dict[str, str] = {}

    for item in candidates:
        full_name = item["full_name"]
        owner, repo_name = full_name.split("/", 1)

        topics = item.get("topics") or []
        description = item.get("description") or ""

        metadata_text = " ".join(
            [
                full_name,
                description,
                " ".join(topics),
                bucket_by_full_name.get(full_name, ""),
                item.get("language") or "",
            ]
        )

        relevance, evidence_text = classify_relevance(metadata_text)

        if deep_readme and relevance in {"Reject", "Weak"}:
            if full_name not in readme_cache:
                readme_cache[full_name] = fetch_readme_text(owner, repo_name, headers)
                time.sleep(sleep_seconds)

            relevance, evidence_text = classify_relevance(
                metadata_text,
                readme_cache[full_name],
            )

        if relevance == "Reject":
            continue

        if relevance == "Weak" and not include_weak:
            continue

        category = classify_category(evidence_text)

        filtered.append(
            RepoResult(
                full_name=full_name,
                html_url=item["html_url"],
                stars=int(item.get("stargazers_count", 0)),
                description=description.replace("\n", " ").strip(),
                topics=topics,
                bucket=bucket_by_full_name.get(full_name, ""),
                category=category,
                relevance=relevance,
                is_500_plus=int(item.get("stargazers_count", 0)) >= 500,
            )
        )

        if len(filtered) >= limit:
            break

    return filtered


def stars_fmt(stars: int) -> str:
    return f"{stars:,}"


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def write_markdown(
    repos: list[RepoResult],
    output_path: str,
    simple: bool = False,
) -> None:
    if simple:
        lines = [
            "| # | Title | URL | Stars |",
            "|---:|---|---|---:|",
        ]

        for i, repo in enumerate(repos, start=1):
            lines.append(
                f"| {i} | {markdown_escape(repo.full_name)} | "
                f"{repo.html_url} | {stars_fmt(repo.stars)} |"
            )
    else:
        lines = [
            "| # | Title | URL | Stars | >=500 | Category | Relevance | Search Bucket |",
            "|---:|---|---|---:|:---:|---|---|---|",
        ]

        for i, repo in enumerate(repos, start=1):
            yes_no = "Yes" if repo.is_500_plus else "No"
            lines.append(
                f"| {i} | {markdown_escape(repo.full_name)} | "
                f"{repo.html_url} | {stars_fmt(repo.stars)} | "
                f"{yes_no} | {markdown_escape(repo.category)} | "
                f"{repo.relevance} | {markdown_escape(repo.bucket)} |"
            )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_csv(repos: list[RepoResult], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "rank",
                "title",
                "url",
                "stars",
                "is_500_plus",
                "category",
                "relevance",
                "bucket",
                "description",
                "topics",
            ],
        )
        writer.writeheader()

        for i, repo in enumerate(repos, start=1):
            writer.writerow(
                {
                    "rank": i,
                    "title": repo.full_name,
                    "url": repo.html_url,
                    "stars": repo.stars,
                    "is_500_plus": repo.is_500_plus,
                    "category": repo.category,
                    "relevance": repo.relevance,
                    "bucket": repo.bucket,
                    "description": repo.description,
                    "topics": ",".join(repo.topics),
                }
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find GitHub repos related to AI/ML + energy."
    )

    parser.add_argument("--min-stars", type=int, default=100)
    parser.add_argument("--limit", type=int, default=250)
    parser.add_argument("--max-pages-per-bucket", type=int, default=3)

    parser.add_argument("--output", default="energy_ai_ml_repos.md")
    parser.add_argument("--csv-output", default="energy_ai_ml_repos.csv")

    parser.add_argument(
        "--sleep",
        type=float,
        default=2.2,
        help="Sleep between GitHub API calls. Increase if rate-limited.",
    )

    parser.add_argument(
        "--include-weak",
        action="store_true",
        help="Include repos where energy relevance is weaker or only appears in README/examples.",
    )

    parser.add_argument(
        "--deep-readme",
        action="store_true",
        help="Fetch README for ambiguous repos. Improves filtering but uses more API calls.",
    )

    parser.add_argument(
        "--simple-markdown",
        action="store_true",
        help="Use only the original four output columns: #, Title, URL, Stars.",
    )

    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Only write Markdown output.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    repos = collect_repos(
        min_stars=args.min_stars,
        limit=args.limit,
        max_pages_per_bucket=args.max_pages_per_bucket,
        include_weak=args.include_weak,
        deep_readme=args.deep_readme,
        sleep_seconds=args.sleep,
    )

    write_markdown(
        repos=repos,
        output_path=args.output,
        simple=args.simple_markdown,
    )

    if not args.no_csv:
        write_csv(repos, args.csv_output)

    over_500 = sum(1 for repo in repos if repo.is_500_plus)

    print()
    print(f"Found {len(repos)} repos.")
    print(f"Repos with >=500 stars: {over_500}")
    print(f"Markdown written to: {args.output}")

    if not args.no_csv:
        print(f"CSV written to: {args.csv_output}")

    if len(repos) < args.limit:
        print()
        print("Warning: fewer repos found than requested.")
        print("Try:")
        print("  python github_energy_ai_ml_repos.py --min-stars 50 --limit 250 --deep-readme --include-weak")
        print("  python github_energy_ai_ml_repos.py --min-stars 25 --limit 250 --deep-readme --include-weak")
        print("  python github_energy_ai_ml_repos.py --max-pages-per-bucket 10 --deep-readme --include-weak")


if __name__ == "__main__":
    main()
