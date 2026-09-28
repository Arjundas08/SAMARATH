"""
Phase 17: Reproducible Scaling Benchmarks Runner.
Executes workloads at 10, 30, and 100 tasks (and 300 exploratory).
Reports P50, P95, stage latencies, memory, and budget compliance.
"""
import sys
import os
import json
import time

# Ensure backend path is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.engine.benchmark_harness import BenchmarkHarness


def main():
    print("=" * 80)
    print(" SAMARATH: Phase 17 Scaling Benchmarks & Latency Profiling")
    print("=" * 80)

    summaries = BenchmarkHarness.generate_full_benchmark_suite()

    print(f"{'Tasks':<8} | {'P50 (ms)':<10} | {'P95 (ms)':<10} | {'Solve (ms)':<10} | {'Check (ms)':<10} | {'Mem (MB)':<8} | {'Budget':<10} | {'Status':<16}")
    print("-" * 88)

    for s in summaries:
        b_target = f"{s.budget_target_ms/1000.0:.0f}s"
        b_status = "PASS" if s.budget_compliant else "OVER_BUDGET"
        print(f"{s.workload_tasks:<8} | {s.p50_total_ms:<10.1f} | {s.p95_total_ms:<10.1f} | {s.mean_solve_ms:<10.1f} | {s.mean_checker_ms:<10.1f} | {s.mean_peak_memory_mb:<8.1f} | {b_target:<10} | {b_status:<16}")

    print("=" * 80)
    print("BENCHMARK REPORT GENERATION COMPLETE.")


if __name__ == "__main__":
    main()
