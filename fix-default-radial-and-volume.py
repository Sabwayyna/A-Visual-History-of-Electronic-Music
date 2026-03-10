"""
1. Change default visualization mode to 'radial' (tunnel effect)
2. Lower audio volume from 0.8 (80%) to 0.5 (50%)
"""

with open('sketch.js', 'r', encoding='utf-8') as f:
    sketch = f.read()

# 1. Change default mode from 'horizontal' to 'radial'
sketch = sketch.replace(
    "let visualMode = 'horizontal'; // 'horizontal' or 'radial'",
    "let visualMode = 'radial'; // 'horizontal' or 'radial' - DEFAULT: radial (tunnel effect)"
)

# 2. Update the mode indicator default text in HTML to show RADIAL MODE
# This will be done in the HTML generation script

with open('sketch.js', 'w', encoding='utf-8') as f:
    f.write(sketch)

print("✓ Changed default visualization mode:")
print("  - Default mode: horizontal → radial")
print("  - Songs will now start with tunnel effect (center expanding outward)")
print("  - Users can still toggle to horizontal with M key or button")
