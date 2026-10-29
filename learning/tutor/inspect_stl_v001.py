"""Read-only binary STL inventory. Numerical agreement is not manufacture/fit approval."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct


def inspect(path, units, expected=None, epsilon=1e-4):
    if units != 'mm':
        raise ValueError('explicit mm interpretation is required; STL stores no unit')
    if not math.isfinite(epsilon) or epsilon <= 0:
        raise ValueError('numeric epsilon must be finite and positive')
    path = Path(path)
    raw = path.read_bytes()
    if len(raw) < 84:
        raise ValueError('binary STL header is truncated; ASCII is unsupported')
    count = struct.unpack_from('<I', raw, 80)[0]
    if not count or len(raw) != 84 + count * 50:
        raise ValueError('binary STL count/length mismatch or empty file; ASCII is unsupported')
    bounds = [[math.inf, -math.inf] for _ in range(3)]
    triangles = Counter()
    zero_area = 0
    for offset in range(84, len(raw), 50):
        values = struct.unpack_from('<12fH', raw, offset)
        if not all(math.isfinite(v) for v in values[:12]):
            raise ValueError('non-finite facet normal or vertex')
        points = tuple(tuple(values[i:i+3]) for i in (3, 6, 9))
        for point in points:
            for axis in range(3):
                bounds[axis][0] = min(bounds[axis][0], point[axis])
                bounds[axis][1] = max(bounds[axis][1], point[axis])
        a = tuple(points[1][i] - points[0][i] for i in range(3))
        b = tuple(points[2][i] - points[0][i] for i in range(3))
        cross = (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
        zero_area += all(v == 0 for v in cross)
        triangles[tuple(sorted(points))] += 1
    dimensions = [hi-lo for lo, hi in bounds]
    comparison = None
    if expected is not None:
        if len(expected) != 3 or any(not math.isfinite(v) or v <= 0 for v in expected):
            raise ValueError('expected dimensions must be three positive finite values')
        differences = [a-b for a, b in zip(dimensions, expected)]
        comparison = {'expectedWorldDimensionsMm': list(expected), 'actualMinusExpectedMm': differences,
                      'absoluteNumericEpsilonMm': epsilon,
                      'withinNumericEpsilon': all(abs(v) <= epsilon for v in differences),
                      'meaning': 'floating-point number comparison only; not a manufacturing tolerance'}
    return {'schemaVersion': 1, 'inputName': path.name, 'sha256': hashlib.sha256(raw).hexdigest(),
            'bytes': len(raw), 'binaryTriangles': count, 'unitInterpretation': units,
            'worldCoordinateBoundsMm': bounds, 'worldDimensionsMm': dimensions,
            'exactCoordinateDuplicateGroups': sum(v > 1 for v in triangles.values()),
            'exactCoordinateDuplicateExcessTriangles': sum(v-1 for v in triangles.values()),
            'zeroAreaFacets': zero_area, 'numericalComparison': comparison,
            'limitations': ['Does not modify the input or weld coordinates; winding is ignored only when counting duplicate coordinates.',
                            'Does not check manifold topology, all self-intersections, thin walls, slicing, material, strength or fit.',
                            'STL has no unit declaration; mm is the explicit interpretation chosen by this command.'],
            'physicalPrint': None, 'physicalMeasurement': None, 'physicalFit': None,
            'qualifiedClearance': None, 'qualifiedStrength': None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', required=True, type=Path)
    parser.add_argument('--units', choices=['mm'], required=True)
    parser.add_argument('--expected-dimensions', type=float, nargs=3, metavar=('X', 'Y', 'Z'))
    args = parser.parse_args(argv)
    try:
        result = inspect(args.file, args.units, args.expected_dimensions)
    except (OSError, ValueError, OverflowError) as error:
        parser.error(str(error))
    # ASCII JSON is portable across Windows console/pipe encodings (e.g. cp950).
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
