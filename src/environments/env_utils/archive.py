"""
Unstructured novelty-search archive.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Tuple

import numpy as np


@dataclass(frozen=True, slots=True)
class Archive:
    """Fixed-size circular archive for state descriptors."""

    data: np.ndarray                    # shape = (max_size, descriptor_dim)
    current_position: int               # next slot to overwrite
    acceptance_threshold: float         # minimum admissible distance
    state_descriptor_size: int          # descriptor dimensionality
    max_size: int                       # capacity


    @property
    def size(self) -> int:
        """Number of *valid* descriptors currently stored."""
        mask = np.isnan(self.data).any(axis=1)  # True where row is all-NaN
        return int(np.count_nonzero(~mask))

    @classmethod
    def create(
        cls,
        acceptance_threshold: float,
        state_descriptor_size: int,
        max_size: int = 80_000,
    ) -> "Archive":
        buf = np.full((max_size, state_descriptor_size), np.nan, dtype=np.float32)
        return cls(
            data=buf,
            current_position=0,
            acceptance_threshold=acceptance_threshold,
            state_descriptor_size=state_descriptor_size,
            max_size=max_size,
        )


    def _single_insertion(self, descriptor: np.ndarray) -> "Archive":
        """Insert `descriptor` at the circular head and return a *new* archive."""
        if descriptor.shape != (self.state_descriptor_size,):
            raise ValueError(
                f"Expected descriptor shape {(self.state_descriptor_size,)}, "
                f"got {descriptor.shape}"
            )

        # Copy underlying buffer (immutability via dataclass `frozen=True`).
        new_data = self.data.copy()
        idx = self.current_position % self.max_size
        new_data[idx] = descriptor

        return replace(self, data=new_data, current_position=self.current_position + 1)

    def _conditioned_single_insertion(
        self, accept: bool, descriptor: np.ndarray
    ) -> Tuple["Archive", np.ndarray]:
        """Insert only if `accept` is True; always returns an archive and
        the actually inserted (or NaN) descriptor."""
        if accept:
            new_arch = self._single_insertion(descriptor)
            return new_arch, descriptor
        else:
            return self, np.full_like(descriptor, np.nan)


    def insert(self, state_descriptors: np.ndarray) -> "Archive":
        """Insert a batch of descriptors obeying novelty constraints."""
        state_descriptors = np.asanyarray(state_descriptors, dtype=np.float32).reshape(
            -1, self.state_descriptor_size
        )

        # The *static* part of the archive: everything currently stored
        stored_mask = ~np.isnan(self.data).any(axis=1)
        stored = self.data[stored_mask] if stored_mask.any() else np.empty(
            (0, self.state_descriptor_size), dtype=np.float32
        )

        # 1) First novelty filter: candidate vs. archive
        if stored.size:
            dists, _ = knn(stored, state_descriptors, k=1)     # (n,1)
            first_cond = dists.squeeze(1) > self.acceptance_threshold
        else:
            first_cond = np.ones(len(state_descriptors), dtype=bool)

        # 2) Sequential scan to prevent mutually-similar additions
        new_arch = self
        already_added = np.empty((0, self.state_descriptor_size), dtype=np.float32)

        for descriptor, ok1 in zip(state_descriptors, first_cond):
            if not ok1:
                continue

            # Distance to those inserted in *this* batch so far
            if already_added.size:
                d2, _ = knn(already_added, descriptor[None, :], k=1)
                ok2 = d2.item() > self.acceptance_threshold
            else:
                ok2 = True

            new_arch, inserted = new_arch._conditioned_single_insertion(ok2, descriptor)

            # keep track of descriptors we really committed
            if ok2:
                already_added = np.vstack([already_added, inserted])

        return new_arch


# --------------------------------------------------------------------------- #
#                           NOVELTY  SCORING                                  #
# --------------------------------------------------------------------------- #

def score_euclidean_novelty(
    archive: Archive,
    state_descriptors: np.ndarray,
    num_nearest_neighb: int = 15,
    scaling_ratio: float = 1.0,
) -> np.ndarray:
    """Return novelty scores for each descriptor in `state_descriptors`."""
    state_descriptors = np.asanyarray(state_descriptors, dtype=np.float32).reshape(
        -1, archive.state_descriptor_size
    )
    stored_mask = ~np.isnan(archive.data).any(axis=1)
    stored = archive.data[stored_mask]

    if not stored.size:
        return np.zeros(len(state_descriptors), dtype=np.float32)
    num_nearest_neighb = min(archive.size, num_nearest_neighb)
    
    dists, _ = knn(stored, state_descriptors, num_nearest_neighb)
    mean_sq_dist = np.mean(dists ** 2, axis=1)  # (batch,)
    return scaling_ratio * mean_sq_dist


# --------------------------------------------------------------------------- #
#                               KNN HELPER                                    #
# --------------------------------------------------------------------------- #

def knn(
    reference: np.ndarray, query: np.ndarray, k: int
) -> Tuple[np.ndarray, np.ndarray]:
    """Brute-force Euclidean k-NN (distance, indices) for each row in `query`."""
    # (q,1) + (1,r) – 2*dot → pairwise sq distances
    dist_sq = (
        np.sum(query ** 2, axis=1, keepdims=True)
        + np.sum(reference ** 2, axis=1)[None, :]
        - 2.0 * query @ reference.T
    )
    # Replace NaN rows (should not appear after masking) with +∞
    np.nan_to_num(dist_sq, copy=False, nan=np.inf)

    # For numerical reasons clip very small negatives
    dist_sq = np.clip(dist_sq, a_min=0.0, a_max=None)
    dist = np.sqrt(dist_sq)

    # Obtain k smallest distances and indices along last axis
    if k == 1:
        idx = np.argmin(dist, axis=1, keepdims=True)
        val = dist[np.arange(dist.shape[0])[:, None], idx]
    else:
        idx_part = np.argpartition(dist, kth=k - 1, axis=1)[:, :k]
        # sort the k-partition block to get exact ordering
        row_indices = np.arange(dist.shape[0])[:, None]
        vals_part = dist[row_indices, idx_part]
        order = np.argsort(vals_part, axis=1)
        idx = idx_part[row_indices, order]
        val = vals_part[row_indices, order]

    return val.astype(np.float32), idx.astype(np.int32)
