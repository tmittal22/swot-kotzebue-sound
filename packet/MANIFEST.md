# Data packet

All files are quality-controlled per `docs/THEORY.md` section 4 unless the name says otherwise.
Times are UTC. WSE is metres above the EGM2008 geoid.

| file | MB | contents |
|---|---|---|
| `chlorophyll_regional_weekly.csv` | 0.1 | VIIRS weekly chlorophyll medians for the 3 sound regions |
| `reference_long_profiles.csv` | 0.6 | per-node reference WSE long profile and its spread |
| `sword_node_inventory.csv.gz` | 0.6 | SWORD v17c node attributes for the domain |
| `sword_reach_inventory.csv` | 0.0 | SWORD v17c reach attributes for the domain |
| `swot_node_timeseries_qc.parquet` | 28.3 | 200 m node time series, quality-passed and ice-free |
| `swot_reach_timeseries_qc.csv.gz` | 0.9 | reach-level SWOT time series, quality-passed and ice-free |
| `usgs_daily.csv` | 3.0 | USGS daily discharge and stage, 1976-2026, 3 gauges |
| `usgs_instantaneous.csv.gz` | 1.9 | USGS 15-minute values 2023-2026, converted to UTC |
| `virtual_gauge_index.csv` | 0.0 | the 12 SWOT virtual gauges plotted in fig09: id, position, drainage area, record length |
