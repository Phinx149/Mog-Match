---
name: new-feature
description: Build a new MogMatch feature end-to-end — Flask endpoint, service, React page/component, API client, types and tests — following project conventions, from branch to PR. Use when a developer wants to add a feature, page, component, button, form, or API endpoint.
---

# New Feature

Explain briefly *why* at each step — several teammates are beginners. Keep the change small.

## 1. Branch
```bash
git checkout dev && git pull
git checkout -b feat/<short-name>
```

## 2. Where code goes
| Building… | Location |
|---|---|
| DB table/column | `backend/app/models/` → then the `db-migration` skill |
| Business logic, validation, serialization | `backend/app/services/<area>_service.py` |
| HTTP endpoint | `backend/app/routes/<area>.py` (Blueprint, register it in `app/__init__.py`) |
| Backend test | `backend/tests/test_<area>.py` (fixtures `app`, `client` in `conftest.py`) |
| Response types | `frontend/src/types/` — snake_case, must match the Flask JSON |
| API call | `frontend/src/services/api.ts` (use the `request<T>()` helper) |
| Page (has a route) | `frontend/src/pages/` + route in `App.tsx` |
| Reusable UI | `frontend/src/components/<area>/` |

## 3. Backend patterns
```python
# routes/<area>.py — thin: parse request, call service, return JSON
bp = Blueprint("swipes", __name__, url_prefix="/api/swipes")

@bp.post("", strict_slashes=False)
def create_swipe():
    me = profile_service.get_demo_profile()          # identity comes from the server, never the client
    if me is None:
        abort(404, description="Demo profile not found.")
    try:
        result = swipe_service.record(me, request.get_json(silent=True))
    except ValidationError as error:
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), 400
    return jsonify(result), 201
```
- Validate every incoming field (type, length, allowed values). Reject unknown fields.
- Error shape: `{"error": {"message": "...", "fields": {...}}}`. Use 400 / 404 / 409 appropriately.
- Test: happy path, 404, and invalid input at minimum.

## 4. Frontend patterns
```ts
// services/api.ts
export function createSwipe(targetId: string, action: SwipeDecision) {
  return request<Swipe>("/api/swipes", { method: "POST", body: JSON.stringify({ target_id: targetId, action }) });
}
```
```tsx
// in a page: load with AbortController, show loading / error / empty states
useEffect(() => {
  const controller = new AbortController();
  getThing(controller.signal).then(setThing).catch((err) => {
    if (err instanceof DOMException && err.name === "AbortError") return;
    setError(err instanceof Error ? err.message : "Something went wrong");
  });
  return () => controller.abort();
}, []);
```
- Reuse `LoadingState`, `ErrorState`, `EmptyState` (`components/common/States.tsx`), `SkillBadge`, `TagInput`, `Navbar`.
- Style with Tailwind + theme tokens (`bg-surface`, `bg-surface-raised`, `border-line`, `text-muted`, violet/cyan accents). Form inputs use the `field` class.
- Icons from `lucide-react` with `aria-hidden`; icon-only buttons need `aria-label`.

## 5. Verify
```bash
cd backend && pytest
cd frontend && npm run build
```
Then click through the feature with both servers running.

## 6. Commit + PR
```bash
git add -A
git commit -m "feat: <what it does>"
git push -u origin feat/<short-name>
gh pr create --base dev --fill
```
PR description: what changed, screenshot for UI, how to test.
