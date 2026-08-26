# 07_plssem_bridge.R
# PLS-SEM model specification via seminr, matching TF v2.3 Table 1 / SS C.1 / SS C.3
# (post Amendment A-8).
# Called from Python via rpy2 (see run_plssem.py). Not run standalone for reporting -
# always cross-validate against SmartPLS 4 output before a number goes in the manuscript
# (CLAUDE.md SS5, 07_plssem_bridge.R docstring rule).
#
# GOVERNANCE-OPEN: TRU/ENG item counts below (TRU1-5, ENG1-6) match the FIELDED
# instrument, not TF v2.2 Table 5. See CLAUDE.md SS1 and src/_config.py.
# DISC_COND enters as an OBSERVED DUMMY predictor - never as a reflective construct.

lib 

run_plssem <- function(data) {

  # ---- Measurement model (reflective constructs only; DISC is never here) ----
  measurements <- constructs(
    composite("AIP",  multi_items("AIP", 1:6)),
    composite("REL",  multi_items("REL", 1:4)),
    composite("INT",  multi_items("INT", 1:5)),
    composite("TRU",  multi_items("TRU", 1:5)),   # GOVERNANCE-OPEN: fielded=5, TF Table5=6
    composite("ENG",  multi_items("ENG", 1:6)),    # GOVERNANCE-OPEN: fielded=6, TF Table5=5
    composite("PI",   multi_items("PI", 1:3)),
    composite("PDPL", multi_items("PDPL", 1:4))
  )

  # ---- Structural model ----
  # H1 AIP->REL, H2 AIP->INT, H4 REL->TRU, H5 REL->ENG,
  # H6a INT->TRU, H6b INT->ENG, H6c INT->PI, E1 TRU->ENG, E2 ENG->PI
  # DISC_COND (observed 0/1) enters as a specification term (DISC->INT) plus the H7a
  # (PDPL×INT) and H7b (DISC×INT) two-way interaction terms — NOT a three-way product
  # term. seminr interaction terms are added via the `interactions` block.
  structure <- relationships(
    paths(from = "AIP",  to = c("REL", "INT")),
    paths(from = "REL",  to = c("TRU", "ENG")),
    paths(from = "INT",  to = c("TRU", "ENG", "PI")),
    paths(from = "TRU",  to = "ENG"),   # E1
    paths(from = "ENG",  to = "PI"),    # E2
    paths(from = "DISC_COND", to = "INT")  # specification term, NOT a second H3 test
  )

  model <- estimate_pls(data = data, measurement_model = measurements,
                         structural_model = structure, missing_value = NA)

  boot <- bootstrap_model(seminr_model = model, nboot = 10000, cores = NULL, seed = 123)

  list(
    loadings = model$outer_loadings,
    weights = model$outer_weights,
    ave = model$rSquared,  # placeholder - replace with proper reliability() call, see NOTE
    path_coefficients = model$path_coef,
    htmt = HTMT(model),
    boot_paths = summary(boot)$bootstrapped_paths
  )
}

# NOTE: This is a STRUCTURE, not a finished script. Before running on real n>=400 data:
#  1. Add ONLY beta_M1 (INT×PDPL→TRU) and beta_M2 (INT×DISC→TRU) as two separate
#     two-way interaction terms via seminr::interactions() / the two-stage approach
#     (Becker et al., 2018) per TF v2.3 SS C.2 (Amendment A-8). Do NOT add a three-way
#     INT×PDPL×DISC product term — it is retired.
#  2. Add MICOM (measurement invariance) via cSEM before any PLS-MGA interpretation
#     (TF v2.2 SS C.2 "Primary - permutation-based multi-group analysis"). Per
#     Amendment A-8, PLS-MGA/MICOM across DISC groups is no longer required
#     specifically for H7 testing.
#  3. Replace the `ave` placeholder with a real reliability()/AVE extraction call.
#  4. Cross-validate every reported number against SmartPLS 4 before manuscript use.
