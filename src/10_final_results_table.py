"""
10_final_results_table.py (renumbered 2026-09-23 from 14_final_results_table.py after
removing 09_h7_supplementary.{py,R}/10_jn_micom.R/11_ols_model1_bootstrap.R/
12_process_moderated_mediation.R -- see CLAUDE.md for the reorg) - assemble ONE
results table for the MAIN sample (2026-09-21, requested by Khai): variables
(descriptives, reliability, validity), manipulation checks, two-way ANOVA (H3),
PLS-SEM paths (the estimator of record for H7a/H7b too, per TF v2.13/A-21 --
docs/Theoretical_Foundations_v2_13_A21_DRAFT.docx, DRAFT pending ratification --
which predicts Buffering, beta_M > 0, for both; A-22/A-23's Dampening resign and
OLS-as-record framing are rescinded, CLAUDE.md SS26), indirect effects, and the
supplementary OLS Hayes PROCESS Model 1 sensitivity check for H7a/H7b (kept
running exactly as before per Khai's instruction, INTERIM). Reads existing
outputs only; runs no analysis.
Writes outputs/tables/FINAL_results_main_all.csv (+ .xlsx). No verdict is assigned here
beyond applying each analysis's own rule to its own output.
Requires these to have been run first on the same data, all with --sample-role main:
01_clean.py, 03, 04, 05, run_plssem.py (default output names), 09_h7_ols_record.R.
"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import statsmodels.formula.api as smf
from scipy.stats import chisquare
from scipy import stats

sys.path.insert(0, "src")
from _config import DEMOGRAPHIC_VALUE_LABELS, CONSTRUCT_ITEMS, ITEM_WORDING_EN  # noqa: E402

T = "outputs/tables/"
F = "outputs/figures/"
main = pd.read_csv("data/processed/main_clean_data.csv")
N = len(main)
rows = []


def add(section, item, pred="", n="", est="", stat="", ci="", p="", eff="", verdict="", note=""):
    rows.append(dict(Section=section, Item=item, Prediction=pred, n=n, Estimate=est, Stat_t_F=stat,
                     CI95=ci, p=p, EffectSize=eff, Verdict=verdict, Note=note))


def fp(p):
    return "<.001" if p < .001 else f"{p:.3f}"


# A. Sample
add("A. Sample", "main sample (administrative label, A-19)", n=N,
    note=f"AIP Low/High = {int((main.AIP_COND == 0).sum())}/{int((main.AIP_COND == 1).sum())}; "
         f"DISC No/With = {int((main.DISC_COND == 0).sum())}/{int((main.DISC_COND == 1).sum())}; "
         f"below the N_main=400 target -> interim / exploratory")

# B. Variables
SEC_B = "B. Variables (mean scores 1-7, reliability, validity)"
rel = pd.read_csv(T + "plssem_reliability_main.csv", index_col=0)
for c in ["AIP", "REL", "INT", "TRU", "ENG", "PI", "PDPL"]:
    s = main[f"{c}_mean"]
    r = rel.loc[c]
    ok = r.alpha > .7 and r.rhoA > .7 and r.rhoC > .7 and r.AVE > .5
    add(SEC_B, c, n=N, est=f"mean {s.mean():.2f}, SD {s.std():.2f}",
        note=f"alpha {r.alpha:.3f}, rhoA {r.rhoA:.3f}, CR {r.rhoC:.3f}, AVE {r.AVE:.3f}; "
             f"min {s.min():.2f} max {s.max():.2f}; skew {s.skew():.2f}",
        verdict="reliability & AVE OK" if ok else "CHECK")
add(SEC_B, "DISC_COND (0/1 dummy)", n=N, est=f"{main.DISC_COND.mean() * 100:.1f}% With Disclosure",
    note="observed dummy, no reliability")
add(SEC_B, "AIP_COND (0/1)", n=N, est=f"{main.AIP_COND.mean() * 100:.1f}% High AIP", note="ANOVA factor only")
h = pd.read_csv(T + "plssem_htmt_main.csv", index_col=0)
hh = h.loc[["REL", "INT", "TRU", "ENG", "PDPL", "PI"], ["AIP", "REL", "INT", "TRU", "ENG", "PDPL"]].astype(float)
add(SEC_B, "HTMT discriminant validity", n=N,
    est=f"max {np.nanmax(hh.values):.3f} (AIP-REL {h.loc['REL', 'AIP']:.3f})", verdict="all < 0.85 OK")
iv = pd.read_csv(T + "plssem_inner_vif_main.csv")
ov = pd.read_csv(T + "plssem_outer_vif_main.csv")
add(SEC_B, "Collinearity / CMB", n=N,
    est=f"max inner VIF {iv.vif.max():.2f}; max outer VIF {ov.vif.max():.2f}", verdict="all < 3.3 OK")

# C. Manipulation checks
mc = pd.read_csv(T + "pilot_manipulation_check_main.csv")
for _, r in mc.iterrows():
    add("C. Manipulation checks (ITT, report only)", f"{r.mc_column} by {r.group_col}",
        pred="High > Low (gate |d|>=0.50)", n=int(r.n_low_or_no + r.n_high_or_with),
        est=f"{r.mean_low_or_no:.2f} vs {r.mean_high_or_with:.2f}", stat=f"t={r.t:.2f}", p=fp(r.p),
        eff=f"d={r.cohens_d:.3f}", verdict="PASS" if r["gate_pass_d>=0.50"] else "FAIL")

# D. ANOVA
SEC_D = "D. Two-way ANOVA (INT ~ AIP_COND x DISC_COND)"
an = pd.read_csv(T + "H3_anova_disclosure_main_effect_main.csv")
df2 = int(an.loc[an.Source == "Residual", "DF"].iloc[0])
lab = {"DISC_label": ("H3: Disclosure main effect on INT (sole confirmatory test)", "- (With < No)"),
       "AIP_COND": ("AIP main effect on INT (H1/H2 replication, not H-numbered)", ""),
       "AIP_COND * DISC_label": ("AIP x DISC interaction (EXPLORATORY only)", "")}
for _, r in an.iterrows():
    if r.Source in lab:
        it, pr = lab[r.Source]
        if r.Source == "DISC_label":
            v = "Not supported" if r.p_unc >= .05 else "Significant"
        else:
            v = "n.s." if r.p_unc >= .05 else "sig. (exploratory)"
        add(SEC_D, it, pred=pr, n=N, stat=f"F(1,{df2})={r.F:.3f}", p=f"{r.p_unc:.3f}",
            eff=f"eta2p={r.np2:.3f}", verdict=v)

# E. PLS-SEM
SEC_E = "E. PLS-SEM (seminr, 10,000 percentile bootstrap)"
b = pd.read_csv(T + "plssem_bootstrap_paths_main.csv", index_col=0)
f2 = pd.read_csv(T + "plssem_f_squared_main.csv", index_col=0)
paths = [("AIP  ->  REL", "H1 AIP->REL", "+"), ("AIP  ->  INT", "H2 AIP->INT", "+"),
         ("REL  ->  TRU", "H4 REL->TRU", "+"), ("REL  ->  ENG", "H5 REL->ENG", "+"),
         ("INT  ->  TRU", "H6a INT->TRU", "-"), ("INT  ->  ENG", "H6b INT->ENG", "-"),
         ("INT  ->  PI", "H6c INT->PI", "-"), ("TRU  ->  ENG", "E1 TRU->ENG (established)", "+"),
         ("ENG  ->  PI", "E2 ENG->PI (established)", "+"), ("DISC  ->  INT", "spec DISC->INT (not H3)", ""),
         ("DISC  ->  TRU", "spec DISC->TRU", ""), ("PDPL  ->  TRU", "spec PDPL->TRU", ""),
         ("INT*PDPL  ->  TRU", "spec INT*PDPL->TRU (H7a tested via OLS Hayes PROCESS Model 1, Section G, not here)", ""),
         ("INT*DISC  ->  TRU", "spec INT*DISC->TRU (H7b tested via OLS Hayes PROCESS Model 1, Section G, not here)", "")]
for k, it, pr in paths:
    r = b.loc[k]
    a, t = [x.strip() for x in k.split("->")]
    fv = f2.loc[a, t]
    p = r["Bootstrap P Val"]
    beta = r["Original Est."]
    sig = p < .05
    sgn = (pr.startswith("+") and beta > 0) or (pr.startswith("-") and beta < 0)
    if it.startswith("E"):
        v = "Established: " + ("sig." if sig else "n.s.")
    elif not pr:
        v = ""
    else:
        v = "Supported" if sig and sgn else ("Significant, OPPOSITE sign" if sig else "Not supported")
    add(SEC_E, it, pred=pr, n=N, est=f"beta={beta:.3f}", stat=f"t={r['T Stat.']:.2f}",
        ci=f"[{r['2.5% CI']:.3f}, {r['97.5% CI']:.3f}]", p=fp(p),
        eff=f"f2={fv:.3f}" if pd.notna(fv) else "f2 n/a (seminr)", verdict=v)

# F. Indirect effects
ie = pd.read_csv(T + "plssem_indirect_effects_main.csv")
for _, r in ie.iterrows():
    add("F. Indirect effects (percentile bootstrap)", r.effect, n=N, est=f"{r.estimate:.3f}",
        ci=f"[{r.ci_low:.3f}, {r.ci_high:.3f}]", p=fp(r.p_boot),
        note=f"direct beta {r.direct_beta:.3f} (p={r.direct_p:.3f})", verdict=r.classification)

# G. OLS Hayes PROCESS Model 1 (supplementary sensitivity check, NOT the estimation
# of record -- see Section E / CLAUDE.md SS26. TF v2.13/A-21 designates the single
# pooled PLS-SEM model as the estimator of record for H7a/H7b.)
SEC_G = "G. OLS Hayes PROCESS Model 1 (SUPPLEMENTARY, not estimation of record; INTERIM, BCa 5,000, no Holm)"
o = pd.read_csv(T + "h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv")
for _, r in o.iterrows():
    if "beta_M" in r.term:
        add(SEC_G, f"{r.term} | {r.analysis}", pred="Dampening, beta_M < 0 (this OLS check's own prediction, independent of Table 9's Buffering)", n=int(r.n),
            est=f"b={r.estimate:.3f}", ci=f"[{r.bca_low:.3f}, {r.bca_high:.3f}] BCa",
            p=f"boot {r.p_boot:.3f} (no Holm adjustment)", eff=f"f2={r.f2:.4f}",
            note=f"classical p={r.p_classical:.3f}; HC3 p={r.p_HC3:.3f}; R2={r.R2:.3f}",
            verdict="CI excludes 0" if r.ci_excludes_0 else "CI includes 0 -> not supported")
    else:
        add(SEC_G, f"{r.term} | {r.analysis}", n=int(r.n), est=f"slope={r.estimate:.3f}",
            ci=f"[{r.bca_low:.3f}, {r.bca_high:.3f}] BCa", p=f"boot {r.p_boot:.3f}",
            note="conditional (base) effect, not moderation")

out = pd.DataFrame(rows)
out.to_csv(T + "FINAL_results_main_all.csv", index=False, encoding="utf-8-sig")
try:
    with pd.ExcelWriter(T + "FINAL_results_main_all.xlsx", engine="openpyxl") as w:
        out.to_excel(w, index=False, sheet_name=f"main_n{N}")
except Exception as e:  # noqa: BLE001
    print("xlsx skipped:", e)
pd.set_option("display.width", 260, "display.max_colwidth", 62, "display.max_rows", 200)
print(out[["Section", "Item", "n", "Estimate", "Stat_t_F", "CI95", "p", "EffectSize", "Verdict"]].to_string(index=False))
print(f"\n{len(out)} rows -> {T}FINAL_results_main_all.csv / .xlsx")


# --- H. Figures -------------------------------------------------------------
# Reuses the same tables already read above (`b` = plssem_bootstrap_paths_main,
# `o` = h7_ols_record_A22_A23_PROCESS_M1_INTERIM) -- no re-analysis, just plotting
# the numbers already in Sections E/G. INTERIM caveat (n < 400) applies here too.

def _star(p):
    return "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else "n.s."


def _path_label(hyp, k):
    """H-number + beta + significance star for a PLS-SEM path key `k` in `b`."""
    r = b.loc[k]
    return f"{hyp}\nb={r['Original Est.']:.3f} {_star(r['Bootstrap P Val'])}"


def figure1_structural_model():
    """Figure 1: Structural Model Diagram (SOR layout per TF SS A.1/model-figure
    legend) -- solid arrows H1-H6c, dotted arrows E1/E2, dashed arrows H7a/H7b
    moderation. Labels pull beta + significance stars from Section E (H1-H6c/E1/E2,
    PLS-SEM) and Section G (H7a/H7b, OLS Hayes PROCESS Model 1 -- H7a/H7b are
    tested via this OLS check, not the PLS-SEM path table, CLAUDE.md SS28;
    predicted Dampening, beta_M<0)."""
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(-1, 12.5)
    ax.set_ylim(-3, 6)
    ax.axis("off")

    nodes = {
        "AIP": (0.3, 3.2), "DISC": (0.3, -0.3), "REL": (3.2, 4.8),
        "INT": (3.2, 1.5), "PDPL": (3.2, -2.2), "TRU": (6.6, 3.0),
        "ENG": (9.4, 4.3), "PI": (11.6, 2.2),
    }
    for name, (x, y) in nodes.items():
        box = FancyBboxPatch((x - 0.55, y - 0.35), 1.1, 0.7,
                              boxstyle="round,pad=0.05", linewidth=1.4,
                              edgecolor="black", facecolor="#eef3fb")
        ax.add_patch(box)
        ax.text(x, y, name, ha="center", va="center", fontsize=11, fontweight="bold")

    def arrow(n1, n2, style="-", color="black", lw=1.6, curve=0.0, label=None, label_pos=0.5):
        x1, y1 = nodes[n1]
        x2, y2 = nodes[n2]
        p = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                             linestyle=style, color=color, lw=lw,
                             connectionstyle=f"arc3,rad={curve}", shrinkA=22, shrinkB=22)
        ax.add_patch(p)
        if label:
            lx, ly = x1 + (x2 - x1) * label_pos, y1 + (y2 - y1) * label_pos
            ax.text(lx, ly, label, ha="center", va="center", fontsize=8,
                     bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))

    # H1-H6c: solid hypothesised structural paths
    arrow("AIP", "REL", label=_path_label("H1", "AIP  ->  REL"))
    arrow("AIP", "INT", curve=-0.15, label=_path_label("H2", "AIP  ->  INT"), label_pos=0.35)
    arrow("REL", "TRU", label=_path_label("H4", "REL  ->  TRU"))
    arrow("REL", "ENG", curve=0.15, label=_path_label("H5", "REL  ->  ENG"))
    arrow("INT", "TRU", label=_path_label("H6a", "INT  ->  TRU"), label_pos=0.4)
    arrow("INT", "ENG", curve=-0.2, label=_path_label("H6b", "INT  ->  ENG"), label_pos=0.35)
    arrow("INT", "PI", curve=-0.3, label=_path_label("H6c", "INT  ->  PI"), label_pos=0.25)
    # E1/E2: dotted established paths
    arrow("TRU", "ENG", style=":", color="dimgray", label=_path_label("E1", "TRU  ->  ENG"))
    arrow("ENG", "PI", style=":", color="dimgray", label=_path_label("E2", "ENG  ->  PI"))
    # Specification terms (thin, unlabeled-hypothesis, still annotated)
    arrow("DISC", "INT", style="-.", color="gray", lw=1.0,
          label=_path_label("spec.", "DISC  ->  INT"), label_pos=0.3)

    # H7a/H7b moderation, dashed, pointing at the INT->TRU path. Source is the
    # OLS Hayes PROCESS Model 1 table (o, Section G) -- H7a/H7b are tested via
    # this OLS check, not the PLS-SEM path table (Khai's instruction,
    # 2026-09-24, CLAUDE.md SS28); predicted direction is Dampening, beta_M<0.
    mid_x, mid_y = (nodes["INT"][0] + nodes["TRU"][0]) / 2, (nodes["INT"][1] + nodes["TRU"][1]) / 2
    p_a = FancyArrowPatch(nodes["PDPL"], (mid_x, mid_y), arrowstyle="-|>", mutation_scale=14,
                           linestyle="--", color="#b03a2e", lw=1.6,
                           connectionstyle="arc3,rad=0.15", shrinkA=20, shrinkB=4)
    p_b = FancyArrowPatch(nodes["DISC"], (mid_x, mid_y), arrowstyle="-|>", mutation_scale=14,
                           linestyle="--", color="#1f618d", lw=1.6,
                           connectionstyle="arc3,rad=-0.15", shrinkA=20, shrinkB=4)
    ax.add_patch(p_a)
    ax.add_patch(p_b)
    row_a = o[(o.analysis.str.startswith("all N")) & (o.term.str.contains("H7a"))].iloc[0]
    row_b = o[(o.analysis.str.startswith("all N")) & (o.term.str.contains("H7b"))].iloc[0]
    ax.text(nodes["PDPL"][0] + 1.7, nodes["PDPL"][1] + 0.9,
            f"H7a (Dampening, OLS Hayes)\nb={row_a.estimate:.3f} {_star(row_a.p_boot)}",
            fontsize=8, color="#b03a2e",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    ax.text(nodes["DISC"][0] + 2.2, nodes["DISC"][1] - 0.9,
            f"H7b (Dampening, OLS Hayes)\nb={row_b.estimate:.3f} {_star(row_b.p_boot)}",
            fontsize=8, color="#1f618d",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))

    ax.text(0.3, 5.6, "Stimulus (S)", fontsize=9, style="italic", color="gray")
    ax.text(3.2, 5.6, "Organism (O)", fontsize=9, style="italic", color="gray")
    ax.text(10.5, 5.6, "Response (R)", fontsize=9, style="italic", color="gray")
    ax.text(0.3, -3.0,
            "Solid = H1-H6c (structural)   Dotted = E1/E2 (established)   "
            "Dash-dot = specification term   Dashed = H7a/H7b moderation\n"
            f"n={N} (sample_role=main, INTERIM -- below N_main=400 stopping rule, TF SS C.2.2)",
            fontsize=8, color="dimgray")
    ax.set_title("Figure 1. Structural Model Diagram (PLS-SEM for H1-H6c/E1/E2; H7a/H7b via OLS Hayes PROCESS Model 1)",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(F + "Figure1_structural_model_main.png", dpi=200)
    plt.close(fig)
    print(f"-> {F}Figure1_structural_model_main.png")


def figure2_interaction_plot():
    """Figure 2: Interaction Plot -- simple slopes of INT->TRU at 3 levels of
    PDPL Awareness (H7a only, per Khai's 2026-09-23 request: single panel, the
    Johnson-Neyman plot and the H7b panel that were here before are dropped from
    this figure). The 3 PDPL levels (-1SD, Mean, +1SD) match Table 14's simple
    slopes exactly -- refit here with the SAME H7a Hayes PROCESS Model 1
    specification as 09_h7_ols_record.R (not re-reading its CSV, which only
    stores point estimates, not a full predicted-value grid across INT)."""
    d = main.copy()
    d["INT_c"] = d.INT_mean - d.INT_mean.mean()
    d["PDPL_c"] = d.PDPL_mean - d.PDPL_mean.mean()

    m_a = smf.ols("TRU_mean ~ REL_mean + DISC_COND + INT_c * PDPL_c", data=d).fit()

    int_grid = np.linspace(d.INT_mean.min(), d.INT_mean.max(), 50)
    int_c_grid = int_grid - d.INT_mean.mean()
    sd_pdpl = d.PDPL_mean.std()

    fig, ax = plt.subplots(figsize=(7, 5.5))
    for pdpl_c, lbl, color in [(-sd_pdpl, "PDPL -1SD", "#2471a3"),
                                (0, "PDPL Mean", "#7d3c98"),
                                (sd_pdpl, "PDPL +1SD", "#b03a2e")]:
        pred = pd.DataFrame({"REL_mean": d.REL_mean.mean(), "DISC_COND": d.DISC_COND.mean(),
                              "INT_c": int_c_grid, "PDPL_c": pdpl_c})
        yhat = m_a.predict(pred)
        ax.plot(int_grid, yhat, label=lbl, color=color, lw=2)
    ax.set_title(f"Interaction Plot (Simple Slopes): H7a\nINT -> TRU moderated by PDPL Awareness (n={N}, INTERIM)")
    ax.set_xlabel("Perceived Intrusiveness (INT)")
    ax.set_ylabel("Predicted Consumer Trust (TRU)")
    ax.legend(frameon=False, title="Moderator level (PDPL)")
    fig.tight_layout()
    fig.savefig(F + "Figure2_interaction_plot_main.png", dpi=200)
    plt.close(fig)
    print(f"-> {F}Figure2_interaction_plot_main.png")


figure1_structural_model()
figure2_interaction_plot()


# --- Manuscript-ready Result tables (Table 1-14), requested 2026-09-23 ------
# Each function reads existing outputs only (same tables Sections A-H already
# read, plus plssem_rsquared/q2predict_main.csv and
# h7_heteroscedasticity_diagnostics.csv, both new outputs of the same day's
# 07_plssem_bridge.R / 09_h7_ols_record.R updates) and writes one clean,
# manuscript-formatted CSV per table. All 14 are also bundled into one
# Manuscript_Results_Tables.xlsx (one sheet per table) at the end for
# convenience. INTERIM caveat (n < 400) applies to every one of these.

_VAR_LABEL = {"AGE_BAND": "Age group", "GEN": "Gender", "EDU": "Education",
              "INC": "Monthly income", "FREQ": "Online shopping frequency",
              "PLAT": "Most-used platform", "PRIOR": "Platform tenure",
              "LOC": "Area of residence"}


def table2_demographic_profile():
    """Table 2 (renumbered 2026-09-23 from Table 1 -- Khai's revised table list
    starts the manuscript's data tables at 2): Demographic Profile of
    Respondents. REF is excluded (team recruitment bookkeeping -- which
    member's invite link a respondent came through -- not a respondent
    demographic). LOC's 1/2/3 labels were supplied directly by Khai; its
    5="Khac/Other" is inferred from the Codebook's own "LOC_5_TEXT carries the
    free-text 'other' answer" note, the same pattern PLAT already uses -- see
    _config.py::DEMOGRAPHIC_VALUE_LABELS for the exact provenance of each LOC
    code. Any code without a label here (would only happen for a not-yet-seen
    LOC value) prints as "code N (unlabeled)" rather than being silently
    dropped. Cross-checked against Master Codebook v2.7/A-20 SS4.8 directly --
    every category here is transcribed from that table, nothing invented."""
    sp = pd.read_csv(T + "main_sample_profile.csv")
    rows = []
    for var, labels in DEMOGRAPHIC_VALUE_LABELS.items():
        sub = sp[(sp.variable == var) & sp.value.notna()]
        for _, r in sub.iterrows():
            code = int(r.value)
            rows.append({"Demographic variable": _VAR_LABEL.get(var, var),
                         "Category": labels.get(code, f"code {code} (unlabeled)"),
                         "Frequency": int(r.n), "%": r.pct})
    out = pd.DataFrame(rows)
    out.to_csv(T + "Table2_demographic_profile.csv", index=False)
    return out


_LOC_OTHER_ALIASES = {
    # Merge only exact respondent-text duplicates that differ by whitespace,
    # case, or an alternate Vietnamese diacritic for the same place name --
    # verified by inspecting the raw LOC_5_TEXT values directly, not guessed.
    "an giang": "An Giang", "tây ninh": "Tây Ninh", "đăk lăk": "Đắk Lắk",
}


def table2b_loc_other_breakdown():
    """Supplementary to Table 2 (after Khai asked to see the LOC=5
    "Khac/Other" respondents broken out by actual city): tallies the free-text
    LOC_5_TEXT answers. Normalizes only 3 confirmed exact-duplicate variants
    (a trailing-space "An Giang ", a lowercase "Tây ninh", and the
    alternate-diacritic spelling "Đăk Lăk" for "Đắk Lắk") -- every other answer
    is kept verbatim, including non-city answers ("Prefer not to say") and
    overseas answers (Wollongong, L.A), since folding those into a "city" bucket
    would misrepresent what the respondent actually wrote."""
    d = main[main.LOC == 5]["LOC_5_TEXT"]

    def norm(v):
        if pd.isna(v):
            return "(missing free text)"
        s = v.strip()
        return _LOC_OTHER_ALIASES.get(s.lower(), s)

    vc = d.apply(norm).value_counts()
    out = vc.reset_index()
    out.columns = ["City / free-text answer (LOC_5_TEXT)", "Frequency"]
    out["% of LOC=5 (Khac/Other)"] = round(100 * out["Frequency"] / len(d), 1)
    out.to_csv(T + "Table2b_LOC_other_breakdown.csv", index=False)
    return out


def table3_cell_distribution():
    """Table 3 (was Table 2): Cell Distribution and Randomization Check across
    the 2x2 design. Randomization check = chi-square goodness-of-fit against an
    equal-25%-per-cell null (Qualtrics Randomizer's "Evenly Present Elements"
    target)."""
    cb = pd.read_csv(T + "main_cell_balance.csv")
    cb = cb.copy()
    cb["Cell"] = cb.apply(lambda r: f"AIP={'High' if r.AIP_COND == 1 else 'Low'} "
                                     f"x DISC={'With' if r.DISC_COND == 1 else 'No'}", axis=1)
    chi2, p = chisquare(cb["n"])
    out = cb[["Cell", "n", "pct", "flag_underfilled"]].rename(
        columns={"n": "Frequency", "pct": "%", "flag_underfilled": "Underfilled (<20% of even share)"})
    out["chi2 (equal-distribution H0)"] = round(chi2, 3)
    out["p (randomization check)"] = round(p, 4)
    out.to_csv(T + "Table3_cell_distribution_2x2.csv", index=False)
    return out


def table4_manipulation_check():
    """Table 4 (was Table 3): Manipulation Check Results (MC_AIP by AIP_COND,
    MC_DISC by DISC_COND -- Welch's t, Cohen's d, ITT/report-only per
    CLAUDE.md SS6.1). AIP_COND/DISC_COND coded 0=Low/No, 1=High/With per
    Master Codebook SS -- confirmed against `_config.py` (AIP_COND_COL,
    DISC_COL), not re-derived here."""
    mc = pd.read_csv(T + "pilot_manipulation_check_main.csv")
    out = mc.rename(columns={
        "mc_column": "Check", "group_col": "Comparison", "n_low_or_no": "n (Low/No)",
        "n_high_or_with": "n (High/With)", "mean_low_or_no": "Mean (Low/No)",
        "mean_high_or_with": "Mean (High/With)", "cohens_d": "Cohen's d"})
    out["Result"] = np.where(out["gate_pass_d>=0.50"], "PASS (|d| >= 0.50)", "FAIL")
    out = out.drop(columns=["gate_pass_d>=0.50"])
    out.to_csv(T + "Table4_manipulation_check.csv", index=False)
    return out


def table5_reliability_validity():
    """Table 5 (was Table 4): Construct Reliability and Validity -- item
    loadings + outer VIF merged with construct-level alpha/rhoA/CR/AVE in one
    table, styled after the reference "Table 2" layout Khai supplied (An & Ngo):
    construct-level statistics (alpha, CR) are printed ONCE per construct, on
    its first item row, and left blank on the item rows below it, rather than
    repeated on every row. rho_A and AVE are kept as extra columns beyond that
    reference table's own columns, since TF's own reliability thresholds
    (CLAUDE.md SS on pilot/main loading cutoffs) require both and dropping them
    would lose information the reference table's source paper didn't need to
    report. Outer VIF is per-item (every row), matching the reference table's
    own per-item VIF column. **The "Item" column shows the item CODE plus its
    full English wording** (e.g. `AIP1: "ShopWave can analyze my consumption
    level."`), matching the reference table's own Items column (a quoted
    statement, not a bare code) -- wording transcribed verbatim from Master
    Codebook v2.7/A-20 into `_config.py::ITEM_WORDING_EN`."""
    load = pd.read_csv(T + "plssem_outer_loadings_main.csv", index_col=0)
    rel = pd.read_csv(T + "plssem_reliability_main.csv", index_col=0)
    ovif = pd.read_csv(T + "plssem_outer_vif_main.csv").set_index(["construct", "item"])
    rows = []
    for cons, items in CONSTRUCT_ITEMS.items():
        if cons not in rel.index or cons == "DISC":
            continue  # DISC is a 0/1 dummy, never a reliability/loadings table (CLAUDE.md SS0)
        r = rel.loc[cons]
        for i, it in enumerate(items):
            loading = load.loc[it, cons] if it in load.index else np.nan
            ovif_val = ovif.loc[(cons, it), "vif"] if (cons, it) in ovif.index else np.nan
            first = i == 0
            wording = ITEM_WORDING_EN.get(it)
            item_label = f'{it}: "{wording}"' if wording else it
            rows.append({"Construct": cons if first else "", "Item": item_label,
                         "Loading": round(loading, 3),
                         "Cronbach's alpha": round(r.alpha, 3) if first else "",
                         "rho_A": round(r.rhoA, 3) if first else "",
                         "CR (rho_C)": round(r.rhoC, 3) if first else "",
                         "AVE": round(r.AVE, 3) if first else "",
                         "Outer VIF": round(ovif_val, 3) if pd.notna(ovif_val) else np.nan})
    out = pd.DataFrame(rows)
    out.to_csv(T + "Table5_reliability_validity.csv", index=False)
    return out


def table6_fornell_larcker():
    """Table 6 (was Table 5): Discriminant Validity - Fornell-Larcker
    Criterion."""
    out = pd.read_csv(T + "plssem_fornell_larcker_main.csv", index_col=0).round(3)
    out.to_csv(T + "Table6_fornell_larcker.csv")
    return out


def table7_htmt():
    """Table 7 (was Table 6): Discriminant Validity - HTMT Ratio."""
    out = pd.read_csv(T + "plssem_htmt_main.csv", index_col=0).round(3)
    out.to_csv(T + "Table7_htmt.csv")
    return out


def table8_inner_vif():
    """Table 8 (was Table 7): Inner VIF Values Among Latent Variables --
    reformatted (2026-09-23) as a predictor x outcome MATRIX to match the
    reference "Table 6" layout Khai supplied (An & Ngo), instead of the earlier
    long (to, from, vif) format. Rows = every construct that predicts at least
    one endogenous construct in this model (AIP, REL, INT, PDPL, DISC, TRU,
    ENG, plus the two interaction terms); columns = the 5 endogenous
    constructs (REL, INT, TRU, ENG, PI). A blank cell means that predictor
    does not appear in that outcome's own structural equation (not a missing
    value) -- e.g. REL only predicts TRU and ENG, so its INT/PI/REL columns
    are blank, matching how the reference table leaves non-applicable cells
    empty rather than 0 or NaN."""
    v = pd.read_csv(T + "plssem_inner_vif_main.csv")
    v = v.loc[:, [c for c in v.columns if not c.startswith("Unnamed")]]
    v = v.dropna(subset=["vif"]).copy()
    piv = v.pivot(index="from", columns="to", values="vif").round(3)
    endogenous_order = [c for c in ["REL", "INT", "TRU", "ENG", "PI"] if c in piv.columns]
    piv = piv[endogenous_order]
    piv.index.name = "Predictor \\ Outcome"
    piv.to_csv(T + "Table8_inner_vif.csv")
    return piv


def table9_path_coefficients():
    """Table 9 (was Table 8): Path Coefficients and Hypothesis Testing --
    beta, SE (bootstrap SD), t, p, 95% bootstrap CI, f2, decision. Same
    beta/p/CI/f2 numbers as Section E above, reformatted into one clean
    manuscript table with an explicit Decision column. **H7a/H7b are
    deliberately NOT included here** (removed 2026-09-24, Khai's explicit
    instruction): H7a/H7b are tested via the OLS Hayes PROCESS Model 1 check
    (Table 13), predicted Dampening (beta_M < 0) -- not via this PLS-SEM path
    table. See CLAUDE.md SS28."""
    hyp_labels = {
        "AIP  ->  REL": "H1", "AIP  ->  INT": "H2", "REL  ->  TRU": "H4", "REL  ->  ENG": "H5",
        "INT  ->  TRU": "H6a", "INT  ->  ENG": "H6b", "INT  ->  PI": "H6c",
        "TRU  ->  ENG": "E1", "ENG  ->  PI": "E2",
    }
    pred_sign = {"H1": "+", "H2": "+", "H4": "+", "H5": "+", "H6a": "-", "H6b": "-", "H6c": "-"}
    rows = []
    for k, hyp in hyp_labels.items():
        r = b.loc[k]
        a_, t_ = [x.strip() for x in k.split("->")]
        fv = f2.loc[a_, t_]
        p = r["Bootstrap P Val"]
        sig = p < .05
        beta = r["Original Est."]
        if hyp in pred_sign:
            sgn_ok = (pred_sign[hyp] == "+" and beta > 0) or (pred_sign[hyp] == "-" and beta < 0)
            decision = "Supported" if sig and sgn_ok else ("Significant, opposite sign" if sig else "Not supported")
        else:
            decision = "Significant (established path)" if sig else "Not significant (established path)"
        rows.append({"Hypothesis": hyp, "Path": k.replace("  ", " "), "beta": round(beta, 3),
                     "SE": round(r["Bootstrap SD"], 3), "t": round(r["T Stat."], 3),
                     "p": p, "95% CI low": round(r["2.5% CI"], 3), "95% CI high": round(r["97.5% CI"], 3),
                     "f2": round(fv, 3) if pd.notna(fv) else np.nan, "Decision": decision})
    out = pd.DataFrame(rows)
    out.to_csv(T + "Table9_path_coefficients.csv", index=False)
    return out


def table10_r2_q2predict():
    """Table 10 (was Table 9): R^2 and Q2predict for Endogenous Constructs
    (Shmueli et al. 2019 PLSpredict, 10-fold x 10-rep, seed 123 -- see
    07_plssem_bridge.R)."""
    r2 = pd.read_csv(T + "plssem_rsquared_main.csv")
    q2 = pd.read_csv(T + "plssem_q2predict_main.csv")
    out = r2.merge(q2, on="construct")[["construct", "R2", "AdjR2", "Q2predict", "predictive_power"]]
    out = out.round({"R2": 3, "AdjR2": 3, "Q2predict": 3})
    out = out.rename(columns={"construct": "Construct", "AdjR2": "Adjusted R2",
                              "predictive_power": "Predictive power (PLS vs. LM benchmark)"})
    out.to_csv(T + "Table10_r2_q2predict.csv", index=False)
    return out


def table11_indirect_effects():
    """Table 11 (was Table 10): Specific Indirect Effects (mediation test,
    percentile bootstrap CI on the same 10,000 resamples as Table 9) --
    includes INT->TRU->ENG, REL->TRU->ENG, and the extended set (through ENG
    only, and the 3-step serial chains through TRU then ENG)."""
    ie = pd.read_csv(T + "plssem_indirect_effects_main.csv")
    out = ie.rename(columns={"effect": "Indirect path", "estimate": "beta", "ci_low": "95% CI low",
                              "ci_high": "95% CI high", "p_boot": "p", "classification": "Mediation type"})
    out.to_csv(T + "Table11_indirect_effects.csv", index=False)
    return out


def table12_heteroscedasticity():
    """Table 12 (was Table 11): Heteroscedasticity Diagnostics (Breusch-Pagan;
    White = bptest() with fitted + fitted^2 auxiliary regressors) for the
    H7a/H7b OLS models, both the all-N and Cook's-D-trimmed sensitivity runs."""
    het = pd.read_csv(T + "h7_heteroscedasticity_diagnostics.csv")
    out = het.rename(columns={"bp_stat": "Breusch-Pagan LM", "bp_df": "BP df", "bp_p": "BP p",
                              "white_stat": "White LM", "white_df": "White df", "white_p": "White p"})
    out.to_csv(T + "Table12_heteroscedasticity.csv", index=False)
    return out


