"""
Create dramatic tunnel/zoom effect for radial mode:
1. Shapes start VERY small at center (10% size)
2. Exponentially grow to VERY large at edge (250% size)
3. Creates feeling of moving through a tunnel expanding around viewer
"""

with open('sketch.js', 'r', encoding='utf-8') as f:
    sketch = f.read()

# Replace the linear size scaling with exponential tunnel effect
sketch = sketch.replace(
    '''  // Size multiplier for radial mode - start small at center, grow outward
  let sizeMultiplier = 1.0;
  if (visualMode === 'radial') {
    // Scale from 0.3 (30% size at center) to 1.5 (150% size at edge)
    sizeMultiplier = map(totalProgress, 0, 1, 0.3, 1.5);
  }''',
    '''  // Size multiplier for radial mode - TUNNEL EFFECT
  let sizeMultiplier = 1.0;
  if (visualMode === 'radial') {
    // Exponential growth for dramatic tunnel effect
    // Start tiny at center (10% size) and expand to very large at edge (250% size)
    // Use pow() for exponential feel - creates sense of zooming through tunnel
    let normalizedProgress = totalProgress; // 0 to 1
    let exponentialProgress = pow(normalizedProgress, 0.7); // Softer exponential curve
    sizeMultiplier = map(exponentialProgress, 0, 1, 0.1, 2.5);
  }'''
)

with open('sketch.js', 'w', encoding='utf-8') as f:
    f.write(sketch)

print("✓ Created tunnel zoom effect for radial mode:")
print("  - Shapes start at 10% size at center (vs 30% before)")
print("  - Shapes grow to 250% size at edge (vs 150% before)")
print("  - Exponential scaling curve for dramatic expansion")
print("  - Creates feeling of zooming through expanding tunnel")
print("  - All shapes radiate from center and widen as they progress")
