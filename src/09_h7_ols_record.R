# 09_h7_ols_record.R -- H7a/H7b OLS moderated regression, THE ONLY ESTIMATION OF
# H7a/H7b in this pipeline (PLS-SEM never estimates or reports H7a/H7b, not even
# for reference -- CLAUDE.md SS32).
#
# REWRITTEN 2026-09-24 against docs/Theoretical_Foundations_v2_14.docx (the current
# governing TF -- v2.13/A21_DRAFT.docx and the earlier A22_main400_DRAFT (1).docx no
# longer exist; always re-extract docs/ before trusting this file, per CLAUDE.md's
# own standing instruction). v2.14 SS C.2.2 confirms, with specific amendment numbers:
#   - Amendment A-14: the predicted sign of BOTH interactions is NEGATIVE
#     (beta_M1 < 0, beta_M2 < 0, "dampening") -- earlier versions' "> 0 / buffering"
#     wording is explicitly called a TYPING ERROR, now corrected throughout the TF.
#   - Amendment A-15 (ratified, not "pending"): OLS moderated regression IS the
#     estimation of record for H7a/H7b (not PLS-SEM) -- Holm-Bonferroni removed,
#     5,000-resample bootstrap, BCa 95% CI, nominal p<.05.
#   - Amendment A-16 (pending ratification, but already the model of record per
#     SS C.2.2's own text): TWO SEPARATE single-moderator OLS regressions, one per
#     hypothesis, Hayes' PROCESS Model 1 template -- WITHOUT REL and WITHOUT the
#     other institutional carrier as a covariate (both were mistakenly included in
#     this script before this rewrite):
#       H7a: TRU = b0 + b1*INT_c + b2*PDPL_c + beta_M1*(INT_c x PDPL_c) + e
#       H7b: TRU = b0 + b1*INT_c + b2*DISC_c + beta_M2*(INT_c x DISC_c) + e
#   - The A-15-era "pooled model with REL" (TRU = b0 + b1*REL + b2*INT_c + b3*PDPL_c +
#     b4*DISC_c + beta_M1*(INT_c x PDPL_c) + beta_M2*(INT_c x DISC_c) + e, one model,
#     both interactions together, mirroring H4) is EXPLICITLY RETAINED as a sensitivity
#     analysis, not the model of record.
# CLAUDE.md SS29 documents this correction and supersedes SS26-SS28's "PLS-SEM is the
# record, Buffering is predicted" framing, which was wrong on both counts.
#
# Construct scores: equal-weighted indicator means (INT1-INT5, PDPL1-PDPL4, TRU1-TRU6);
# DISC is the 0/1 dummy; INT, PDPL, DISC mean-centred BEFORE the products are formed.
# Sample of record: MAIN-ONLY. Stopping rule: collection stops at N_main = 400 valid
#   cases ("H7 is not analysed before the stop"). Running this on N_main < 400 is an
#   INTERIM LOOK, labelled as such, not the verdict of record. Full sample / pilot are
#   sensitivity only and not run here.
# **FINAL / confirmatory run, 2026-09-26**: Khai confirmed n_main=406 (>= N_main=400) is
#   the locked, final sample -- no further data collection. This is the verdict of
#   record, not an interim look; the runtime label below reflects this once N>=400.
# Influential cases: Cook's distance computed once on the model of record (per
#   hypothesis), threshold 4/N, applied uniformly; flagged cases listed. Conclusions
#   rest on ALL N; the run without flagged cases is sensitivity, and "supported"
#   requires the verdict to hold in BOTH.
# Inference (Amendment A-15): case-resampling bootstrap, 5,000 resamples, BCa 95% CI,
#   two-tailed for the CI itself, seed 123. No Holm or other multiple-comparison
#   adjustment. HC3 (SE + p) and classical p reported alongside for completeness.
# Verdict rule (Amendment A-15, DIRECTIONAL -- corrected 2026-09-24, was wrongly
#   non-directional before this rewrite): H7a (H7b) is supported if and only if its
#   95% BCa CI excludes zero AND the coefficient is negative, as predicted
#   (beta_M1 < 0 / beta_M2 < 0). A significant POSITIVE coefficient is reported as
#   such and does NOT count as support. Simple slopes (PDPL -1SD/Mean/+1SD; DISC=0/1)
#   and f2 (change in R2) reported with bootstrap intervals.
# Usage: Rscript src/09_h7_ols_record.R data/processed/main_clean_data.csv

suppressMessages(library(boot))
suppressMessages(library(lmtest))
args <- commandArgs(trailingOnly = TRUE)
d <- read.csv(args[1]); N <- nrow(d); R <- 5000; set.seed(123)
d$INT_c <- d$INT_mean - mean(d$INT_mean); d$PDPL_c <- d$PDPL_mean - mean(d$PDPL_mean)
d$DISC_c <- d$DISC_COND - mean(d$DISC_COND)
d$INT_x_PDPL <- d$INT_c * d$PDPL_c; d$INT_x_DISC <- d$INT_c * d$DISC_c