def table13_moderation_results():
    """Table 13 (was Table 12): Moderation Results -- INT x PDPL -> TRU (H7a)
    and INT x DISC -> TRU (H7b): b, HC3 SE, bootstrap CI, p (both bootstrap
    and HC3), from the Hayes PROCESS Model 1 SUPPLEMENTARY sensitivity check
    (09_h7_ols_record.R). NOT the estimation of record -- TF v2.13/A-21
    designates the single pooled PLS-SEM model (Table 9) as the estimator of
    record for H7a/H7b; kept running unchanged per Khai's instruction,
    2026-09-24, see CLAUDE.md SS26."""
    o2 = pd.read_csv(T + "h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv")
    mod = o2[o2.term.str.contains("beta_M")].copy()
    mod = mod.rename(columns={"term": "Hypothesis term", "analysis": "Sample", "estimate": "b",
                              "bca_low": "95% CI low (BCa)", "bca_high": "95% CI high (BCa)",
                              "p_boot": "p (bootstrap)", "SE_HC3": "SE (HC3)", "p_HC3": "p (HC3)"})
    out = mod[["Hypothesis term", "Sample", "n", "b", "SE (HC3)", "95% CI low (BCa)",
              "95% CI high (BCa)", "p (bootstrap)", "p (HC3)", "f2"]]
    out.to_csv(T + "Table13_moderation_results.csv", index=False)
    return out


