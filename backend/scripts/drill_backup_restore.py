"""
Phase 17: Empirical Backup & Restore Drill Runner.
Measures restore latency, verifies SHA-256 data integrity, and checks offline compliance.
"""
import sys
import os
import json
import time

# Ensure backend path is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.engine.resilience_harness import ResilienceHarness


def main():
    print("=" * 70)
    print(" SAMARATH: Phase 17 Backup & Restore Drill")
    print("=" * 70)

    report = ResilienceHarness.execute_backup_restore_drill()

    print(f"Drill Identifier       : {report.drill_id}")
    print(f"Executed At (UTC)      : {report.executed_at_utc.isoformat()}")
    print(f"Records Processed      : {report.records_backed_up}")
    print(f"Backup Duration        : {report.backup_duration_ms:.2f} ms")
    print(f"Restore Duration       : {report.restore_duration_ms:.2f} ms")
    print(f"RPO (Data Loss Target) : {report.rpo_seconds:.1f} s")
    print(f"RTO (Recovery Time)    : {report.rto_seconds:.4f} s")
    print(f"Integrity Hash Matched : {report.integrity_hash_matched}")
    print(f"Offline Self-Contained : {report.offline_verified}")
    print(f"Status                 : {report.status}")
    print("=" * 70)
    assert report.integrity_hash_matched, "Integrity verification failed!"
    print("RESULT: DRILL COMPLETED WITH ZERO DATA LOSS.")


if __name__ == "__main__":
    main()
