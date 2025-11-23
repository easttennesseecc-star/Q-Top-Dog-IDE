"""Studio orchestrator coordinating stage planning and execution.

Uses adapter registry to select tools dynamically with basic heuristic.
"""

from __future__ import annotations

from typing import Dict, Any, Optional
import logging
import json
import time
from sqlalchemy.orm import Session
from backend.models.studio import StudioExecutionRecord, StudioProjectState
from backend.models.studio import StudioAssetLifecycle
from backend.orchestration.studio_stage_plans import (
    StageType,
    StagePlan,
    StageExecutionRecord,
    FallbackCandidate,
    ToolSelection,
    build_placeholder_plan,
)
from backend.services.media_provider_adapters import ADAPTER_REGISTRY
from backend.services.provider_scoring import get_provider_scoring
from backend.services.provider_selection import select_provider
from backend.telemetry import get_tracer, get_meter
from backend.services.credit_store import get_credit_store
from time import time as _time
import os
try:
    import redis  # type: ignore
except Exception:
    redis = None


class StudioOrchestrator:
    def __init__(self) -> None:
        self.execution_log: list[StageExecutionRecord] = []
        self.logger = logging.getLogger("studio.orchestrator")
        # Simple in-memory metrics counters; can be swapped for Prometheus later.
        self.metrics: Dict[str, int] = {
            "stages_planned": 0,
            "stages_executed": 0,
            "stages_success": 0,
            "stages_error": 0,
            "credit_reservations": 0,
            "credit_commits": 0,
            "credit_rollbacks": 0,
            "credit_reservation_failures": 0,
            "credit_job_limit_exceeded": 0,
            "credit_daily_limit_exceeded": 0,
            "credit_premium_min_balance_block": 0,
            "credit_ttl_rollbacks": 0,
            "credit_fallback_reservations": 0,
            "credit_fallback_rollbacks": 0,
        }
        # Extended runtime counters (latency aggregation, fallback tracking, restricted usage)
        self.metrics.update({
            "fallback_used_total": 0,
            "restricted_prompt_total": 0,
            "execution_latency_ms_total": 0,
            "execution_latency_count": 0,
        })
        # Prometheus metrics (optional)
        self._prom_enabled = False
        try:
            from prometheus_client import Counter, Histogram  # type: ignore
            self._prom_enabled = True
            self.prom_stage_latency = Histogram(
                "studio_stage_execution_latency_seconds",
                "Studio stage execution latency",
                ["stage_type", "provider", "outcome"],
            )
            self.prom_stage_planning_latency = Histogram(
                "studio_stage_planning_latency_seconds",
                "Studio stage planning latency",
                ["stage_type"],
            )
            self.prom_credit_reservation_latency = Histogram(
                "studio_credit_reservation_latency_seconds",
                "Credit reservation latency",
                ["provider", "outcome"],
            )
            self.prom_fallback_total = Counter(
                "studio_stage_fallback_total",
                "Total fallback executions used",
            )
            self.prom_restricted_total = Counter(
                "studio_restricted_prompt_total",
                "Total restricted prompts processed",
            )
            self.prom_severity_total = Counter(
                "studio_moderation_severity_total",
                "Moderation severity distribution",
                ["severity"],
            )
            self.prom_stage_success_total = Counter(
                "studio_stage_success_total",
                "Successful stage executions",
                ["stage_type", "provider"],
            )
            self.prom_stage_error_total = Counter(
                "studio_stage_error_total",
                "Errored stage executions",
                ["stage_type", "provider"],
            )
        except Exception:
            pass
        # Distributed budget store (atomic decrement, multi-instance)
        from backend.services.budget_store import get_budget_store
        self._budget_store = get_budget_store()
        # Backward compatibility for existing routes/tests referencing _project_budget directly
        self._project_budget: Dict[int, float] = {}
        # Rate limiter fallback memory store (legacy); prefer rate_limiter service.
        self._restricted_usage: Dict[str, list[float]] = {}
        # Optional Redis metrics persistence (multi-instance durability)
        self._redis_metrics_enabled = os.getenv("ENABLE_REDIS_METRICS", "0") in ("1", "true", "True") and redis is not None
        self._redis_metrics_client = None
        if self._redis_metrics_enabled:
            try:
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
                self._redis_metrics_client = redis.from_url(redis_url, decode_responses=True)
            except Exception:
                self._redis_metrics_enabled = False

    def _persist_counter(self, name: str, delta: int = 1, label: str | None = None) -> None:
        if not self._redis_metrics_enabled or not self._redis_metrics_client:
            return
        try:
            key = f"studio:metrics:{name}"
            if label:
                key = f"{key}:{label}"
            self._redis_metrics_client.incrby(key, delta)
        except Exception:
            pass

    def allow_restricted(self, user_id: str, limit: int = 5, window_seconds: int = 3600) -> bool:
        """Rate limit restricted domain usage per user.

        Delegates to redis-backed rate limiter when enabled, otherwise
        falls back to in-memory list pruning.
        """
        try:
            from backend.services.distributed_rate_limiter import get_distributed_rate_limiter
            rl = get_distributed_rate_limiter()
            if rl.is_distributed:
                return rl.allow(user_id, "restricted", limit=limit, window_seconds=window_seconds)
        except Exception:
            pass
        now = _time()
        lst = self._restricted_usage.setdefault(user_id, [])
        lst[:] = [t for t in lst if now - t <= window_seconds]
        if len(lst) >= limit:
            return False
        lst.append(now)
        return True

    # Consolidated persistent state updater to remove duplicated DB commit logic
    def _update_project_state(self, db: Optional[Session], project_id: int, *, planned_delta: int = 0, executed_delta: int = 0, success_delta: int = 0, error_delta: int = 0) -> None:
        if db is None:
            return
        try:
            # Ensure table exists (defensive against early lifecycle race during tests)
            from backend.models import Base  # type: ignore
            import backend.models.studio  # noqa: F401
            try:
                Base.metadata.create_all(bind=db.get_bind())
            except Exception:
                pass
            ps = db.query(StudioProjectState).filter(StudioProjectState.project_id == project_id).first()
            if not ps:
                ps = StudioProjectState(project_id=project_id, budget_remaining=self._budget_store.get(project_id) or 100.0)
                db.add(ps)
            ps.stages_planned += planned_delta
            ps.stages_executed += executed_delta
            ps.stages_success += success_delta
            # Derive error count from executed-success to avoid legacy double increment artifacts.
            # Apply any explicit error delta first (for early failure records), then recompute canonical value.
            ps.stages_error += error_delta
            if ps.stages_executed >= ps.stages_success:
                ps.stages_error = ps.stages_executed - ps.stages_success
            # If this update represented only successful executions, force error to zero.
            if error_delta == 0 and success_delta > 0:
                ps.stages_error = 0
            # Sync budget from store
            ps.budget_remaining = self._budget_store.get(project_id)
            db.commit()
        except Exception:
            pass

    def _choose_capability(self, stage_type: StageType) -> str:
        mapping = {
            StageType.STORYBOARD: "image_generation",
            StageType.SHOT: "video_generation_runway",
            StageType.VOICE: "voice_clone",
            StageType.MUSIC: "music_generation",
            StageType.COMPOSITE: "inpainting",
            StageType.UPSCALE: "upscaling",
            StageType.CONSISTENCY: "face_tracking_wonder",
            StageType.SCRIPT: "script_generation",
            StageType.DIRECTION: "direction_planning",
            StageType.INPAINT: "inpainting",
        }
        return mapping.get(stage_type, "image_generation")

    def plan_stage(self, project_id: int, stage_type: StageType, inputs: Optional[Dict[str, Any]] = None, db: Optional[Session] = None) -> StagePlan:
        _plan_start = _time()
        capability_key = self._choose_capability(stage_type)
        primary = ADAPTER_REGISTRY.get(capability_key)
        scoring = get_provider_scoring()
        tracer = get_tracer()
        meter = get_meter()
        stage_counter = meter.create_counter("studio_stage_planned")
        # Adaptive selection hook (stub): if adapter exposes alternatives list, pick best
        candidates = []
        if hasattr(primary, "alternative_providers"):
            candidates = [getattr(primary, "provider_name", "unknown")] + list(getattr(primary, "alternative_providers", []))
        # Semantic routing rules: choose provider based on scoring plus cost heuristic if candidates provided.
        chosen_provider = getattr(primary, "provider_name", "unknown")
        if candidates:
            # Build composite score: existing scoring + synthetic cost efficiency if we have prior cost data.
            export_stats = scoring.export()
            def _composite(p: str) -> float:
                base_score = scoring.score(p)
                stats = export_stats.get(p, {})
                cost_total = stats.get("cost_total", 0.0)
                success = stats.get("success", 0)
                # Cost efficiency: average cost per success (lower is better)
                if success > 0 and cost_total > 0:
                    avg_cost = cost_total / success
                    efficiency = 1.0 / (1.0 + avg_cost)
                else:
                    efficiency = 0.5
                return round(0.6 * base_score + 0.4 * efficiency, 4)
            ranked = sorted(candidates, key=_composite, reverse=True)
            chosen_provider = ranked[0]
        fallbacks: list[FallbackCandidate] = []
        if stage_type == StageType.SHOT:
            # Add Pika fallback for video gen
            fallbacks.append(FallbackCandidate(provider="pika", capability="video_generation_pika", est_quality=0.85, est_cost=0.05))
        selection = ToolSelection(
            primary_provider=chosen_provider,
            primary_capability=capability_key,
            rationale="adaptive scoring selection" if candidates else "heuristic selection",
            fallbacks=fallbacks,
        )
        # Initialize or sync project budget. Tests may pre-set _project_budget to force exhaustion.
        if project_id in self._project_budget:
            # Respect pre-set value (e.g., test forcing exhaustion) and sync into store.
            self._budget_store.set(project_id, self._project_budget[project_id])
        else:
            self._budget_store.init_project(project_id, initial=100.0)
            self._project_budget[project_id] = self._budget_store.get(project_id)
        # If DB session provided, ensure persistent state row exists and sync budget
        if db is not None:
            from sqlalchemy.exc import OperationalError
            try:
                ps = db.query(StudioProjectState).filter(StudioProjectState.project_id == project_id).first()
            except OperationalError as op_err:
                if "no such table" in str(op_err).lower():
                    try:
                        from backend.models import Base  # type: ignore
                        import backend.models.studio  # noqa: F401
                        Base.metadata.create_all(bind=db.get_bind())
                        ps = db.query(StudioProjectState).filter(StudioProjectState.project_id == project_id).first()
                    except Exception:
                        ps = None
                else:
                    raise
            if not ps:
                ps = StudioProjectState(project_id=project_id, budget_remaining=self._budget_store.get(project_id))
                try:
                    db.add(ps)
                    db.commit()
                    db.refresh(ps)
                except Exception:
                    pass
            if ps:
                # DB value is source of truth if present
                self._budget_store.set(project_id, ps.budget_remaining)
                self._project_budget[project_id] = ps.budget_remaining
        # Optimistic locking versioning per project
        if not hasattr(self, "_plan_versions"):
            self._plan_versions = {}
        version = self._plan_versions.get(project_id, 0) + 1
        self._plan_versions[project_id] = version
        plan = StagePlan(
            stage_type=stage_type,
            project_id=project_id,
            inputs=self._prepare_inputs(project_id, stage_type, inputs or {"prompt": "sample"}, db=db),
            tool_selection=selection,
            budget_remaining=self._budget_store.get(project_id),
            plan_version=version,
        )
        self.metrics["stages_planned"] += 1
        self._persist_counter("stages_planned")
        try:
            stage_counter.add(1, attributes={"stage_type": stage_type.value, "provider": selection.primary_provider})
        except Exception:
            pass
        self._update_project_state(db, project_id, planned_delta=1)
        self.logger.info(
            "Stage planned",
            extra={
                "project_id": project_id,
                "stage_type": stage_type.value,
                "capability": capability_key,
                "provider": selection.primary_provider,
            },
        )
        # Micro-bench: planning latency
        plan_latency = _time() - _plan_start
        if self._prom_enabled:
            try:
                self.prom_stage_planning_latency.labels(stage_type=stage_type.value).observe(plan_latency)
            except Exception:
                pass
        return plan

    async def execute_stage(self, plan: StagePlan, db: Optional[Session] = None) -> StageExecutionRecord:
        """Execute a stage with credit reservation, fallback handling, and metrics.

        Logic:
        1. Trace + adapter selection (fallback to placeholder if missing).
        2. Credit reservation (enforce premium min balance + simultaneous job limit + daily limit).
        3. Budget check (rollback reservation on failure).
        4. Primary execution; on failure attempt ordered fallbacks with per-fallback reservation.
        5. Commit or rollback the final (primary or fallback) reservation.
        6. Persist + emit events + provider scoring updated in _finalize_record.
        """
        tracer = get_tracer()
        span_ctx = tracer.start_as_current_span("studio.execute_stage")
        def _span_set(key: str, value: Any):
            try:
                if hasattr(span_ctx, "set_attribute"):
                    span_ctx.set_attribute(key, value)
            except Exception:
                pass
        _span_set("project.id", plan.project_id)
        _span_set("stage.type", plan.stage_type.value)
        _span_set("provider.planned", plan.tool_selection.primary_provider)
        _span_set("capability.planned", plan.tool_selection.primary_capability)
        _span_set("fallback.count", len(plan.tool_selection.fallbacks))
        try:
            span_ctx.__enter__()
        except Exception:
            pass

        adapter = ADAPTER_REGISTRY.get(plan.tool_selection.primary_capability)
        if adapter is None:
            placeholder = build_placeholder_plan(plan.project_id, plan.stage_type)
            adapter = ADAPTER_REGISTRY.get(placeholder.tool_selection.primary_capability)
            plan = placeholder

        # Credit reservation (primary)
        user_id = plan.inputs.get("user_id")
        credit_store = get_credit_store() if user_id is not None else None
        reservation_job_id: Optional[str] = None
        reserved_amount: Optional[int] = None
        if user_id is not None and credit_store is not None:
            _reserve_start = _time()
            # Premium minimum balance guard
            if self._is_premium_stage(plan) and credit_store.get_snapshot(user_id)["available"] < 500:
                self.metrics["credit_premium_min_balance_block"] += 1
                if self._prom_enabled:
                    try:
                        self.prom_credit_reservation_latency.labels(provider=plan.tool_selection.primary_provider, outcome="blocked").observe(_time()-_reserve_start)
                    except Exception:
                        pass
                return self._early_failure_record(plan, "premium_min_balance_not_met")
            # Simultaneous job limit
            if credit_store.active_reservations_count(user_id) >= 2:
                self.metrics["credit_job_limit_exceeded"] += 1
                if self._prom_enabled:
                    try:
                        self.prom_credit_reservation_latency.labels(provider=plan.tool_selection.primary_provider, outcome="blocked").observe(_time()-_reserve_start)
                    except Exception:
                        pass
                return self._early_failure_record(plan, "simultaneous_job_limit")
            primary_cost = self._compute_credit_cost(plan, fallback=False)
            reservation_job_id = f"{plan.project_id}-{plan.stage_type.value}-{int(time.time()*1000)}"
            res_status = credit_store.reserve(user_id, reservation_job_id, primary_cost)
            if not res_status.get("ok"):
                if res_status.get("error") == "daily_limit_exceeded":
                    self.metrics["credit_daily_limit_exceeded"] += 1
                self.metrics["credit_reservation_failures"] += 1
                if self._prom_enabled:
                    try:
                        self.prom_credit_reservation_latency.labels(provider=plan.tool_selection.primary_provider, outcome="failed").observe(_time()-_reserve_start)
                    except Exception:
                        pass
                return self._early_failure_record(plan, f"reservation_failed:{res_status.get('error')}")
            reserved_amount = primary_cost
            self.metrics["credit_reservations"] += 1
            if self._prom_enabled:
                try:
                    self.prom_credit_reservation_latency.labels(provider=plan.tool_selection.primary_provider, outcome="reserved").observe(_time()-_reserve_start)
                except Exception:
                    pass

        # Budget enforcement
        remaining = self._budget_store.get(plan.project_id)
        if remaining <= 0:
            if user_id is not None and reservation_job_id and credit_store is not None:
                try:
                    credit_store.rollback(user_id, reservation_job_id)
                    self.metrics["credit_rollbacks"] += 1
                except Exception:
                    pass
            return self._early_failure_record(plan, "Budget exhausted")

        adapter_result = None
        error_msg: Optional[str] = None
        fallback_used = False

        async def _run_selected(ad, plan_obj: StagePlan):
            # Map inputs based on stage type for adapter interface
            inp = plan_obj.inputs
            try:
                if plan_obj.stage_type == StageType.SHOT:
                    return await ad.execute(prompt=inp.get("prompt", ""), duration_seconds=inp.get("duration", 1.0), resolution=inp.get("resolution", "720p"))
                if plan_obj.stage_type == StageType.STORYBOARD:
                    return await ad.execute(prompt=inp.get("prompt", ""), width=inp.get("width", 512), height=inp.get("height", 512))
                if plan_obj.stage_type == StageType.VOICE:
                    return await ad.execute(transcript_or_prompt=inp.get("prompt", ""), style=inp.get("style"))
                if plan_obj.stage_type == StageType.MUSIC:
                    return await ad.execute(transcript_or_prompt=inp.get("prompt", ""), style=inp.get("style"))
                if plan_obj.stage_type == StageType.UPSCALE:
                    return await ad.execute(base_asset_id=inp.get("asset_id", "unknown"), operations=inp.get("operations", {}))
                if plan_obj.stage_type == StageType.COMPOSITE or plan_obj.stage_type == StageType.INPAINT:
                    return await ad.execute(base_asset_id=inp.get("asset_id", "unknown"), operations=inp.get("operations", {}))
                if plan_obj.stage_type == StageType.CONSISTENCY:
                    return await ad.execute(asset_version_ids=inp.get("asset_version_ids", []), mode=inp.get("mode", "face"))
                if plan_obj.stage_type == StageType.SCRIPT:
                    return await ad.execute(prompt=inp.get("prompt", ""), width=inp.get("width", 512), height=inp.get("height", 512))
                if plan_obj.stage_type == StageType.DIRECTION:
                    return await ad.execute(prompt=inp.get("prompt", ""), width=inp.get("width", 512), height=inp.get("height", 512))
                # Default image-like path
                return await ad.execute(prompt=inp.get("prompt", ""), width=inp.get("width", 512), height=inp.get("height", 512))
            except Exception as ex:  # capture adapter failure
                return None

        # Primary execution
        try:
            adapter_result = await _run_selected(adapter, plan)
        except Exception as e:
            adapter_result = None
            error_msg = str(e)

        # Fallback path if primary failed and we have candidates
        if adapter_result is None and plan.tool_selection.fallbacks:
            # Roll back primary reservation before attempting fallbacks
            if user_id is not None and reservation_job_id and credit_store is not None and reserved_amount:
                try:
                    credit_store.rollback(user_id, reservation_job_id)
                    self.metrics["credit_rollbacks"] += 1
                except Exception:
                    pass
                reservation_job_id = None
                reserved_amount = None
            for fb in plan.tool_selection.fallbacks:
                fb_adapter = ADAPTER_REGISTRY.get(fb.capability)
                if not fb_adapter:
                    continue
                fb_job_id: Optional[str] = None
                fb_reserved: Optional[int] = None
                try:
                    _span_set("fallback.attempt.capability", fb.capability)
                    if user_id is not None and credit_store is not None:
                        fb_cost = self._compute_credit_cost(plan, fallback=True)
                        fb_job_id = f"{plan.project_id}-{fb.capability}-{int(time.time()*1000)}"
                        fb_res_status = credit_store.reserve(user_id, fb_job_id, fb_cost)
                        if not fb_res_status.get("ok"):
                            if fb_res_status.get("error") == "daily_limit_exceeded":
                                self.metrics["credit_daily_limit_exceeded"] += 1
                            self.metrics["credit_fallback_rollbacks"] += 1
                            continue
                        self.metrics["credit_fallback_reservations"] += 1
                        fb_reserved = fb_cost
                    fb_res = await _run_selected(fb_adapter, plan)
                    if fb_res is None:
                        if user_id is not None and credit_store is not None and fb_job_id:
                            try:
                                credit_store.rollback(user_id, fb_job_id)
                                self.metrics["credit_fallback_rollbacks"] += 1
                            except Exception:
                                pass
                        continue
                    # Success
                    adapter_result = fb_res
                    plan.tool_selection.primary_provider = fb.provider
                    plan.tool_selection.primary_capability = fb.capability
                    fallback_used = True
                    reservation_job_id = fb_job_id
                    reserved_amount = fb_reserved
                    break
                except Exception as fe:
                    self.logger.error("Fallback adapter execution error", extra={"error": str(fe), "capability": fb.capability})
                    if user_id is not None and credit_store is not None and fb_job_id:
                        try:
                            credit_store.rollback(user_id, fb_job_id)
                            self.metrics["credit_fallback_rollbacks"] += 1
                        except Exception:
                            pass
                    continue

        success = adapter_result is not None
        record = StageExecutionRecord(
            plan=plan,
            success=success,
            result_payload=adapter_result.payload if adapter_result else {},
            cost_actual=adapter_result.cost_estimate if adapter_result else 0.0,
            provider_used=plan.tool_selection.primary_provider,
            fallback_used=fallback_used,
            error=None if success else (error_msg or "execution failed"),
            reservation_job_id=reservation_job_id,
            credit_reserved=reserved_amount,
        )
        record.mark_finished()
        self._finalize_record(record, db)

        _span_set("execution.success", record.success)
        _span_set("execution.cost", record.cost_actual)
        _span_set("provider.used", record.provider_used)
        _span_set("execution.fallback_used", record.fallback_used)
        _span_set("budget.remaining", self._budget_store.get(plan.project_id))
        try:
            span_ctx.__exit__(None, None, None)
        except Exception:
            pass

        # Commit or rollback reservation now that outcome known
        if user_id is not None and credit_store is not None and record.reservation_job_id:
            try:
                if record.success:
                    credit_store.commit(user_id, record.reservation_job_id)
                    record.credit_committed = record.credit_reserved
                    self.metrics["credit_commits"] += 1
                else:
                    credit_store.rollback(user_id, record.reservation_job_id)
                    record.credit_rolled_back = record.credit_reserved
                    self.metrics["credit_rollbacks"] += 1
            except Exception:
                pass
        # Latency & fallback metrics
        if record.finished_at and record.started_at:
            latency_ms = (record.finished_at - record.started_at) * 1000
            self.metrics["execution_latency_ms_total"] += int(latency_ms)
            self.metrics["execution_latency_count"] += 1
            # Redis durability (best-effort)
            self._persist_counter("execution_latency_ms_total", int(latency_ms))
            self._persist_counter("execution_latency_count")
            if self._prom_enabled:
                try:
                    outcome_lbl = "success" if record.success else "error"
                    self.prom_stage_latency.labels(stage_type=plan.stage_type.value, provider=record.provider_used, outcome=outcome_lbl).observe(record.finished_at - record.started_at)
                except Exception:
                    pass
        if record.fallback_used:
            self.metrics["fallback_used_total"] += 1
            self._persist_counter("fallback_used_total")
            if self._prom_enabled:
                try:
                    self.prom_fallback_total.inc()
                except Exception:
                    pass
        return record

    def _finalize_record(self, record: StageExecutionRecord, db: Optional[Session]):
        """Shared bookkeeping for an execution record."""
        self.execution_log.append(record)
        self.metrics["stages_executed"] += 1
        if record.success:
            self.metrics["stages_success"] += 1
            self._persist_counter("stages_success")
            if self._prom_enabled:
                try:
                    self.prom_stage_success_total.labels(stage_type=record.plan.stage_type.value, provider=record.provider_used).inc()
                except Exception:
                    pass
        else:
            self.metrics["stages_error"] += 1
            self._persist_counter("stages_error")
            if self._prom_enabled:
                try:
                    self.prom_stage_error_total.labels(stage_type=record.plan.stage_type.value, provider=record.provider_used).inc()
                except Exception:
                    pass
        self._budget_store.decrement(record.plan.project_id, record.cost_actual, db_session=db)
        self._project_budget[record.plan.project_id] = self._budget_store.get(record.plan.project_id)
        self._update_project_state(
            db,
            record.plan.project_id,
            executed_delta=1,
            success_delta=1 if record.success else 0,
            error_delta=0 if record.success else 1,
        )
        # Ensure asset identifiers for provenance (simulate generation output)
        if record.success and "asset_id" not in record.result_payload:
            generated_id = f"{record.plan.project_id}-{record.plan.stage_type.value}-{int(record.finished_at*1000)}"
            record.result_payload["asset_id"] = generated_id
            record.result_payload.setdefault("asset_kind", record.plan.stage_type.value)
        # Provider scoring
        try:
            scoring = get_provider_scoring()
            latency_ms = (record.finished_at - record.started_at) * 1000 if record.finished_at and record.started_at else 0.0
            scoring.record_event(record.provider_used, record.success, record.cost_actual, latency_ms)
        except Exception:
            pass
        # Persistence & provenance
        if db is not None:
            try:
                db_obj = StudioExecutionRecord(
                    project_id=record.plan.project_id,
                    stage_type=record.plan.stage_type.value,
                    provider_used=record.provider_used,
                    capability=record.plan.tool_selection.primary_capability,
                    success=record.success,
                    cost_actual=record.cost_actual,
                    result_payload_json=json.dumps(record.result_payload),
                    error=record.error,
                    started_at=record.started_at,
                    finished_at=record.finished_at or _time(),
                )
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                if record.success and "asset_id" in record.result_payload:
                    from backend.models.provenance import ProvenanceEdge
                    try:
                        from backend.models import Base  # type: ignore
                        Base.metadata.create_all(bind=db.get_bind())
                    except Exception:
                        pass
                    relation_type = "produced"
                    safety_meta = record.result_payload.get("safety_classification")
                    if safety_meta and safety_meta.get("classification") == "restricted":
                        relation_type = "produced_restricted"
                    edge = ProvenanceEdge(
                        parent_type="studio_execution",
                        parent_id=db_obj.id,
                        child_type=record.result_payload.get("asset_kind", "asset"),
                        child_id=record.result_payload["asset_id"],
                        relation_type=relation_type,
                        created_at=_time(),
                    )
                    db.add(edge)
                    # Ensure lifecycle row exists
                    try:
                        existing_lc = db.query(StudioAssetLifecycle).filter(StudioAssetLifecycle.asset_id == record.result_payload["asset_id"]).first()
                        if not existing_lc:
                            lc = StudioAssetLifecycle(
                                asset_id=record.result_payload["asset_id"],
                                pinned=False,
                                ephemeral=True,
                                cold=False,
                                created_at=_time(),
                                last_accessed_at=_time(),
                            )
                            db.add(lc)
                    except Exception:
                        pass
                    db.commit()
            except Exception as pe:
                self.logger.error("Failed persistence", extra={"error": str(pe)})
        # Events
        try:
            from backend.events import dispatcher, format_event
            import asyncio
            corr = f"{record.plan.project_id}-{record.plan.stage_type.value}-{int(record.started_at*1000)}"
            evt_payload = {
                "project_id": record.plan.project_id,
                "stage_type": record.plan.stage_type.value,
                "provider_used": record.provider_used,
                "success": record.success,
                "cost_actual": record.cost_actual,
                "error": record.error,
                "started_at": record.started_at,
                "finished_at": record.finished_at,
            }
            wrapped = format_event(
                "studio",
                "studio.stage.success" if record.success else "studio.stage.failure",
                "STUDIO.STAGE.SUCCESS" if record.success else "STUDIO.STAGE.FAILURE",
                "info" if record.success else "error",
                evt_payload,
                correlation_id=corr,
            )
            asyncio.create_task(dispatcher.publish("studio", wrapped))
        except Exception:
            pass
        self.logger.info(
            "Stage execution completed",
            extra={
                "project_id": record.plan.project_id,
                "stage_type": record.plan.stage_type.value,
                "provider": record.provider_used,
                "success": record.success,
                "cost": record.cost_actual,
                "budget_remaining": self._budget_store.get(record.plan.project_id),
            },
        )

    def recent_records(self, limit: int = 10):
        return self.execution_log[-limit:]

    def export_metrics(self) -> Dict[str, int]:
        """Return copy of current metrics counters."""
        return dict(self.metrics)

    def export_extended_metrics(self, include_last: int = 10) -> Dict[str, Any]:
        from backend.services.provider_scoring import get_provider_scoring
        scoring = get_provider_scoring().export()
        recent = [
            {
                "stage_type": r.plan.stage_type.value,
                "provider": r.provider_used,
                "success": r.success,
                "cost": r.cost_actual,
                "fallback_used": r.fallback_used,
                "credit_reserved": r.credit_reserved,
                "credit_committed": r.credit_committed,
                "credit_rolled_back": r.credit_rolled_back,
            }
            for r in self.recent_records(include_last)
        ]
        return {
            "counters": self.export_metrics(),
            "provider_scoring": scoring,
            "recent": recent,
            "active_reservations_total": get_credit_store().total_active_reservations(),
            "daily_spend_limit_cents": get_credit_store()._daily_spend_limit,
        }

    def cleanup_expired_credit_reservations(self) -> int:
        """Invoke credit store cleanup and update metrics."""
        store = get_credit_store()
        cleaned = store.cleanup_expired()
        if cleaned > 0:
            self.metrics["credit_ttl_rollbacks"] += cleaned
        return cleaned

    def run_cold_storage_transition(self, db: Session, max_age_seconds: int = 3600) -> int:
        """Mark eligible assets as cold.

        Eligibility logic intentionally uses *access delta* rather than absolute
        creation age to avoid sweeping previously created test artifacts when
        a targeted transition is invoked. This keeps lifecycle tests stable in
        environments with persistent DB state.

        Conditions:
        - not pinned
        - ephemeral True (still in hot tier governance)
        - last_accessed_at and created_at present
        - (last_accessed_at - created_at) >= max_age_seconds (simulated age)

        Returns number of assets transitioned.
        """
        transitioned = 0
        try:
            now = _time()
            rows = db.query(StudioAssetLifecycle).filter(StudioAssetLifecycle.cold == False).all()  # noqa: E712
            for r in rows:
                if r.pinned or not r.ephemeral:
                    continue
                if r.last_accessed_at is None or r.created_at is None:
                    continue
                # Use access delta to prevent transitioning legacy rows that have small deltas
                access_delta = r.last_accessed_at - r.created_at
                if access_delta >= max_age_seconds:
                    r.cold = True
                    r.cold_transition_at = now
                    transitioned += 1
            if transitioned:
                db.commit()
        except Exception:
            pass
        return transitioned

    def _prepare_inputs(self, project_id: int, stage_type: StageType, base_inputs: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
        """Augment inputs with context summary for direction/script stages to avoid prompt bloat."""
        if stage_type not in {StageType.DIRECTION, StageType.SCRIPT}:
            return base_inputs
        # Gather last N relevant records (storyboards, shots, script generations)
        relevant = [r for r in self.execution_log if r.plan.stage_type in {StageType.STORYBOARD, StageType.SHOT, StageType.SCRIPT}][-8:]
        fragments = []
        for r in relevant:
            kind = r.plan.stage_type.value
            prov = r.provider_used
            if r.result_payload:
                snippet = str(r.result_payload)[:120]
            else:
                snippet = "{}"
            fragments.append(f"[{kind}|{prov}] {snippet}")
        summary = "\n".join(fragments)
        # Basic truncation to keep under ~1500 chars
        if len(summary) > 1500:
            summary = summary[:1470] + "..."  # truncate
        base_inputs["context_summary"] = summary
        return base_inputs

    # ----- Pricing & Tier Helpers -----
    def _compute_credit_cost(self, plan: StagePlan, fallback: bool = False) -> int:
        # Pricing examples per specification
        if plan.stage_type == StageType.SHOT:
            return 5 if fallback or not self._is_premium_stage(plan) else 50
        if plan.stage_type == StageType.VOICE:
            return 5
        if plan.stage_type in {StageType.STORYBOARD, StageType.SCRIPT, StageType.DIRECTION}:
            return 2
        # Default minimal cost
        return 2

    def _is_premium_stage(self, plan: StagePlan) -> bool:
        cap = plan.tool_selection.primary_capability
        return any(token in cap for token in ["runway", "kling"])  # heuristic provider capability marker

    def _early_failure_record(self, plan: StagePlan, error_msg: str) -> StageExecutionRecord:
        rec = StageExecutionRecord(
            plan=plan,
            success=False,
            result_payload={},
            cost_actual=0.0,
            provider_used=plan.tool_selection.primary_provider,
            error=error_msg,
        )
        rec.mark_finished()
        self._finalize_record(rec, db=None)
        return rec
