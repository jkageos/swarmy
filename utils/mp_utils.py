import multiprocessing as mp
import os
import sys
import time


def apply_mp_safety_env(blas_threads: str = "1") -> None:
    """
    Apply parent-process env settings for safe multiprocessing runs.
    Ensures child workers inherit limits (esp. BLAS thread caps).
    """
    os.environ.setdefault("OMP_NUM_THREADS", blas_threads)
    os.environ.setdefault("MKL_NUM_THREADS", blas_threads)
    os.environ.setdefault("OPENBLAS_NUM_THREADS", blas_threads)
    os.environ.setdefault("NUMEXPR_NUM_THREADS", blas_threads)


def set_low_priority() -> None:
    """
    Best-effort: lower process priority to reduce CPU pressure/heat.
    - Windows: BELOW_NORMAL
    - POSIX: niceness +10 (or setpriority)
    Safe to use as Pool.initializer.
    """
    try:
        pid = os.getpid()

        # Prefer psutil on all platforms
        try:
            import psutil  # optional

            p = psutil.Process(pid)
            if sys.platform.startswith("win"):
                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            else:
                p.nice(10)
            return
        except Exception:
            pass

        if sys.platform.startswith("win"):
            # Win32 fallback
            try:
                import ctypes

                BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
                ctypes.windll.kernel32.SetPriorityClass(
                    ctypes.windll.kernel32.GetCurrentProcess(),
                    BELOW_NORMAL_PRIORITY_CLASS,
                )
            except Exception:
                pass
        else:
            # POSIX fallbacks (guard for type checkers/platforms)
            try:
                if hasattr(os, "nice"):
                    os.nice(10)  # type: ignore[attr-defined]
                elif hasattr(os, "setpriority") and hasattr(os, "PRIO_PROCESS"):
                    os.setpriority(os.PRIO_PROCESS, pid, 10)  # type: ignore[attr-defined]
            except Exception:
                pass
    except Exception:
        pass


def safe_worker_count(
    total_jobs: int, max_workers: int | None = None, max_cpu_utilization: float = 0.75
) -> int:
    """
    Compute conservative worker count.
    - Leaves 1 core free by default.
    - Caps by utilization and explicit max_workers.
    """
    cpu = mp.cpu_count() or 1
    util_cap = max(1, int(cpu * max(0.1, min(1.0, float(max_cpu_utilization)))))
    leave_one = max(1, cpu - 1)
    cap = min(util_cap, leave_one)
    if isinstance(max_workers, int) and max_workers > 0:
        cap = min(cap, max_workers)
    return max(1, min(total_jobs, cap))


def run_pool_batches(
    items,
    worker,
    *,
    processes: int,
    maxtasksperchild: int = 10,
    batch_size: int | None = None,
    cooldown_seconds: float = 0.0,
    ctx: str = "spawn",
    initializer=set_low_priority,
    unordered: bool = True,
):
    """
    Run items with a Pool in optional batches and yield results.
    - Uses spawn context for Windows/Linux parity.
    - Recycles workers via maxtasksperchild.
    - Optional cooldowns between batches.
    """
    if batch_size is None or batch_size <= 0:
        batch_size = len(items)

    i = 0
    total = len(items)
    mp_ctx = mp.get_context(ctx)

    while i < total:
        batch = items[i : i + batch_size]
        with mp_ctx.Pool(
            processes=processes,
            maxtasksperchild=maxtasksperchild,
            initializer=initializer,
        ) as pool:
            iterator = (
                pool.imap_unordered(worker, batch)
                if unordered
                else pool.imap(worker, batch)
            )
            for result in iterator:
                yield result
        i += batch_size
        if cooldown_seconds > 0.0 and i < total:
            time.sleep(cooldown_seconds)
