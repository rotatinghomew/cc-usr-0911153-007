from __future__ import annotations

import math
from typing import Any, Callable, Mapping

from corridor_twin.events.logistics_event import DomainRecord, RuleResult, bounded, finite_number, normalized_text

RuleFunction = Callable[[DomainRecord, Mapping[str, Any]], RuleResult]

def _number(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    if not text:
        return 0.0
    try:
        return finite_number(text)
    except ValueError:
        return float(sum(ord(ch) for ch in text) % 101)

def _context_number(context: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return finite_number(context.get(key, default))
    except ValueError:
        return default

def _result(code: str, value: float, threshold: float, higher_is_better: bool, message: str, evidence: dict[str, Any]) -> RuleResult:
    distance = (value - threshold) if higher_is_better else (threshold - value)
    passed = distance >= 0
    scale = max(1.0, abs(threshold))
    score = bounded(0.5 + distance / (2.0 * scale))
    severity = 'info' if passed else ('critical' if score < 0.2 else 'error')
    return RuleResult(code, passed, score, severity, message, evidence)

def check_shipment_id_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'shipment_id')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_shipment_id_presence_threshold', 10.333)
    return _result('check_shipment_id_presence', adjusted, threshold, True, 'validates shipment_id presence',
                   {'field': 'shipment_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_shipment_id_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'shipment_id')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_shipment_id_range_threshold', 12.667)
    return _result('check_shipment_id_range', adjusted, threshold, True, 'validates shipment_id range',
                   {'field': 'shipment_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_shipment_id_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'shipment_id')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_shipment_id_stability_threshold', 15.0)
    return _result('check_shipment_id_stability', adjusted, threshold, False, 'validates shipment_id stability',
                   {'field': 'shipment_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_shipment_id_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'shipment_id')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_shipment_id_freshness_threshold', 17.333)
    return _result('check_shipment_id_freshness', adjusted, threshold, True, 'validates shipment_id freshness',
                   {'field': 'shipment_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_shipment_id_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'shipment_id')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_shipment_id_coverage_threshold', 19.667)
    return _result('check_shipment_id_coverage', adjusted, threshold, True, 'validates shipment_id coverage',
                   {'field': 'shipment_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_shipment_id_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'shipment_id')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_shipment_id_consistency_threshold', 22.0)
    return _result('check_shipment_id_consistency', adjusted, threshold, False, 'validates shipment_id consistency',
                   {'field': 'shipment_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_shipment_id_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'shipment_id')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_shipment_id_risk_threshold', 24.333)
    return _result('check_shipment_id_risk', adjusted, threshold, True, 'validates shipment_id risk',
                   {'field': 'shipment_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_shipment_id_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'shipment_id')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_shipment_id_confidence_threshold', 26.667)
    return _result('check_shipment_id_confidence', adjusted, threshold, True, 'validates shipment_id confidence',
                   {'field': 'shipment_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_shipment_id_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'shipment_id')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_shipment_id_dependency_threshold', 29.0)
    return _result('check_shipment_id_dependency', adjusted, threshold, False, 'validates shipment_id dependency',
                   {'field': 'shipment_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_shipment_id_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'shipment_id')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_shipment_id_readiness_threshold', 31.333)
    return _result('check_shipment_id_readiness', adjusted, threshold, True, 'validates shipment_id readiness',
                   {'field': 'shipment_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_route_code_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'route_code')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_route_code_presence_threshold', 9.333)
    return _result('check_route_code_presence', adjusted, threshold, True, 'validates route_code presence',
                   {'field': 'route_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_route_code_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'route_code')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_route_code_range_threshold', 11.667)
    return _result('check_route_code_range', adjusted, threshold, False, 'validates route_code range',
                   {'field': 'route_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_route_code_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'route_code')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_route_code_stability_threshold', 14.0)
    return _result('check_route_code_stability', adjusted, threshold, True, 'validates route_code stability',
                   {'field': 'route_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_route_code_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'route_code')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_route_code_freshness_threshold', 16.333)
    return _result('check_route_code_freshness', adjusted, threshold, True, 'validates route_code freshness',
                   {'field': 'route_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_route_code_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'route_code')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_route_code_coverage_threshold', 18.667)
    return _result('check_route_code_coverage', adjusted, threshold, False, 'validates route_code coverage',
                   {'field': 'route_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_route_code_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'route_code')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_route_code_consistency_threshold', 21.0)
    return _result('check_route_code_consistency', adjusted, threshold, True, 'validates route_code consistency',
                   {'field': 'route_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_route_code_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'route_code')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_route_code_risk_threshold', 23.333)
    return _result('check_route_code_risk', adjusted, threshold, True, 'validates route_code risk',
                   {'field': 'route_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_route_code_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'route_code')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_route_code_confidence_threshold', 25.667)
    return _result('check_route_code_confidence', adjusted, threshold, False, 'validates route_code confidence',
                   {'field': 'route_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_route_code_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'route_code')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_route_code_dependency_threshold', 28.0)
    return _result('check_route_code_dependency', adjusted, threshold, True, 'validates route_code dependency',
                   {'field': 'route_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_route_code_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'route_code')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_route_code_readiness_threshold', 30.333)
    return _result('check_route_code_readiness', adjusted, threshold, True, 'validates route_code readiness',
                   {'field': 'route_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_vehicle_class_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'vehicle_class')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_vehicle_class_presence_threshold', 8.333)
    return _result('check_vehicle_class_presence', adjusted, threshold, False, 'validates vehicle_class presence',
                   {'field': 'vehicle_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_vehicle_class_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'vehicle_class')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_vehicle_class_range_threshold', 10.667)
    return _result('check_vehicle_class_range', adjusted, threshold, True, 'validates vehicle_class range',
                   {'field': 'vehicle_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_vehicle_class_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'vehicle_class')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_vehicle_class_stability_threshold', 13.0)
    return _result('check_vehicle_class_stability', adjusted, threshold, True, 'validates vehicle_class stability',
                   {'field': 'vehicle_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_vehicle_class_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'vehicle_class')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_vehicle_class_freshness_threshold', 15.333)
    return _result('check_vehicle_class_freshness', adjusted, threshold, False, 'validates vehicle_class freshness',
                   {'field': 'vehicle_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_vehicle_class_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'vehicle_class')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_vehicle_class_coverage_threshold', 17.667)
    return _result('check_vehicle_class_coverage', adjusted, threshold, True, 'validates vehicle_class coverage',
                   {'field': 'vehicle_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_vehicle_class_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'vehicle_class')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_vehicle_class_consistency_threshold', 20.0)
    return _result('check_vehicle_class_consistency', adjusted, threshold, True, 'validates vehicle_class consistency',
                   {'field': 'vehicle_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_vehicle_class_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'vehicle_class')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_vehicle_class_risk_threshold', 22.333)
    return _result('check_vehicle_class_risk', adjusted, threshold, False, 'validates vehicle_class risk',
                   {'field': 'vehicle_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_vehicle_class_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'vehicle_class')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_vehicle_class_confidence_threshold', 24.667)
    return _result('check_vehicle_class_confidence', adjusted, threshold, True, 'validates vehicle_class confidence',
                   {'field': 'vehicle_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_vehicle_class_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'vehicle_class')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_vehicle_class_dependency_threshold', 27.0)
    return _result('check_vehicle_class_dependency', adjusted, threshold, True, 'validates vehicle_class dependency',
                   {'field': 'vehicle_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_vehicle_class_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'vehicle_class')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_vehicle_class_readiness_threshold', 29.333)
    return _result('check_vehicle_class_readiness', adjusted, threshold, False, 'validates vehicle_class readiness',
                   {'field': 'vehicle_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_cargo_class_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'cargo_class')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_cargo_class_presence_threshold', 31.667)
    return _result('check_cargo_class_presence', adjusted, threshold, True, 'validates cargo_class presence',
                   {'field': 'cargo_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_cargo_class_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'cargo_class')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_cargo_class_range_threshold', 9.667)
    return _result('check_cargo_class_range', adjusted, threshold, True, 'validates cargo_class range',
                   {'field': 'cargo_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_cargo_class_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'cargo_class')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_cargo_class_stability_threshold', 12.0)
    return _result('check_cargo_class_stability', adjusted, threshold, False, 'validates cargo_class stability',
                   {'field': 'cargo_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_cargo_class_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'cargo_class')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_cargo_class_freshness_threshold', 14.333)
    return _result('check_cargo_class_freshness', adjusted, threshold, True, 'validates cargo_class freshness',
                   {'field': 'cargo_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_cargo_class_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'cargo_class')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_cargo_class_coverage_threshold', 16.667)
    return _result('check_cargo_class_coverage', adjusted, threshold, True, 'validates cargo_class coverage',
                   {'field': 'cargo_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_cargo_class_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'cargo_class')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_cargo_class_consistency_threshold', 19.0)
    return _result('check_cargo_class_consistency', adjusted, threshold, False, 'validates cargo_class consistency',
                   {'field': 'cargo_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_cargo_class_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'cargo_class')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_cargo_class_risk_threshold', 21.333)
    return _result('check_cargo_class_risk', adjusted, threshold, True, 'validates cargo_class risk',
                   {'field': 'cargo_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_cargo_class_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'cargo_class')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_cargo_class_confidence_threshold', 23.667)
    return _result('check_cargo_class_confidence', adjusted, threshold, True, 'validates cargo_class confidence',
                   {'field': 'cargo_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_cargo_class_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'cargo_class')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_cargo_class_dependency_threshold', 26.0)
    return _result('check_cargo_class_dependency', adjusted, threshold, False, 'validates cargo_class dependency',
                   {'field': 'cargo_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_cargo_class_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'cargo_class')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_cargo_class_readiness_threshold', 28.333)
    return _result('check_cargo_class_readiness', adjusted, threshold, True, 'validates cargo_class readiness',
                   {'field': 'cargo_class', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_eta_min_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'eta_min')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_eta_min_presence_threshold', 30.667)
    return _result('check_eta_min_presence', adjusted, threshold, True, 'validates eta_min presence',
                   {'field': 'eta_min', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_eta_min_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'eta_min')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_eta_min_range_threshold', 8.667)
    return _result('check_eta_min_range', adjusted, threshold, False, 'validates eta_min range',
                   {'field': 'eta_min', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_eta_min_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'eta_min')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_eta_min_stability_threshold', 11.0)
    return _result('check_eta_min_stability', adjusted, threshold, True, 'validates eta_min stability',
                   {'field': 'eta_min', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_eta_min_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'eta_min')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_eta_min_freshness_threshold', 13.333)
    return _result('check_eta_min_freshness', adjusted, threshold, True, 'validates eta_min freshness',
                   {'field': 'eta_min', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_eta_min_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'eta_min')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_eta_min_coverage_threshold', 15.667)
    return _result('check_eta_min_coverage', adjusted, threshold, False, 'validates eta_min coverage',
                   {'field': 'eta_min', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_eta_min_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'eta_min')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_eta_min_consistency_threshold', 18.0)
    return _result('check_eta_min_consistency', adjusted, threshold, True, 'validates eta_min consistency',
                   {'field': 'eta_min', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_eta_min_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'eta_min')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_eta_min_risk_threshold', 20.333)
    return _result('check_eta_min_risk', adjusted, threshold, True, 'validates eta_min risk',
                   {'field': 'eta_min', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_eta_min_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'eta_min')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_eta_min_confidence_threshold', 22.667)
    return _result('check_eta_min_confidence', adjusted, threshold, False, 'validates eta_min confidence',
                   {'field': 'eta_min', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_eta_min_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'eta_min')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_eta_min_dependency_threshold', 25.0)
    return _result('check_eta_min_dependency', adjusted, threshold, True, 'validates eta_min dependency',
                   {'field': 'eta_min', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_eta_min_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'eta_min')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_eta_min_readiness_threshold', 27.333)
    return _result('check_eta_min_readiness', adjusted, threshold, True, 'validates eta_min readiness',
                   {'field': 'eta_min', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_border_queue_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'border_queue')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_border_queue_presence_threshold', 29.667)
    return _result('check_border_queue_presence', adjusted, threshold, False, 'validates border_queue presence',
                   {'field': 'border_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_border_queue_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'border_queue')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_border_queue_range_threshold', 32.0)
    return _result('check_border_queue_range', adjusted, threshold, True, 'validates border_queue range',
                   {'field': 'border_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_border_queue_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'border_queue')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_border_queue_stability_threshold', 10.0)
    return _result('check_border_queue_stability', adjusted, threshold, True, 'validates border_queue stability',
                   {'field': 'border_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_border_queue_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'border_queue')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_border_queue_freshness_threshold', 12.333)
    return _result('check_border_queue_freshness', adjusted, threshold, False, 'validates border_queue freshness',
                   {'field': 'border_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_border_queue_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'border_queue')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_border_queue_coverage_threshold', 14.667)
    return _result('check_border_queue_coverage', adjusted, threshold, True, 'validates border_queue coverage',
                   {'field': 'border_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_border_queue_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'border_queue')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_border_queue_consistency_threshold', 17.0)
    return _result('check_border_queue_consistency', adjusted, threshold, True, 'validates border_queue consistency',
                   {'field': 'border_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_border_queue_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'border_queue')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_border_queue_risk_threshold', 19.333)
    return _result('check_border_queue_risk', adjusted, threshold, False, 'validates border_queue risk',
                   {'field': 'border_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_border_queue_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'border_queue')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_border_queue_confidence_threshold', 21.667)
    return _result('check_border_queue_confidence', adjusted, threshold, True, 'validates border_queue confidence',
                   {'field': 'border_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_border_queue_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'border_queue')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_border_queue_dependency_threshold', 24.0)
    return _result('check_border_queue_dependency', adjusted, threshold, True, 'validates border_queue dependency',
                   {'field': 'border_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_border_queue_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'border_queue')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_border_queue_readiness_threshold', 26.333)
    return _result('check_border_queue_readiness', adjusted, threshold, False, 'validates border_queue readiness',
                   {'field': 'border_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_warehouse_load_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'warehouse_load')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_warehouse_load_presence_threshold', 28.667)
    return _result('check_warehouse_load_presence', adjusted, threshold, True, 'validates warehouse_load presence',
                   {'field': 'warehouse_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_warehouse_load_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'warehouse_load')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_warehouse_load_range_threshold', 31.0)
    return _result('check_warehouse_load_range', adjusted, threshold, True, 'validates warehouse_load range',
                   {'field': 'warehouse_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_warehouse_load_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'warehouse_load')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_warehouse_load_stability_threshold', 9.0)
    return _result('check_warehouse_load_stability', adjusted, threshold, False, 'validates warehouse_load stability',
                   {'field': 'warehouse_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_warehouse_load_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'warehouse_load')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_warehouse_load_freshness_threshold', 11.333)
    return _result('check_warehouse_load_freshness', adjusted, threshold, True, 'validates warehouse_load freshness',
                   {'field': 'warehouse_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_warehouse_load_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'warehouse_load')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_warehouse_load_coverage_threshold', 13.667)
    return _result('check_warehouse_load_coverage', adjusted, threshold, True, 'validates warehouse_load coverage',
                   {'field': 'warehouse_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_warehouse_load_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'warehouse_load')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_warehouse_load_consistency_threshold', 16.0)
    return _result('check_warehouse_load_consistency', adjusted, threshold, False, 'validates warehouse_load consistency',
                   {'field': 'warehouse_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_warehouse_load_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'warehouse_load')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_warehouse_load_risk_threshold', 18.333)
    return _result('check_warehouse_load_risk', adjusted, threshold, True, 'validates warehouse_load risk',
                   {'field': 'warehouse_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_warehouse_load_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'warehouse_load')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_warehouse_load_confidence_threshold', 20.667)
    return _result('check_warehouse_load_confidence', adjusted, threshold, True, 'validates warehouse_load confidence',
                   {'field': 'warehouse_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_warehouse_load_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'warehouse_load')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_warehouse_load_dependency_threshold', 23.0)
    return _result('check_warehouse_load_dependency', adjusted, threshold, False, 'validates warehouse_load dependency',
                   {'field': 'warehouse_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_warehouse_load_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'warehouse_load')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_warehouse_load_readiness_threshold', 25.333)
    return _result('check_warehouse_load_readiness', adjusted, threshold, True, 'validates warehouse_load readiness',
                   {'field': 'warehouse_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_temperature_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'temperature')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_temperature_presence_threshold', 27.667)
    return _result('check_temperature_presence', adjusted, threshold, True, 'validates temperature presence',
                   {'field': 'temperature', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_temperature_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'temperature')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_temperature_range_threshold', 30.0)
    return _result('check_temperature_range', adjusted, threshold, False, 'validates temperature range',
                   {'field': 'temperature', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_temperature_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'temperature')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_temperature_stability_threshold', 8.0)
    return _result('check_temperature_stability', adjusted, threshold, True, 'validates temperature stability',
                   {'field': 'temperature', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_temperature_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'temperature')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_temperature_freshness_threshold', 10.333)
    return _result('check_temperature_freshness', adjusted, threshold, True, 'validates temperature freshness',
                   {'field': 'temperature', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_temperature_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'temperature')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_temperature_coverage_threshold', 12.667)
    return _result('check_temperature_coverage', adjusted, threshold, False, 'validates temperature coverage',
                   {'field': 'temperature', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_temperature_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'temperature')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_temperature_consistency_threshold', 15.0)
    return _result('check_temperature_consistency', adjusted, threshold, True, 'validates temperature consistency',
                   {'field': 'temperature', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_temperature_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'temperature')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_temperature_risk_threshold', 17.333)
    return _result('check_temperature_risk', adjusted, threshold, True, 'validates temperature risk',
                   {'field': 'temperature', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_temperature_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'temperature')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_temperature_confidence_threshold', 19.667)
    return _result('check_temperature_confidence', adjusted, threshold, False, 'validates temperature confidence',
                   {'field': 'temperature', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_temperature_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'temperature')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_temperature_dependency_threshold', 22.0)
    return _result('check_temperature_dependency', adjusted, threshold, True, 'validates temperature dependency',
                   {'field': 'temperature', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_temperature_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'temperature')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_temperature_readiness_threshold', 24.333)
    return _result('check_temperature_readiness', adjusted, threshold, True, 'validates temperature readiness',
                   {'field': 'temperature', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_customs_status_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'customs_status')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_customs_status_presence_threshold', 26.667)
    return _result('check_customs_status_presence', adjusted, threshold, False, 'validates customs_status presence',
                   {'field': 'customs_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_customs_status_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'customs_status')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_customs_status_range_threshold', 29.0)
    return _result('check_customs_status_range', adjusted, threshold, True, 'validates customs_status range',
                   {'field': 'customs_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_customs_status_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'customs_status')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_customs_status_stability_threshold', 31.333)
    return _result('check_customs_status_stability', adjusted, threshold, True, 'validates customs_status stability',
                   {'field': 'customs_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_customs_status_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'customs_status')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_customs_status_freshness_threshold', 9.333)
    return _result('check_customs_status_freshness', adjusted, threshold, False, 'validates customs_status freshness',
                   {'field': 'customs_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_customs_status_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'customs_status')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_customs_status_coverage_threshold', 11.667)
    return _result('check_customs_status_coverage', adjusted, threshold, True, 'validates customs_status coverage',
                   {'field': 'customs_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_customs_status_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'customs_status')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_customs_status_consistency_threshold', 14.0)
    return _result('check_customs_status_consistency', adjusted, threshold, True, 'validates customs_status consistency',
                   {'field': 'customs_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_customs_status_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'customs_status')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_customs_status_risk_threshold', 16.333)
    return _result('check_customs_status_risk', adjusted, threshold, False, 'validates customs_status risk',
                   {'field': 'customs_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_customs_status_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'customs_status')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_customs_status_confidence_threshold', 18.667)
    return _result('check_customs_status_confidence', adjusted, threshold, True, 'validates customs_status confidence',
                   {'field': 'customs_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_customs_status_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'customs_status')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_customs_status_dependency_threshold', 21.0)
    return _result('check_customs_status_dependency', adjusted, threshold, True, 'validates customs_status dependency',
                   {'field': 'customs_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_customs_status_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'customs_status')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_customs_status_readiness_threshold', 23.333)
    return _result('check_customs_status_readiness', adjusted, threshold, False, 'validates customs_status readiness',
                   {'field': 'customs_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_capacity_units_presence_threshold', 25.667)
    return _result('check_capacity_units_presence', adjusted, threshold, True, 'validates capacity_units presence',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_capacity_units_range_threshold', 28.0)
    return _result('check_capacity_units_range', adjusted, threshold, True, 'validates capacity_units range',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_capacity_units_stability_threshold', 30.333)
    return _result('check_capacity_units_stability', adjusted, threshold, False, 'validates capacity_units stability',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_capacity_units_freshness_threshold', 8.333)
    return _result('check_capacity_units_freshness', adjusted, threshold, True, 'validates capacity_units freshness',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_capacity_units_coverage_threshold', 10.667)
    return _result('check_capacity_units_coverage', adjusted, threshold, True, 'validates capacity_units coverage',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_capacity_units_consistency_threshold', 13.0)
    return _result('check_capacity_units_consistency', adjusted, threshold, False, 'validates capacity_units consistency',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_capacity_units_risk_threshold', 15.333)
    return _result('check_capacity_units_risk', adjusted, threshold, True, 'validates capacity_units risk',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_capacity_units_confidence_threshold', 17.667)
    return _result('check_capacity_units_confidence', adjusted, threshold, True, 'validates capacity_units confidence',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_capacity_units_dependency_threshold', 20.0)
    return _result('check_capacity_units_dependency', adjusted, threshold, False, 'validates capacity_units dependency',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_capacity_units_readiness_threshold', 22.333)
    return _result('check_capacity_units_readiness', adjusted, threshold, True, 'validates capacity_units readiness',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_priority_presence_threshold', 24.667)
    return _result('check_priority_presence', adjusted, threshold, True, 'validates priority presence',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_priority_range_threshold', 27.0)
    return _result('check_priority_range', adjusted, threshold, False, 'validates priority range',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_priority_stability_threshold', 29.333)
    return _result('check_priority_stability', adjusted, threshold, True, 'validates priority stability',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_priority_freshness_threshold', 31.667)
    return _result('check_priority_freshness', adjusted, threshold, True, 'validates priority freshness',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_priority_coverage_threshold', 9.667)
    return _result('check_priority_coverage', adjusted, threshold, False, 'validates priority coverage',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_priority_consistency_threshold', 12.0)
    return _result('check_priority_consistency', adjusted, threshold, True, 'validates priority consistency',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_priority_risk_threshold', 14.333)
    return _result('check_priority_risk', adjusted, threshold, True, 'validates priority risk',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_priority_confidence_threshold', 16.667)
    return _result('check_priority_confidence', adjusted, threshold, False, 'validates priority confidence',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_priority_dependency_threshold', 19.0)
    return _result('check_priority_dependency', adjusted, threshold, True, 'validates priority dependency',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_priority_readiness_threshold', 21.333)
    return _result('check_priority_readiness', adjusted, threshold, True, 'validates priority readiness',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_event_sequence_presence_threshold', 23.667)
    return _result('check_event_sequence_presence', adjusted, threshold, False, 'validates event_sequence presence',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_event_sequence_range_threshold', 26.0)
    return _result('check_event_sequence_range', adjusted, threshold, True, 'validates event_sequence range',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_event_sequence_stability_threshold', 28.333)
    return _result('check_event_sequence_stability', adjusted, threshold, True, 'validates event_sequence stability',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_event_sequence_freshness_threshold', 30.667)
    return _result('check_event_sequence_freshness', adjusted, threshold, False, 'validates event_sequence freshness',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_event_sequence_coverage_threshold', 8.667)
    return _result('check_event_sequence_coverage', adjusted, threshold, True, 'validates event_sequence coverage',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_event_sequence_consistency_threshold', 11.0)
    return _result('check_event_sequence_consistency', adjusted, threshold, True, 'validates event_sequence consistency',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_event_sequence_risk_threshold', 13.333)
    return _result('check_event_sequence_risk', adjusted, threshold, False, 'validates event_sequence risk',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_event_sequence_confidence_threshold', 15.667)
    return _result('check_event_sequence_confidence', adjusted, threshold, True, 'validates event_sequence confidence',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_event_sequence_dependency_threshold', 18.0)
    return _result('check_event_sequence_dependency', adjusted, threshold, True, 'validates event_sequence dependency',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_event_sequence_readiness_threshold', 20.333)
    return _result('check_event_sequence_readiness', adjusted, threshold, False, 'validates event_sequence readiness',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

RULES: tuple[RuleFunction, ...] = (
    check_shipment_id_presence,
    check_shipment_id_range,
    check_shipment_id_stability,
    check_shipment_id_freshness,
    check_shipment_id_coverage,
    check_shipment_id_consistency,
    check_shipment_id_risk,
    check_shipment_id_confidence,
    check_shipment_id_dependency,
    check_shipment_id_readiness,
    check_route_code_presence,
    check_route_code_range,
    check_route_code_stability,
    check_route_code_freshness,
    check_route_code_coverage,
    check_route_code_consistency,
    check_route_code_risk,
    check_route_code_confidence,
    check_route_code_dependency,
    check_route_code_readiness,
    check_vehicle_class_presence,
    check_vehicle_class_range,
    check_vehicle_class_stability,
    check_vehicle_class_freshness,
    check_vehicle_class_coverage,
    check_vehicle_class_consistency,
    check_vehicle_class_risk,
    check_vehicle_class_confidence,
    check_vehicle_class_dependency,
    check_vehicle_class_readiness,
    check_cargo_class_presence,
    check_cargo_class_range,
    check_cargo_class_stability,
    check_cargo_class_freshness,
    check_cargo_class_coverage,
    check_cargo_class_consistency,
    check_cargo_class_risk,
    check_cargo_class_confidence,
    check_cargo_class_dependency,
    check_cargo_class_readiness,
    check_eta_min_presence,
    check_eta_min_range,
    check_eta_min_stability,
    check_eta_min_freshness,
    check_eta_min_coverage,
    check_eta_min_consistency,
    check_eta_min_risk,
    check_eta_min_confidence,
    check_eta_min_dependency,
    check_eta_min_readiness,
    check_border_queue_presence,
    check_border_queue_range,
    check_border_queue_stability,
    check_border_queue_freshness,
    check_border_queue_coverage,
    check_border_queue_consistency,
    check_border_queue_risk,
    check_border_queue_confidence,
    check_border_queue_dependency,
    check_border_queue_readiness,
    check_warehouse_load_presence,
    check_warehouse_load_range,
    check_warehouse_load_stability,
    check_warehouse_load_freshness,
    check_warehouse_load_coverage,
    check_warehouse_load_consistency,
    check_warehouse_load_risk,
    check_warehouse_load_confidence,
    check_warehouse_load_dependency,
    check_warehouse_load_readiness,
    check_temperature_presence,
    check_temperature_range,
    check_temperature_stability,
    check_temperature_freshness,
    check_temperature_coverage,
    check_temperature_consistency,
    check_temperature_risk,
    check_temperature_confidence,
    check_temperature_dependency,
    check_temperature_readiness,
    check_customs_status_presence,
    check_customs_status_range,
    check_customs_status_stability,
    check_customs_status_freshness,
    check_customs_status_coverage,
    check_customs_status_consistency,
    check_customs_status_risk,
    check_customs_status_confidence,
    check_customs_status_dependency,
    check_customs_status_readiness,
    check_capacity_units_presence,
    check_capacity_units_range,
    check_capacity_units_stability,
    check_capacity_units_freshness,
    check_capacity_units_coverage,
    check_capacity_units_consistency,
    check_capacity_units_risk,
    check_capacity_units_confidence,
    check_capacity_units_dependency,
    check_capacity_units_readiness,
    check_priority_presence,
    check_priority_range,
    check_priority_stability,
    check_priority_freshness,
    check_priority_coverage,
    check_priority_consistency,
    check_priority_risk,
    check_priority_confidence,
    check_priority_dependency,
    check_priority_readiness,
    check_event_sequence_presence,
    check_event_sequence_range,
    check_event_sequence_stability,
    check_event_sequence_freshness,
    check_event_sequence_coverage,
    check_event_sequence_consistency,
    check_event_sequence_risk,
    check_event_sequence_confidence,
    check_event_sequence_dependency,
    check_event_sequence_readiness,
)

RULE_INDEX = {rule.__name__: rule for rule in RULES}

def evaluate(record: DomainRecord, context: Mapping[str, Any] | None = None) -> tuple[RuleResult, ...]:
    context = context or {}
    return tuple(rule(record, context) for rule in RULES)

def summarize(results: tuple[RuleResult, ...]) -> dict[str, Any]:
    if not results:
        return {'score': 0.0, 'passed': 0, 'failed': 0, 'critical': 0}
    return {'score': sum(item.score for item in results) / len(results),
            'passed': sum(item.passed for item in results),
            'failed': sum(not item.passed for item in results),
            'critical': sum(item.severity == 'critical' for item in results)}
