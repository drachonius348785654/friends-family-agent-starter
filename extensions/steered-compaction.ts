/**
 * Deferred compaction -- deferral only.
 *
 * Pi's built-in summarizer is good (8-31k structured summaries, and it handled a
 * 355k-token input correctly). What it cannot do is pick a convenient moment:
 * automatic (threshold) compaction can fire between tool batches inside a run,
 * i.e. mid-task.
 *
 * So this extension changes only WHEN compaction happens, never HOW:
 *
 *   - an automatic ("threshold") compaction is cancelled and remembered, then
 *     re-issued once the run has actually finished;
 *   - "manual" and "overflow" are never touched -- manual is the user asking,
 *     and overflow recovery must succeed for the run to continue;
 *   - the summary is always Pi's own summarizer, at the model's own configured
 *     threshold. No custom prompt, no alternate model.
 *
 * The threshold stays yours. Per-model triggers live in
 * ~/.pi/agent/settings.json -> compaction.modelOverrides.<provider>/<model>
 * .reserveTokens, where trigger = contextWindow - reserveTokens. Deferral does
 * not shift those numbers; it moves the moment they fire to a run boundary.
 *
 * HISTORY -- read before editing. An earlier version of this file also replaced
 * the summarizer with a cheap model and a custom prompt. It worked at ~40k
 * input and returned a 451-character fragment of raw transcript at 371k input,
 * wiping a live session's context. Do not reintroduce a custom summarizer
 * without testing at 300k+ input and comparing against Pi's default.
 *
 * Env overrides:
 *   STEERED_COMPACT_HARD  safety valve (default 850000): above this, a threshold
 *                         compaction is allowed through mid-run rather than
 *                         deferred further.
 *   STEERED_COMPACT_SOFT  optional. Unset by default, which means "compact at the
 *                         run boundary whenever Pi itself asked for it" -- i.e.
 *                         your per-model trigger decides, not this file. Set it
 *                         only to force an earlier floor.
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

/** Above this, stop deferring and let Pi compact mid-run. Safety valve only. */
const HARD_TOKENS = Number(process.env.STEERED_COMPACT_HARD ?? 850_000);

/** Never defer past this fraction of the model's own context window. */
const HARD_WINDOW_FRACTION = 0.9;

/** Optional floor. null = defer whenever Pi asks, honouring its own threshold. */
const SOFT_TOKENS = process.env.STEERED_COMPACT_SOFT
	? Number(process.env.STEERED_COMPACT_SOFT)
	: null;

export default function (pi: ExtensionAPI) {
	/** Set when a threshold compaction was deferred, cleared when handled. */
	let deferred = false;

	pi.on("session_before_compact", async (event, ctx) => {
		const { preparation, reason } = event as any;
		const tokens = preparation?.tokensBefore ?? 0;

		if (reason !== "threshold") {
			return; // manual / overflow: Pi's own summarizer, untouched
		}

		// Safety valve, sized against the model's own window: a flat 850k would sit
		// above the entire context of a small-window model (kimi is 256k), so
		// deferral could run straight into the provider's limit instead of stopping.
		const usage = ctx.getContextUsage();
		const window = usage?.contextWindow ?? ctx.model?.contextWindow;
		const hard = window ? Math.min(HARD_TOKENS, Math.floor(window * HARD_WINDOW_FRACTION)) : HARD_TOKENS;
		if (tokens >= hard) {
			return; // large enough that waiting for the run to end is the bigger risk
		}

		deferred = true;
		if (ctx.hasUI) {
			ctx.ui.notify(
				`Compaction deferred to end of run (${tokens.toLocaleString()} tokens)`,
				"info",
			);
		}
		return { cancel: true };
	});

	// Re-issue the deferred compaction now that the run has finished.
	pi.on("agent_end", async (_event, ctx) => {
		if (!deferred) {
			return;
		}
		deferred = false;

		if (SOFT_TOKENS !== null) {
			const tokens = ctx.getContextUsage()?.tokens ?? 0;
			if (tokens < SOFT_TOKENS) {
				return;
			}
		}

		if (ctx.hasUI) {
			ctx.ui.notify("Compacting at end of run (deferred from mid-run)", "info");
		}
		ctx.compact({
			onError: (error: Error) => {
				ctx.ui.notify(`Deferred compaction failed: ${error.message}`, "error");
			},
		});
	});

	pi.registerCommand("trigger-compact", {
		description: "Compact now, optionally with instructions",
		handler: async (args: string, ctx: ExtensionContext) => {
			const instructions = (args ?? "").trim() || undefined;
			deferred = false;
			ctx.compact({
				customInstructions: instructions,
				onError: (error: Error) => {
					ctx.ui.notify(`Compaction failed: ${error.message}`, "error");
				},
			});
		},
	});
}
