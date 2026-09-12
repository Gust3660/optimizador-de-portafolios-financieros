"""Simulación Monte Carlo de carteras long-only."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PortfolioResult:
    weights: np.ndarray
    annual_returns: np.ndarray
    annual_volatility: np.ndarray
    sharpe: np.ndarray
    max_sharpe_index: int
    min_volatility_index: int
    expected_asset_returns: np.ndarray
    covariance: np.ndarray


def optimize_portfolios(
    returns: np.ndarray,
    periods_per_year: int = 12,
    risk_free_rate: float = 0.02,
    simulations: int = 10_000,
    seed: int = 42,
) -> PortfolioResult:
    values = np.asarray(returns, dtype=float)
    if values.ndim != 2 or values.shape[0] < 10 or values.shape[1] < 2:
        raise ValueError("Se requieren al menos 10 periodos y 2 activos.")
    if not np.all(np.isfinite(values)) or np.any(values <= -1):
        raise ValueError("Los rendimientos deben ser finitos y mayores que -100%.")
    if periods_per_year < 1 or simulations < 100:
        raise ValueError("Usa periodos por año positivos y al menos 100 simulaciones.")
    if not np.isfinite(risk_free_rate):
        raise ValueError("La tasa libre de riesgo debe ser finita.")

    expected = np.mean(values, axis=0) * periods_per_year
    covariance = np.atleast_2d(np.cov(values, rowvar=False)) * periods_per_year
    rng = np.random.default_rng(seed)
    weights = rng.dirichlet(np.ones(values.shape[1]), size=simulations)
    annual_returns = weights @ expected
    variance = np.einsum("ij,jk,ik->i", weights, covariance, weights)
    volatility = np.sqrt(np.maximum(variance, 0))
    sharpe = np.divide(
        annual_returns - risk_free_rate,
        volatility,
        out=np.full_like(annual_returns, -np.inf),
        where=volatility > 0,
    )
    return PortfolioResult(
        weights=weights,
        annual_returns=annual_returns,
        annual_volatility=volatility,
        sharpe=sharpe,
        max_sharpe_index=int(np.argmax(sharpe)),
        min_volatility_index=int(np.argmin(volatility)),
        expected_asset_returns=expected,
        covariance=covariance,
    )
