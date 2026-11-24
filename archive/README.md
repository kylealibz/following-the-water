# Original project code

`prepare_tree_loss_patches.py` is preserved from the original November 2026 mapping workflow. It documents raster thresholding, GDAL polygonization, year/tile grouping, source attribution and approximate ellipsoidal area calculations used for the historical tree-cover-loss layer.

This is an archival script, not part of the portable quick start. It expects the original working-directory structure, GDAL/OGR/OSR, NumPy, saved `lossyear.npy` and `treecover2000.npy` arrays, and network access to the Hansen raster metadata. Those large source arrays are not bundled. The relative paths are historical project paths. Do not run it expecting the portable repository to contain those inputs.

The saved outputs are represented in `data/tree_loss_stats.json`. The reproducible README chart redraws those statistics. This archive preserves implementation detail without claiming that the entire original raster workflow can be reproduced from the small bundled files alone.