def table14_sensitivity_check():
    """Table 14 (was Table 13): Sensitivity Check -- Full Sample vs. Cook's
    D-Trimmed Sample, for both H7a and H7b's beta_M term, side by side.
    Part of the supplementary OLS check (Table 13), not the PLS-SEM
    estimation of record (Table 9) -- CLAUDE.md SS26."""
    o2 = pd.read_csv(T + "h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv")
    mod = o2[o2.term.str.contains("beta_M")].copy()
    mod["analysis"] = mod["analysis"].replace({
        "all N (conclusions rest on this)": "Full sample",
        "without Cook's-D-flagged cases (sensitivity)": "Cook's D-trimmed"})
    piv = mod.pivot(index="term",
                     columns="analysis",
                     values=["n", "estimate", "bca_low", "bca_high", "p_boot", "ci_excludes_0"])
    piv.columns = [f"{stat} ({sample})" for stat, sample in piv.columns]
    piv = piv.reset_index().rename(columns={"term": "Hypothesis term"})
    piv.to_csv(T + "Table14_sensitivity_full_vs_trimmed.csv", index=False)
    return piv


def table15_simple_slopes():
    """Table 15 (was Table 14): Conditional Effects / Simple Slopes of
    INT->TRU at 3 levels of PDPL (-1SD, Mean, +1SD) -- H7a only; DISC has no
    third "mean" level distinct from its two natural categories, so it stays
    a 2-level comparison in Table 13. Part of the supplementary OLS check,
    not the PLS-SEM estimation of record (Table 9) -- CLAUDE.md SS26."""
    o2 = pd.read_csv(T + "h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv")
    slopes = o2[o2.term.str.contains("slope INT->TRU PDPL")].copy()
    slopes["analysis"] = slopes["analysis"].replace({
        "all N (conclusions rest on this)": "Full sample",
        "without Cook's-D-flagged cases (sensitivity)": "Cook's D-trimmed"})
    out = slopes.rename(columns={"term": "Conditional effect", "analysis": "Sample",
                                 "estimate": "Simple slope (b)", "bca_low": "95% CI low (BCa)",
                                 "bca_high": "95% CI high (BCa)", "p_boot": "p"})
    out = out[["Conditional effect", "Sample", "n", "Simple slope (b)",
              "95% CI low (BCa)", "95% CI high (BCa)", "p"]]
    out.to_csv(T + "Table15_simple_slopes_PDPL.csv", index=False)
    return out


