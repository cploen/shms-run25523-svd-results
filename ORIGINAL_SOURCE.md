# Historical SHMS fitter and the single-foil limit change

The reference is `fit_opt_matrix_gmm.C` at commit **3b93f6e3a25a4078fa73bc8f46ecf8624d4d0bba**, the first SHMS-capable revision. The byte-identical reference is retained as `reference/fit_opt_matrix_gmm.C.original`.

The executable `fit_opt_matrix_gmm.C` has only two selection-limit substitutions:

- `MaxZtarPerBin=15000` becomes `MaxZtarPerBin=nfit_max_arg`.
- `Max_Per_Run_Per_Foil[nf]=30000` becomes `Max_Per_Run_Per_Foil[nf]=nfit_max_arg`.

The run passes nfit_max_arg=433019, the number of supplied rows. These remove arbitrary foil-total caps for a one-foil dataset. The original delta-by-y-sieve-column cap of 1000, delta cut, row order, basis, fixed coefficients, raw unweighted X^T X accumulation and ROOT default SVD truncation remain unchanged. There is no supplied balancing function, column rescaling, custom cutoff, external-offset subtraction or later fitter improvement in this executable. The full two-line diff is `reference/single_foil_limits.diff`.

Reference SHA256: `643ab237a3231bb3a4da573fb68ff21d3dd08ebc78588a16a1ba47eeca69512d`.
Executable SHA256: `864e58096706b55be6b5bd55b2d702137572732a5941509d078533bfa18afe43`.

The matching helper headers are unchanged exports from the same commit. The existing complete-row matrix parser was already present in that historical revision. The temporary local execution used a function-name suffix to distinguish builds; after removing that name suffix, its source is byte-identical to the published executable.

The only ROOT branch adaptation is converting ztarT from int64 to float64. All 57 original arrays retain every value and the original order of 433019 events. No weight branch is added to the unweighted input.
