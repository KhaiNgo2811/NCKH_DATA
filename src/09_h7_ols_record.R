# 09_h7_ols_record.R (renumbered 2026-09-23 from 13_h7_ols_record.R after removing
# 09_h7_supplementary.{py,R}/10_jn_micom.R/11_ols_model1_bootstrap.R/
# 12_process_moderated_mediation.R -- see CLAUDE.md for the reorg) -- H7a/H7b OLS
# model of record per Theoretical_Foundations v2.13
# (file: Theoretical_Foundations_v2_13_A22_main400_DRAFT (1).docx), Amendment A-22
# (ratified 21 Sep 2026: Holm-Bonferroni filter removed, H7a re-signed to Dampening,
# beta_M1 < 0) and Amendment A-23 (authorized by Khai, 22 Sep 2026, pending the same
# Project Lead & Faculty Advisor ratification A-22 received: H7b re-signed to Dampening,
# beta_M2 < 0; estimation switched from one pooled two-interaction model to two separate
# single-moderator regressions following Hayes' PROCESS Model 1 template).
#
# UPDATED 2026-09-23 (requested by Khai, for the manuscript's Table 11/12/14): added (a)
# HC3-robust standard errors alongside the HC3 p already reported, (b) Breusch-Pagan and
# White heteroscedasticity tests per model (full-N run only), (c) a third PDPL evaluation
# point (Mean, i.e. PDPL_c=0) for H7a's simple slopes -- DISC stays at its 2 natural
# levels (0/1) since it has no "mean" level to speak of.
#
# Two independent PROCESS Model 1 (Hayes) regressions, one per hypothesis. Each is a
# simple moderation Y = TRU on X = INT, moderator W, and X*W, with REL and the other
# institutional carrier entered as covariates (no interaction term of their own):
#   H7a: TRU = b0 + b1*REL + b2*DISC + b3*INT_c + b4*PDPL_c + bM1*(INT_c x PDPL_c)
#   H7b: TRU = b0 + b1*REL + b2*PDPL + b3*INT_c + b4*DISC_c + bM2*(INT_c x DISC_c)
#   INT, PDPL, DISC mean-centred BEFORE each model's own product term is formed.
# Sample of record: MAIN-ONLY. Draft stopping rule: collection stops at N_main = 400 valid
#   cases and "H7 is not analysed before the stop". Running this on N_main < 400 is an INTERIM
#   LOOK: it is labelled as such in the output, is not the verdict of record, and must be
#   disclosed. The full sample / pilot are sensitivity only and are not run here.
# Influential cases: Cook's distance computed once per model (on that model's own N),
#   threshold 4/N, applied uniformly; flagged cases listed. Conclusions rest on ALL N; the
#   run without the flagged cases is sensitivity, and "supported" requires the verdict to
#   hold in BOTH.
# Inference: case-resampling bootstrap, 5,000 resamples (TF v2.13/A-22), BCa 95% CI,
#   two-tailed, seed 123. No Holm or other multiple-comparison adjustment (removed by
#   A-22) -- HC3 (SE + p) and classical p are reported alongside for reference only.
# Verdict rule (A-22/A-23): H7a (H7b) is "supported (post hoc, non-directional)" if its
#   BCa CI excludes 0 at nominal p < .05, else "not supported". The SIGN is always reported;
#   the original directional predictions are now beta_M1 < 0 and beta_M2 < 0 (both
#   Dampening) -- a negative coefficient IS the predicted direction under A-22/A-23, kept
#   distinct from the pre-amendment buffering predictions for the historical record.
#   Simple slopes (PDPL -1SD/Mean/+1SD; DISC = 0/1) and f2 reported with bootstrap intervals.
# Usage: Rscript src/09_h7_ols_record.R data/processed/clean_main.csv

suppressMessages(library(boot))
suppressMessages(library(lmtest))
args <- commandArgs(trailingOnly = TRUE)
d <- read.csv(args[1]); N <- nrow(d); R <- 5000; set.seed(123)
d$INT_c <- d$INT_mean - mean(d$INT_mean); d$PDPL_c <- d$PDPL_mean - mean(d$PDPL_mean)
d$DISC_c <- d$DISC_COND - mean(d$DISC_COND)
d$INT_x_PDPL <- d$INT_c * d$PDPL_c; d$INT_x_DISC <- d$INT_c * d$DISC_c

f_H7a <- TRU_mean ~ REL_mean + DISC_COND + INT_c + PDPL_c + INT_x_PDPL
f_H7b <- TRU_mean ~ REL_mean + PDPL_mean + INT_c + DISC_c + INT_x_DISC

