#!/usr/bin/env python3

# 100 websites across 10 categories of 10 each
# Then pair 4 out of 5 in each category, leaving 1 leftover per category
# Alternate which category gets 6 vs 4

websites = {
    "LLM_Chat": [
        "ChatGPT",
        "Claude",
        "Gemini",
        "Perplexity",
        "Grok",
        "Kimi",
        "DeepSeek",
        "Qwen",
        "Llama",
        "Mistral",
    ],
    "Code_Hosting": [
        "GitHub",
        "GitLab",
        "Bitbucket",
        "SourceForge",
        "Codeberg",
        "Gitea",
        "Gogs",
        "Launchpad",
        "Phabricator",
        "Gerrit",
    ],
    "Cloud_Providers": [
        "AWS",
        "Azure",
        "GCP",
        "DigitalOcean",
        "Linode",
        "Vultr",
        "Hetzner",
        "Oracle Cloud",
        "IBM Cloud",
        "Scaleway",
    ],
    "Search_Engines": [
        "Google",
        "Bing",
        "DuckDuckGo",
        "Brave Search",
        "Kagi",
        "You.com",
        "SearXNG",
        "Startpage",
        "Qwant",
        "Mojeek",
    ],
    "Social_Media": [
        "Twitter/X",
        "Mastodon",
        "Bluesky",
        "Threads",
        "LinkedIn",
        "Reddit",
        "Discord",
        "Telegram",
        "Signal",
        "Matrix",
    ],
    "Video_Platforms": [
        "YouTube",
        "Vimeo",
        "PeerTube",
        "Rumble",
        "Odysee",
        "Dailymotion",
        "Twitch",
        "Kick",
        "TikTok",
        "Instagram Reels",
    ],
    "Package_Managers": [
        "npm",
        "pip",
        "cargo",
        "go mod",
        "maven",
        "gradle",
        "nuget",
        "composer",
        "pub",
        "hex",
    ],
    "CI_CD": [
        "GitHub Actions",
        "GitLab CI",
        "CircleCI",
        "Travis CI",
        "Jenkins",
        "Buildkite",
        "Drone",
        "Woodpecker",
        "Tekton",
        "Argo CD",
    ],
    "Databases": [
        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Redis",
        "SQLite",
        "MariaDB",
        "Cassandra",
        "DynamoDB",
        "CockroachDB",
        "TimescaleDB",
    ],
    "Observability": [
        "Datadog",
        "New Relic",
        "Grafana",
        "Prometheus",
        "Honeycomb",
        "Splunk",
        "Elastic",
        "Jaeger",
        "Zipkin",
        "SigNoz",
    ],
}

# Pairings - 4 out of 5 get pairs, 1 leftover
# Alternate: categories 0,2,4,6,8 get 6 (3 pairs), categories 1,3,5,7,9 get 4 (2 pairs)

pairings = {
    "LLM_Chat": {
        "pairs": [("ChatGPT", "Claude"), ("Gemini", "Grok"), ("Kimi", "DeepSeek")],
        "leftover": "Perplexity",
        "unselected": ["Qwen", "Llama", "Mistral"],
    },
    "Code_Hosting": {
        "pairs": [("GitHub", "GitLab"), ("Bitbucket", "Codeberg")],
        "leftover": "SourceForge",
        "unselected": ["Gitea", "Gogs", "Launchpad", "Phabricator", "Gerrit"],
    },
    "Cloud_Providers": {
        "pairs": [("AWS", "Azure"), ("GCP", "DigitalOcean"), ("Linode", "Vultr")],
        "leftover": "Hetzner",
        "unselected": ["Oracle Cloud", "IBM Cloud", "Scaleway"],
    },
    "Search_Engines": {
        "pairs": [("Google", "Bing"), ("DuckDuckGo", "Brave Search")],
        "leftover": "Kagi",
        "unselected": ["You.com", "SearXNG", "Startpage", "Qwant", "Mojeek"],
    },
    "Social_Media": {
        "pairs": [
            ("Twitter/X", "Bluesky"),
            ("Mastodon", "Threads"),
            ("Reddit", "Discord"),
        ],
        "leftover": "LinkedIn",
        "unselected": ["Telegram", "Signal", "Matrix"],
    },
    "Video_Platforms": {
        "pairs": [("YouTube", "Vimeo"), ("PeerTube", "Rumble")],
        "leftover": "Odysee",
        "unselected": ["Dailymotion", "Twitch", "Kick", "TikTok", "Instagram Reels"],
    },
    "Package_Managers": {
        "pairs": [("npm", "pip"), ("cargo", "go mod"), ("maven", "gradle")],
        "leftover": "nuget",
        "unselected": ["composer", "pub", "hex"],
    },
    "CI_CD": {
        "pairs": [("GitHub Actions", "GitLab CI"), ("CircleCI", "Travis CI")],
        "leftover": "Jenkins",
        "unselected": ["Buildkite", "Drone", "Woodpecker", "Tekton", "Argo CD"],
    },
    "Databases": {
        "pairs": [
            ("PostgreSQL", "MySQL"),
            ("MongoDB", "Redis"),
            ("MariaDB", "Cassandra"),
        ],
        "leftover": "SQLite",
        "unselected": ["DynamoDB", "CockroachDB", "TimescaleDB"],
    },
    "Observability": {
        "pairs": [("Datadog", "New Relic"), ("Grafana", "Prometheus")],
        "leftover": "Honeycomb",
        "unselected": ["Splunk", "Elastic", "Jaeger", "Zipkin", "SigNoz"],
    },
}

print("=" * 80)
print("100 WEBSITES -> 10 CATEGORIES -> PAIR ANALYSIS")
print("=" * 80)

for cat, data in pairings.items():
    pair_count = len(data["pairs"])
    print(f"\n{cat} ({pair_count} pairs = {pair_count * 2} items paired, 1 leftover)")
    print("-" * 60)
    for a, b in data["pairs"]:
        print(f"  {a} <-> {b}")
    print(f"  LEFTOVER: {data['leftover']}")
    print(f"  Unselected (5): {', '.join(data['unselected'])}")

# Summary
six_pair_cats = [c for c, d in pairings.items() if len(d["pairs"]) == 3]
four_pair_cats = [c for c, d in pairings.items() if len(d["pairs"]) == 2]

print("\n" + "=" * 80)
print("SUMMARY: Alternating 6 vs 4 paired items per category")
print("=" * 80)
print(f"Categories with 6 paired (3 pairs): {', '.join(six_pair_cats)}")
print(f"Categories with 4 paired (2 pairs): {', '.join(four_pair_cats)}")
