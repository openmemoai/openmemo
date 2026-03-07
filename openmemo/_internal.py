"""
Internal engine parameters.

This module contains encapsulated tuning parameters
used by OpenMemo's intelligence layer. These are not
part of the public API and may change without notice.
"""


def get_evolution_params():
    return {
        "mastery_access": 5,
        "mastery_importance": 0.6,
        "consolidation_access": 2,
        "dormant_days": 30,
        "default_importance": 0.5,
    }


def get_skill_params():
    return {
        "pattern_threshold": 3,
    }


def get_pyramid_params():
    return {
        "short_term_max": 50,
        "short_term_hours": 24,
        "batch_size": 5,
    }
