
import json
import sys
from urllib.parse import urlsplit

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

public_css = {
    "/static/css/animated.css",
    "/static/css/fontawesome.css",
    "/static/css/owl.css",
    "/static/css/templatemo-space-dynamic.css",
    "/static/fonts/poppins/poppins.css",
}

manual_review = {
    ("10055", "CSP: script-src unsafe-eval"),
    ("10055", "CSP: style-src unsafe-inline"),
    ("90004", "Cross-Origin-Embedder-Policy Header Missing or Invalid"),
}

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

        if finding == ("10049", "Storable and Cacheable Content"):
            instances = alert.get("instances", [])

            if not instances:
                unexpected.append("Cacheable content has no URL evidence")
                continue

            for instance in instances:
                url = instance.get("uri", "")
                method = instance.get("method", "")
                parsed = urlsplit(url)

                if (
                    parsed.scheme != "http"
                    or parsed.netloc != "127.0.0.1:8001"
                    or parsed.path not in public_css
                    or parsed.query
                    or method != "GET"
                    or risk != 0
                ):
                    unexpected.append(
                        f"Unapproved cacheable content: {url}"
                    )
                else:
                    print(f"APPROVED PUBLIC CSS: {parsed.path}")

        elif finding in manual_review:
            review_required.append(f"{rule}: {name}")

            for instance in alert.get("instances", []):
                print("REVIEW URL:", instance.get("uri"))

        elif risk != 0:
            unexpected.append(
                f"Unexpected risk level: {rule}: {name}"
            )

        else:
            print(f"ACCEPTED INFORMATIONAL: {rule}: {name}")

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
