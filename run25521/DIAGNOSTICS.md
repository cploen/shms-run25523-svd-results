# Run 25521 diagnostics: choose a foil, then a delta slice

The original summary PDFs combine foils. **Use the links below for the actual foil-by-foil inspection.** Each foil report contains six delta slices, in increasing delta order; its PDF bookmarks select a slice. Each slice has five pages, described below.

All views use the identical 73,188 fitted events (24,396 per foil), with matching old/new matrix inputs. There has been no refit or change to any matrix.

## One report per foil

| Method | Foil label / z | Old matrix (30 pages) | New matrix (30 pages) |
|---|---|---|---|
| Unweighted legacy fit | 0 / +10 cm | [Old foil 0](unweighted/plots/old/foil_0_z_plus10/all_delta_slices.pdf) | [New foil 0](unweighted/plots/new/foil_0_z_plus10/all_delta_slices.pdf) |
| Unweighted legacy fit | 1 / +0 cm | [Old foil 1](unweighted/plots/old/foil_1_z_0/all_delta_slices.pdf) | [New foil 1](unweighted/plots/new/foil_1_z_0/all_delta_slices.pdf) |
| Unweighted legacy fit | 2 / -10 cm | [Old foil 2](unweighted/plots/old/foil_2_z_minus10/all_delta_slices.pdf) | [New foil 2](unweighted/plots/new/foil_2_z_minus10/all_delta_slices.pdf) |
| Supplied weights | 0 / +10 cm | [Old foil 0](weighted/plots/old/foil_0_z_plus10/all_delta_slices.pdf) | [New foil 0](weighted/plots/new/foil_0_z_plus10/all_delta_slices.pdf) |
| Supplied weights | 1 / +0 cm | [Old foil 1](weighted/plots/old/foil_1_z_0/all_delta_slices.pdf) | [New foil 1](weighted/plots/new/foil_1_z_0/all_delta_slices.pdf) |
| Supplied weights | 2 / -10 cm | [Old foil 2](weighted/plots/old/foil_2_z_minus10/all_delta_slices.pdf) | [New foil 2](weighted/plots/new/foil_2_z_minus10/all_delta_slices.pdf) |

## What is on each slice’s five pages?

1. Full xptar, ytar and yptar residual distributions, plus residual-versus-target 2D histograms. Counts, mean, RMS and RMSE are printed; tail counts outside the plotted range are explicit.
2. Xptar residual distributions for every x-sieve column (11 panels).
3. Yptar residual distributions for every y-sieve column (11 panels).
4. Ytar residual distributions for every y-sieve column (11 panels).
5. Reconstructed sieve pattern with occupied target holes marked, and each residual versus delta within that slice.

Residuals are reconstructed minus geometric target; slopes are mrad and ytar is cm. These displays use raw residuals with **no historical ±0.035 cm plotting shifts**. All statistics include tails. Empty sieve columns are explicitly marked, and no Gaussian fit conceals a second population. Old/new use the same axis limits. These are event-count histograms for both methods, as in the legacy diagnostics.

The new displays restore the distributions that were disabled or not written by the existing macros. They supplement the original legacy PDFs, which are preserved. The old/new comparison evaluates the respective matrix at the same geometric xtar; the reconstructed sieve is xtar+253*xptar and ytar+253*yptar+hb(delta). This is not a fresh iterative HCANA replay.

## Direct links to individual delta slices

The first slice retains the native strict lower cut delta > −15%; subsequent lower edges are inclusive. Upper edges are exclusive. Counts below are identical for both cases and both old/new views.

### Foil 0: z = +10 cm