# Model of record (Amendment A-16): two separate simple-moderation regressions, no
# REL, no cross-covariate.
f_H7a <- TRU_mean ~ INT_c + PDPL_c + INT_x_PDPL
f_H7b <- TRU_mean ~ INT_c + DISC_c + INT_x_DISC
# Sensitivity (Amendment A-15 form, retained per SS C.2.2): ONE pooled model with REL,
# both interactions together, mirroring H4's REL covariate.
f_pooled <- TRU_mean ~ REL_mean + INT_c + PDPL_c + DISC_c + INT_x_PDPL + INT_x_DISC

if (N >= 400) {
  cat(sprintf("\n*** FINAL / CONFIRMATORY RUN: main-only N=%d (>= stopping rule N_main=400). This IS the verdict of record. ***\n", N))
} else {
  cat(sprintf("\n*** INTERIM LOOK: main-only N=%d < 400 (stopping rule N_main=400; 'H7 is not analysed before the stop'). Not the verdict of record. ***\n", N))
}

# HC3-robust SE + p for one coefficient (MacKinnon & White, 1985 HC3 estimator).
hc3_stats <- function(m, t) {
  X <- model.matrix(m); e <- resid(m); h <- hatvalues(m); XtXi <- solve(crossprod(X))
  V <- XtXi %*% crossprod(X * (e / (1 - h)), X * (e / (1 - h))) %*% XtXi
  se <- sqrt(V[t, t])
  list(se = se, p = 2 * pt(-abs(coef(m)[t] / se), df.residual(m)))
}

# One PROCESS-Model-1-style analysis: X=INT, moderator = mod_c (already centred), `term`
# is the exact interaction column name to test (looked up BY NAME, not by position --
# needed because the pooled sensitivity model has two interaction terms, so the one
# being tested is not necessarily the last coefficient). `levels` is a named numeric
# vector of moderator evaluation points (name = printed label).
analyse <- function(dat, label, formula, term, hyp, levels) {
  m0 <- lm(formula, dat); cd <- cooks.distance(m0); thr <- 4 / nrow(dat); flagged <- which(cd > thr)
  nlev <- length(levels)
  stat <- function(x, i) {
    mm <- lm(formula, x[i, ]); b <- coef(mm)
    bM <- unname(b[term]); bINT <- unname(b["INT_c"])
    c(bM, bINT + bM * as.numeric(levels))
  }
  bt <- boot(dat, stat, R = R); m <- lm(formula, dat); s <- summary(m)$coefficients
  pb <- sapply(1:(1 + nlev), function(k) 2 * min(mean(bt$t[, k] <= 0), mean(bt$t[, k] > 0)))
  ci <- t(sapply(1:(1 + nlev), function(k) { b <- boot.ci(bt, type = "bca", index = k)$bca; c(b[4], b[5]) }))
  r2 <- summary(m)$r.squared
  mr <- update(m, as.formula(paste(". ~ . -", term))); f2 <- (r2 - summary(mr)$r.squared) / (1 - r2)
  hc3 <- hc3_stats(m, term)
  tab <- data.frame(analysis = label, n = nrow(dat),
    term = c(sprintf("%s beta_M (%s)", hyp, term), sprintf("slope INT->TRU %s", names(levels))),
    estimate = round(bt$t0, 4), bca_low = round(ci[, 1], 4), bca_high = round(ci[, 2], 4),
    ci_excludes_0 = (ci[, 1] > 0) | (ci[, 2] < 0), p_boot = round(pb, 4),
    p_classical = c(round(s[term, 4], 4), rep(NA, nlev)),
    SE_HC3 = c(round(hc3$se, 4), rep(NA, nlev)),
    p_HC3 = c(round(hc3$p, 4), rep(NA, nlev)),
    f2 = c(round(f2, 4), rep(NA, nlev)), R2 = round(r2, 3), row.names = NULL)
  # DIRECTIONAL verdict (Amendment A-15, TF v2.14 SS C.2.2): supported iff the CI is
  # entirely negative (excludes zero on the negative side) AND p < .05. A significant
  # POSITIVE coefficient is NOT support, even though it also "excludes zero".
  ver <- if (ci[1, 2] < 0 && pb[1] < .05) "supported (as predicted, dampening)" else "not supported"
  # Heteroscedasticity diagnostics on the fitted model (Breusch-Pagan: standard, on the
  # model's own regressors; White: the common bptest() approximation using fitted values
  # + fitted^2 as the auxiliary regressors, per Wooldridge's textbook simplification).
  bp <- bptest(m); wh <- bptest(m, varformula = ~ fitted(m) + I(fitted(m)^2))
  hetero <- data.frame(hypothesis = hyp, analysis = label, n = nrow(dat),
    bp_stat = round(unname(bp$statistic), 4), bp_df = unname(bp$parameter), bp_p = round(bp$p.value, 4),
    white_stat = round(unname(wh$statistic), 4), white_df = unname(wh$parameter), white_p = round(wh$p.value, 4),
    row.names = NULL)
  list(tab = tab, ver = ver, sign = sign(bt$t0[1]), flagged = flagged, dat = dat, hetero = hetero)
}
options(width = 250)

