from .reporter import generate_report
from .audit import log_governance_event, get_audit_log, get_stats


def main():
    print("\n=== AI Governance Dashboard ===")
    print("Screen text for compliance, bias, PII and policy violations.")
    print("Commands: 'history', 'stats', 'exit'\n")

    while True:
        text = input(">> ").strip()

        if not text:
            continue

        if text.lower() == "exit":
            print("Goodbye.")
            break

        if text.lower() == "history":
            records = get_audit_log(limit=5)
            if not records:
                print("No audit history yet.\n")
            else:
                for r in records:
                    flag = "🚨" if r["overall_flagged"] else "✅"
                    print(f"{flag} [{r['timestamp']}] {r['overall_severity']} | {r['text']}")
            print()
            continue

        if text.lower() == "stats":
            s = get_stats()
            print(f"\nTotal events:   {s['total_events']}")
            print(f"Total flagged:  {s['total_flagged']}")
            print(f"Avg risk score: {s['avg_risk_score']}")
            print(f"Critical:       {s['critical_count']}")
            print(f"High:           {s['high_count']}")
            print(f"Low:            {s['low_count']}\n")
            continue

        print("\nRunning governance checks...")
        result = generate_report(text, context="input")
        log_governance_event(result)

        flag = "🚨 FLAGGED" if result["overall_flagged"] else "✅ CLEARED"
        print(f"\nStatus: {flag}")
        print(f"Severity: {result['overall_severity']} | Risk Score: {result['overall_risk_score']}")

        if result["findings"]:
            print("\nFindings:")
            for f in result["findings"]:
                print(f"  [{f['nist_function']} {f['nist_category']}] {f['severity']} — {f['detail']}")

        print(f"\nGOVERNANCE REPORT:\n{result['report']}\n")


if __name__ == "__main__":
    main()