| Delta (%) | Events | Unweighted old | Unweighted new | Supplied weights old | Supplied weights new |
|---|---:|---|---|---|---|
| -15 < δ < -6 | 6,684 | [PDF](unweighted/plots/old/foil_0_z_plus10/delta_00_minus15_to_minus6.pdf) | [PDF](unweighted/plots/new/foil_0_z_plus10/delta_00_minus15_to_minus6.pdf) | [PDF](weighted/plots/old/foil_0_z_plus10/delta_00_minus15_to_minus6.pdf) | [PDF](weighted/plots/new/foil_0_z_plus10/delta_00_minus15_to_minus6.pdf) |
| -6 ≤ δ < -2 | 5,211 | [PDF](unweighted/plots/old/foil_0_z_plus10/delta_01_minus6_to_minus2.pdf) | [PDF](unweighted/plots/new/foil_0_z_plus10/delta_01_minus6_to_minus2.pdf) | [PDF](weighted/plots/old/foil_0_z_plus10/delta_01_minus6_to_minus2.pdf) | [PDF](weighted/plots/new/foil_0_z_plus10/delta_01_minus6_to_minus2.pdf) |
| -2 ≤ δ < 2 | 4,564 | [PDF](unweighted/plots/old/foil_0_z_plus10/delta_02_minus2_to_plus2.pdf) | [PDF](unweighted/plots/new/foil_0_z_plus10/delta_02_minus2_to_plus2.pdf) | [PDF](weighted/plots/old/foil_0_z_plus10/delta_02_minus2_to_plus2.pdf) | [PDF](weighted/plots/new/foil_0_z_plus10/delta_02_minus2_to_plus2.pdf) |
| 2 ≤ δ < 6 | 3,400 | [PDF](unweighted/plots/old/foil_0_z_plus10/delta_03_plus2_to_plus6.pdf) | [PDF](unweighted/plots/new/foil_0_z_plus10/delta_03_plus2_to_plus6.pdf) | [PDF](weighted/plots/old/foil_0_z_plus10/delta_03_plus2_to_plus6.pdf) | [PDF](weighted/plots/new/foil_0_z_plus10/delta_03_plus2_to_plus6.pdf) |
| 6 ≤ δ < 10 | 2,390 | [PDF](unweighted/plots/old/foil_0_z_plus10/delta_04_plus6_to_plus10.pdf) | [PDF](unweighted/plots/new/foil_0_z_plus10/delta_04_plus6_to_plus10.pdf) | [PDF](weighted/plots/old/foil_0_z_plus10/delta_04_plus6_to_plus10.pdf) | [PDF](weighted/plots/new/foil_0_z_plus10/delta_04_plus6_to_plus10.pdf) |
| 10 ≤ δ < 22 | 2,147 | [PDF](unweighted/plots/old/foil_0_z_plus10/delta_05_plus10_to_plus22.pdf) | [PDF](unweighted/plots/new/foil_0_z_plus10/delta_05_plus10_to_plus22.pdf) | [PDF](weighted/plots/old/foil_0_z_plus10/delta_05_plus10_to_plus22.pdf) | [PDF](weighted/plots/new/foil_0_z_plus10/delta_05_plus10_to_plus22.pdf) |

### Foil 1: z = +0 cm

| Delta (%) | Events | Unweighted old | Unweighted new | Supplied weights old | Supplied weights new |
|---|---:|---|---|---|---|
| -15 < δ < -6 | 6,899 | [PDF](unweighted/plots/old/foil_1_z_0/delta_00_minus15_to_minus6.pdf) | [PDF](unweighted/plots/new/foil_1_z_0/delta_00_minus15_to_minus6.pdf) | [PDF](weighted/plots/old/foil_1_z_0/delta_00_minus15_to_minus6.pdf) | [PDF](weighted/plots/new/foil_1_z_0/delta_00_minus15_to_minus6.pdf) |
| -6 ≤ δ < -2 | 5,513 | [PDF](unweighted/plots/old/foil_1_z_0/delta_01_minus6_to_minus2.pdf) | [PDF](unweighted/plots/new/foil_1_z_0/delta_01_minus6_to_minus2.pdf) | [PDF](weighted/plots/old/foil_1_z_0/delta_01_minus6_to_minus2.pdf) | [PDF](weighted/plots/new/foil_1_z_0/delta_01_minus6_to_minus2.pdf) |
| -2 ≤ δ < 2 | 4,199 | [PDF](unweighted/plots/old/foil_1_z_0/delta_02_minus2_to_plus2.pdf) | [PDF](unweighted/plots/new/foil_1_z_0/delta_02_minus2_to_plus2.pdf) | [PDF](weighted/plots/old/foil_1_z_0/delta_02_minus2_to_plus2.pdf) | [PDF](weighted/plots/new/foil_1_z_0/delta_02_minus2_to_plus2.pdf) |
| 2 ≤ δ < 6 | 3,149 | [PDF](unweighted/plots/old/foil_1_z_0/delta_03_plus2_to_plus6.pdf) | [PDF](unweighted/plots/new/foil_1_z_0/delta_03_plus2_to_plus6.pdf) | [PDF](weighted/plots/old/foil_1_z_0/delta_03_plus2_to_plus6.pdf) | [PDF](weighted/plots/new/foil_1_z_0/delta_03_plus2_to_plus6.pdf) |
| 6 ≤ δ < 10 | 2,095 | [PDF](unweighted/plots/old/foil_1_z_0/delta_04_plus6_to_plus10.pdf) | [PDF](unweighted/plots/new/foil_1_z_0/delta_04_plus6_to_plus10.pdf) | [PDF](weighted/plots/old/foil_1_z_0/delta_04_plus6_to_plus10.pdf) | [PDF](weighted/plots/new/foil_1_z_0/delta_04_plus6_to_plus10.pdf) |
| 10 ≤ δ < 22 | 2,541 | [PDF](unweighted/plots/old/foil_1_z_0/delta_05_plus10_to_plus22.pdf) | [PDF](unweighted/plots/new/foil_1_z_0/delta_05_plus10_to_plus22.pdf) | [PDF](weighted/plots/old/foil_1_z_0/delta_05_plus10_to_plus22.pdf) | [PDF](weighted/plots/new/foil_1_z_0/delta_05_plus10_to_plus22.pdf) |

