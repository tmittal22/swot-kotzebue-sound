"""Shared loading, quality control and plotting setup for the Kotzebue SWOT work.

Quality control policy (see docs/THEORY.md S4 for the justification):

  reach_q <= 1     Empirically justified, not assumed.  On the Kobuk reach at
                   the Kiana gauge, reach_q<=1 gives WSE spanning 2.4-6.8 m
                   (std 1.02 m), consistent with the ~4 m gauged seasonal
                   stage range.  Admitting reach_q==2 widens the span to
                   -5.2 to 11.2 m, i.e. below-sea-level and 11 m elevations on
                   a reach whose bed sits near 2 m -- physically impossible, so
                   those are retrieval failures, not extreme flows.

  ice_clim_f == 0  The climatological ice flag.  Kotzebue rivers are ice
                   covered roughly November-May; KaRIn returns off river ice
                   are not a water surface, so ice-flagged epochs are dropped
                   rather than interpreted as stage.  ice_dyn_f is unpopulated
                   (-999) throughout this record and is not used.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIGS = os.path.join(HERE, "..", "figs")

RIVER_COLORS = {"Kobuk": "#1f6f8b", "Selawik": "#c1543a",
                "Noatak": "#4f7942", "Squirrel": "#8a6fae",
                "Buckland": "#b08b2e", "Wulik": "#6b6b6b",
                "HothamInletChannel": "#2f4858"}

GAUGES = {"15744500": "Kobuk R nr Kiana",
          "15743850": "Dahl C nr Kobuk",
          "15747000": "Wulik R bl Tutak C"}

CFS_TO_CMS = 0.028316846592


def mpl_setup():
    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "savefig.bbox": "tight",
        "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
        "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "legend.fontsize": 8,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })


def load_reaches(qc=True, ice_free=True, robust=True):
    df = pd.read_parquet(f"{DATA}/swot/reach_timeseries.parquet")
    return _qc(df, qc, ice_free, "reach_q", robust, "reach_id")


def load_nodes(qc=True, ice_free=True, robust=True):
    df = pd.read_parquet(f"{DATA}/swot/node_timeseries.parquet")
    return _qc(df, qc, ice_free, "node_q", robust, "node_id")


def _qc(df, qc, ice_free, qcol, robust=True, idcol="reach_id",
        sigma_k=4.0, floor_m=3.0):
    """Quality filter.

    `robust` adds a per-feature outlier rejection on top of the product quality
    flag: a value is dropped if it lies more than `sigma_k` robust standard
    deviations from that feature's own median.  The floor of `floor_m` is set
    above the largest real seasonal stage range in the basin (~4.4 m gauged on
    the Kobuk) so genuine floods survive.  Without this, reach_q<=1 still
    admits enough spikes to give 13-20 m apparent stage ranges on rivers whose
    true range is 3-4 m.
    """
    df = df[df.wse.notna()].copy()
    if qc:
        df = df[df[qcol] <= 1]
    if ice_free:
        df = df[df.ice_clim_f == 0]
    if robust and len(df):
        g = df.groupby(idcol).wse
        med = g.transform("median")
        mad = g.transform(lambda s: (s - s.median()).abs().median())
        lim = np.maximum(floor_m, sigma_k * 1.4826 * mad.fillna(0))
        df = df[(df.wse - med).abs() <= lim]
    df["year"] = df.time.dt.year
    df["doy"] = df.time.dt.dayofyear
    return df.reset_index(drop=True)


def load_gauges(kind="daily"):
    f = "usgs_daily.parquet" if kind == "daily" else "usgs_instantaneous.parquet"
    g = pd.read_parquet(f"{DATA}/gauges/{f}")
    g["site_no"] = g.site_no.astype(str)
    if "discharge_cfs" in g:
        g["q_cms"] = g.discharge_cfs * CFS_TO_CMS
    return g


def load_inventory(what="reaches"):
    return pd.read_parquet(f"{DATA}/swot/inventory_{what}.parquet")


def nearest_reach(inv, lat, lon, river=None):
    s = inv if river is None else inv[inv.river == river]
    d = np.hypot((s.y - lat) * 111.32,
                 (s.x - lon) * 111.32 * np.cos(np.radians(lat)))
    return s.loc[d.idxmin()], d.min()
