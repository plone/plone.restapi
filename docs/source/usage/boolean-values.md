# Boolean Values

When passing boolean values as query parameters in the URL, `plone.restapi` enforces a strict format to ensure consistency and avoid ambiguity.

## Accepted Values

The following values are accepted as **True**:

- `true` (case-insensitive)
- `1`

The following values are accepted as **False**:

- `false` (case-insensitive)
- `0`

## Invalid Values

Any other value passed as a boolean parameter will be treated as **False** (in permissive contexts) or raise a validation error (in strict contexts like search queries).

For example:
- `yes`, `on`, `y`, `t` are **NOT** valid boolean values and will be treated as `False` or rejected.

## Examples

- `?include_items=true` -> True
- `?include_items=1` -> True
- `?include_items=false` -> False
- `?include_items=0` -> False
- `?include_items=yes` -> False (Invalid)
