
import json
import sys
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, unquote

REPORT = "security-reports/dast-report.json"

with open(REPORT, encoding="utf-8") as f:
    report = json.load(f)

allowed = {
    ("10049", "Non-Storable Content"),
    ("10049", "Storable and Cacheable Content"),
    ("10055", "CSP: script-src unsafe-eval"),
    ("10055", "CSP: style-src unsafe-inline"),
    ("10109", "Modern Web Application"),
    ("10111", "Authentication Request Identified"),
    ("10112", "Session Management Response Identified"),
    ("90004", "Cross-Origin-Embedder-Policy Header Missing or Invalid"),
}

public_extensions = {
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
}

manual_review = {
    ("10055", "CSP: script-src unsafe-eval"),
    ("10055", "CSP: style-src unsafe-inline"),
    ("90004", "Cross-Origin-Embedder-Policy Header Missing or Invalid"),
}

tracked_files = set(
    subprocess.check_output(
        ["git", "ls-files", "-z", "--", "project4/static/"]
    ).decode("utf-8").split("\0")
)

static_root = Path("project4/static").resolve()


def is_public_static(url, method, risk):
    parsed = urlsplit(url)
    path = unquote(parsed.path)

    if (
        parsed.scheme != "http"
        or parsed.netloc != "127.0.0.1:8001"
        or not path.startswith("/static/")
        or parsed.query
        or parsed.fragment
        or method not in {"GET", "HEAD"}
        or risk != 0
    ):
        return False

    relative = path.removeprefix("/static/")

    if (
        not relative
        or "\\" in relative
        or any(
            part in {"", ".", ".."}
            or part.startswith(".")
            for part in relative.split("/")
        )
    ):
        return False

    asset = static_root / relative
    tracked_path = "project4/static/" + relative

    return (
        asset.suffix.lower() in public_extensions
        and tracked_path in tracked_files
        and asset.is_file()
        and asset.resolve().is_relative_to(static_root)
        and not asset.is_symlink()
    )


sites = report.get("site", [])

if not sites:
    sys.exit("Invalid or empty ZAP report")

unexpected = []
review_required = []

for site in sites:
    for alert in site.get("alerts", []):
        rule = str(alert.get("pluginid", ""))
        name = alert.get("alert", "")
        risk = int(alert["riskcode"])
        finding = (rule, name)

        if finding not in allowed or risk > 2:
            unexpected.append(f"{rule}: {name}")
            continue

        if finding == (
            "10049",
            "Storable and Cacheable Content"
        ):
            instances = alert.get("instances", [])

            if not instances:
                unexpected.append(
                    "Cacheable content has no URL evidence"
                )
                continue

            for instance in instances:
                url = instance.get("uri", "")
                method = instance.get("method", "")

                if is_public_static(url, method, risk):
                    print(
                        "APPROVED PUBLIC STATIC:",
                        urlsplit(url).path
                    )
                else:
                    unexpected.append(
                        f"Unapproved cacheable content: {url}"
                    )

        elif finding in manual_review:
            review_required.append(f"{rule}: {name}")

            for instance in alert.get("instances", []):
                print("REVIEW URL:", instance.get("uri"))

        elif risk != 0:
            unexpected.append(
                f"Unexpected risk level: {rule}: {name}"
            )

        else:
            print(
                f"ACCEPTED INFORMATIONAL: {rule}: {name}"
            )

if unexpected:
    for finding in unexpected:
        print("UNAPPROVED:", finding)

    sys.exit(1)

if review_required:
    for finding in sorted(set(review_required)):
        print("REVIEW REQUIRED:", finding)

    sys.exit(2)

print("ZAP security policy validation passed")
sys.exit(0)