### Foil 2: z = -10 cm

| Delta (%) | Events | Unweighted old | Unweighted new | Supplied weights old | Supplied weights new |
|---|---:|---|---|---|---|
| -15 < δ < -6 | 6,948 | [PDF](unweighted/plots/old/foil_2_z_minus10/delta_00_minus15_to_minus6.pdf) | [PDF](unweighted/plots/new/foil_2_z_minus10/delta_00_minus15_to_minus6.pdf) | [PDF](weighted/plots/old/foil_2_z_minus10/delta_00_minus15_to_minus6.pdf) | [PDF](weighted/plots/new/foil_2_z_minus10/delta_00_minus15_to_minus6.pdf) |
| -6 ≤ δ < -2 | 5,294 | [PDF](unweighted/plots/old/foil_2_z_minus10/delta_01_minus6_to_minus2.pdf) | [PDF](unweighted/plots/new/foil_2_z_minus10/delta_01_minus6_to_minus2.pdf) | [PDF](weighted/plots/old/foil_2_z_minus10/delta_01_minus6_to_minus2.pdf) | [PDF](weighted/plots/new/foil_2_z_minus10/delta_01_minus6_to_minus2.pdf) |
| -2 ≤ δ < 2 | 3,551 | [PDF](unweighted/plots/old/foil_2_z_minus10/delta_02_minus2_to_plus2.pdf) | [PDF](unweighted/plots/new/foil_2_z_minus10/delta_02_minus2_to_plus2.pdf) | [PDF](weighted/plots/old/foil_2_z_minus10/delta_02_minus2_to_plus2.pdf) | [PDF](weighted/plots/new/foil_2_z_minus10/delta_02_minus2_to_plus2.pdf) |
| 2 ≤ δ < 6 | 3,207 | [PDF](unweighted/plots/old/foil_2_z_minus10/delta_03_plus2_to_plus6.pdf) | [PDF](unweighted/plots/new/foil_2_z_minus10/delta_03_plus2_to_plus6.pdf) | [PDF](weighted/plots/old/foil_2_z_minus10/delta_03_plus2_to_plus6.pdf) | [PDF](weighted/plots/new/foil_2_z_minus10/delta_03_plus2_to_plus6.pdf) |
| 6 ≤ δ < 10 | 2,414 | [PDF](unweighted/plots/old/foil_2_z_minus10/delta_04_plus6_to_plus10.pdf) | [PDF](unweighted/plots/new/foil_2_z_minus10/delta_04_plus6_to_plus10.pdf) | [PDF](weighted/plots/old/foil_2_z_minus10/delta_04_plus6_to_plus10.pdf) | [PDF](weighted/plots/new/foil_2_z_minus10/delta_04_plus6_to_plus10.pdf) |
| 10 ≤ δ < 22 | 2,982 | [PDF](unweighted/plots/old/foil_2_z_minus10/delta_05_plus10_to_plus22.pdf) | [PDF](unweighted/plots/new/foil_2_z_minus10/delta_05_plus10_to_plus22.pdf) | [PDF](weighted/plots/old/foil_2_z_minus10/delta_05_plus10_to_plus22.pdf) | [PDF](weighted/plots/new/foil_2_z_minus10/delta_05_plus10_to_plus22.pdf) |

[All foil/slice numerical metrics (CSV)](foil_slice_metrics.csv) · [Population and PDF validation](foil_slice_validation.json) · [Results and fitting details](README.md)
