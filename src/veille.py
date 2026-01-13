import feedparser
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

RSS_FEEDS = [
    "https://www.zdnet.fr/feeds/rss/actualites/",
    "https://www.lemondeinformatique.fr/flux-rss/thematique/toutes-les-actualites/rss.xml",
    "https://techcrunch.com/feed/",
]

KEYWORDS = [
    "cybersécurité", "ransomware", "zero trust", "cloud", "aws", "azure", "gcp",
    "ia", "intelligence artificielle", "llm", "openai", "mistral",
    "devops", "kubernetes", "docker",
    "linux", "windows", "android",
]

OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)

def match_keywords(text: str) -> bool:
    t = (text or "").lower()
    return any(k.lower() in t for k in KEYWORDS)

def main():
    rows = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries:
            title = e.get("title", "")
            summary = e.get("summary", "")
            link = e.get("link", "")
            published = e.get("published", "") or e.get("updated", "")
            if match_keywords(title + " " + summary):
                rows.append({
                    "published": published,
                    "title": title,
                    "link": link,
                    "source": feed.feed.get("title", url),
                })

    df = pd.DataFrame(rows).drop_duplicates(subset=["title", "link"])

    # Date (UTC) pour nommer le fichier (simple et fiable côté GitHub Actions)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    csv_path = OUT_DIR / f"veille_{today}.csv"
    md_path = OUT_DIR / f"veille_{today}.md"

    df.to_csv(csv_path, index=False)

    # Petit rendu Markdown propre pour ton BTS
    lines = [
        f"# Veille techno — {today}",
        "",
        f"**Mots-clés :** {', '.join(KEYWORDS)}",
        "",
        f"**Articles retenus :** {len(df)}",
        "",
        "## Liens",
        "",
    ]
    for _, r in df.head(50).iterrows():  # limite pour éviter des fichiers énormes
        lines.append(f"- [{r['title']}]({r['link']}) — *{r['source']}*")
    lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"OK → {csv_path} et {md_path}")

if __name__ == "__main__":
    main()