cat(sprintf("\n*** INTERIM LOOK: main-only N=%d < 400 (draft stopping rule N_main=400; 'H7 is not analysed before the stop'). Not the verdict of record. ***\n", N))

# HC3-robust SE + p for one coefficient (MacKinnon & White, 1985 HC3 estimator).
hc3_stats <- function(m, t) {
  X <- model.matrix(m); e <- resid(m); h <- hatvalues(m); XtXi <- solve(crossprod(X))
  V <- XtXi %*% crossprod(X * (e / (1 - h)), X * (e / (1 - h))) %*% XtXi
  se <- sqrt(V[t, t])
  list(se = se, p = 2 * pt(-abs(coef(m)[t] / se), df.residual(m)))
}

# One PROCESS-Model-1-style analysis: X=INT, moderator = mod_c (already centred), term
# name = interaction column name, `levels` a named numeric vector of moderator
# evaluation points (name = printed label, e.g. c("PDPL -1SD" = -sdP, "PDPL Mean" = 0)).
analyse <- function(dat, label, formula, term, hyp, levels) {
  m0 <- lm(formula, dat); cd <- cooks.distance(m0); thr <- 4 / nrow(dat); flagged <- which(cd > thr)
  nlev <- length(levels)
  stat <- function(x, i) {
    mm <- lm(formula, x[i, ]); b <- coef(mm); names(b) <- NULL
    bM <- b[length(b)]; bINT <- b[names(coef(mm)) == "INT_c"]
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
  ver <- if ((ci[1, 1] > 0 | ci[1, 2] < 0) && pb[1] < .05) "supported (post hoc, non-directional)" else "not supported"
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
  final <- if (A$ver == "supported (post hoc, non-directional)" && B$ver == "supported (post hoc, non-directional)")
    "supported (post hoc, non-directional)" else "not supported"
  list(A = A, B = B, final = final)
}

# H7a: PROCESS Model 1, X=INT, W=PDPL (mean-centred), covariates REL, DISC.
# 3 evaluation points (Table 14): PDPL -1SD, Mean (PDPL_c=0), +1SD.
res_H7a <- run_hypothesis(f_H7a, "INT_x_PDPL", "H7a",
                           c("PDPL -1SD" = -sdP, "PDPL Mean" = 0, "PDPL +1SD" = sdP))
# H7b: PROCESS Model 1, X=INT, W=DISC (mean-centred 0/1), covariates REL, PDPL.
# 2 natural levels only -- DISC has no "mean" level distinct from its two categories.
lo_disc <- 0 - mean(d$DISC_COND); hi_disc <- 1 - mean(d$DISC_COND)
res_H7b <- run_hypothesis(f_H7b, "INT_x_DISC", "H7b", c("DISC=0" = lo_disc, "DISC=1" = hi_disc))

cat("\nVerdict per A-22/A-23 (INTERIM LOOK, read from this run; 'supported' requires BOTH analyses; predicted direction is now Dampening, beta_M < 0, for both H7a and H7b):\n")
verdict_tab <- data.frame(
  hypothesis = c("H7a", "H7b"),
  all_N = c(res_H7a$A$ver, res_H7b$A$ver),
  without_flagged = c(res_H7a$B$ver, res_H7b$B$ver),
  verdict = c(res_H7a$final, res_H7b$final),
  sign_all_N = c(ifelse(res_H7a$A$sign < 0, "negative (Dampening direction)", "positive"),
                 ifelse(res_H7b$A$sign < 0, "negative (Dampening direction)", "positive")),
  supported_as_predicted_A22_A23 = c(
    ifelse(res_H7a$A$sign < 0 & res_H7a$final != "not supported", "supported as predicted (Dampening)", "not supported"),
    ifelse(res_H7b$A$sign < 0 & res_H7b$final != "not supported", "supported as predicted (Dampening)", "not supported")))
print(verdict_tab, row.names = FALSE)

cat("\nHeteroscedasticity diagnostics (Breusch-Pagan; White = bptest() with fitted + fitted^2 auxiliary regressors):\n")
hetero_tab <- rbind(res_H7a$A$hetero, res_H7a$B$hetero, res_H7b$A$hetero, res_H7b$B$hetero)
print(hetero_tab, row.names = FALSE)

write.csv(rbind(res_H7a$A$tab, res_H7a$B$tab, res_H7b$A$tab, res_H7b$B$tab),
          "outputs/tables/h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv", row.names = FALSE)
write.csv(hetero_tab, "outputs/tables/h7_heteroscedasticity_diagnostics.csv", row.names = FALSE)