sdP <- sd(d$PDPL_mean)
run_hypothesis <- function(formula, term, hyp, levels) {
  A <- analyse(d, "all N (conclusions rest on this)", formula, term, hyp, levels)
  cat(sprintf("\nCook's D on the %s model of record: threshold 4/N = %.5f; %d flagged case(s): %s\n",
              hyp, 4 / N, length(A$flagged), paste(A$flagged, collapse = ", ")))
  dat_wo <- if (length(A$flagged) == 0) d else d[-A$flagged, ]
  rownames(dat_wo) <- NULL  # bptest()'s fitted()-based varformula mis-sizes its
                            # auxiliary regression when the data.frame keeps the
                            # original (non-sequential) row names after subsetting
  B <- analyse(dat_wo, "without Cook's-D-flagged cases (sensitivity)", formula, term, hyp, levels)
  for (r in list(A, B)) { cat(sprintf("\n===== %s, %s, n=%d =====\n", hyp, r$tab$analysis[1], r$tab$n[1])); print(r$tab[, -(1:2)], row.names = FALSE) }
  final <- if (grepl("^supported", A$ver) && grepl("^supported", B$ver))
    "supported (as predicted, dampening)" else "not supported"
  list(A = A, B = B, final = final)
}

# H7a: PROCESS Model 1, X=INT, W=PDPL (mean-centred). 3 evaluation points (Table 15):
# PDPL -1SD, Mean (PDPL_c=0), +1SD.
res_H7a <- run_hypothesis(f_H7a, "INT_x_PDPL", "H7a",
                           c("PDPL -1SD" = -sdP, "PDPL Mean" = 0, "PDPL +1SD" = sdP))
# H7b: PROCESS Model 1, X=INT, W=DISC (mean-centred 0/1). 2 natural levels only.
lo_disc <- 0 - mean(d$DISC_COND); hi_disc <- 1 - mean(d$DISC_COND)
res_H7b <- run_hypothesis(f_H7b, "INT_x_DISC", "H7b", c("DISC=0" = lo_disc, "DISC=1" = hi_disc))

# Sensitivity: pooled model with REL (Amendment A-15 form), both interactions in ONE
# fit -- reuses `analyse()` twice on the SAME formula/data, once per term, all-N only
# (SS C.2.2 does not ask for a Cook's-D-trimmed variant of this sensitivity model).
cat("\n--- Sensitivity: pooled model with REL (A-15 form, both interactions together) ---\n")
sens_H7a <- analyse(d, "pooled model with REL (A-15 form, sensitivity)", f_pooled, "INT_x_PDPL", "H7a",
                     c("PDPL -1SD" = -sdP, "PDPL Mean" = 0, "PDPL +1SD" = sdP))
sens_H7b <- analyse(d, "pooled model with REL (A-15 form, sensitivity)", f_pooled, "INT_x_DISC", "H7b",
                     c("DISC=0" = lo_disc, "DISC=1" = hi_disc))
for (r in list(sens_H7a, sens_H7b)) { cat(sprintf("\n===== %s =====\n", r$tab$term[1])); print(r$tab[, -(1:2)], row.names = FALSE) }

run_label <- if (N >= 400) "FINAL / confirmatory" else "INTERIM LOOK"
cat(sprintf("\nVerdict (Amendment A-15, model of record; %s; 'supported' requires BOTH the all-N and Cook's-D-trimmed runs; predicted direction is Dampening, beta_M1 < 0 and beta_M2 < 0, per Amendment A-14):\n", run_label))
verdict_tab <- data.frame(
  hypothesis = c("H7a", "H7b"),
  all_N = c(res_H7a$A$ver, res_H7b$A$ver),
  without_flagged = c(res_H7a$B$ver, res_H7b$B$ver),
  verdict = c(res_H7a$final, res_H7b$final),
  sign_all_N = c(ifelse(res_H7a$A$sign < 0, "negative (Dampening direction)", "positive (opposite predicted direction)"),
                 ifelse(res_H7b$A$sign < 0, "negative (Dampening direction)", "positive (opposite predicted direction)")))
print(verdict_tab, row.names = FALSE)

cat("\nHeteroscedasticity diagnostics (Breusch-Pagan; White = bptest() with fitted + fitted^2 auxiliary regressors):\n")
hetero_tab <- rbind(res_H7a$A$hetero, res_H7a$B$hetero, res_H7b$A$hetero, res_H7b$B$hetero)
print(hetero_tab, row.names = FALSE)

out_suffix <- if (N >= 400) "FINAL" else "INTERIM"
write.csv(rbind(res_H7a$A$tab, res_H7a$B$tab, res_H7b$A$tab, res_H7b$B$tab, sens_H7a$tab, sens_H7b$tab),
          sprintf("outputs/tables/h7_ols_record_A15_A16_PROCESS_M1_%s.csv", out_suffix), row.names = FALSE)
write.csv(hetero_tab, "outputs/tables/h7_heteroscedasticity_diagnostics.csv", row.names = FALSE)
