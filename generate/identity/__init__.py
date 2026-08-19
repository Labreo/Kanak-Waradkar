__all__ = [
    "VectorAIdentityGenerator",
    "VectorAFidelityScorer",
    "calculate_shannon_entropy",
    "compute_icao_check_digit",
]


def __getattr__(name: str):
    if name in ("VectorAIdentityGenerator", "calculate_shannon_entropy", "compute_icao_check_digit"):
        import generate.identity.generator as _gen
        return getattr(_gen, name)
    if name == "VectorAFidelityScorer":
        import generate.identity.score_fidelity as _fid
        return getattr(_fid, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