_manuscript_tables = [
    ("Table2", table2_demographic_profile), ("Table2b", table2b_loc_other_breakdown),
    ("Table3", table3_cell_distribution),
    ("Table4", table4_manipulation_check), ("Table5", table5_reliability_validity),
    ("Table6", table6_fornell_larcker), ("Table7", table7_htmt),
    ("Table8", table8_inner_vif), ("Table9", table9_path_coefficients),
    ("Table10", table10_r2_q2predict), ("Table11", table11_indirect_effects),
    ("Table12", table12_heteroscedasticity), ("Table13", table13_moderation_results),
    ("Table14", table14_sensitivity_check), ("Table15", table15_simple_slopes),
]

_MATRIX_TABLES = ("Table6", "Table7", "Table8")  # constructs/predictors are the index

_built = {}
for _name, _fn in _manuscript_tables:
    try:
        _built[_name] = _fn()
        print(f"-> {T}{_name}_*.csv")
    except Exception as e:  # noqa: BLE001
        print(f"!! {_name} ({_fn.__name__}) failed: {e}")

try:
    with pd.ExcelWriter(T + "Manuscript_Results_Tables.xlsx", engine="openpyxl") as w:
        for _name, _df in _built.items():
            _df.to_excel(w, sheet_name=_name, index=(_name in _MATRIX_TABLES))
    print(f"-> {T}Manuscript_Results_Tables.xlsx ({len(_built)}/{len(_manuscript_tables)} sheets)")
except Exception as e:  # noqa: BLE001
    print("Manuscript_Results_Tables.xlsx skipped:", e)
