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
from ..services import swipe_service
from ..services.auth_service import current_profile_or_401

bp = Blueprint("swipes", __name__, url_prefix="/api/swipes")

@bp.post("", strict_slashes=False)
def create_swipe():
    me = current_profile_or_401()   # the logged-in user, from the signed session (401 if logged out)
    try:
        result = swipe_service.record_swipe(me, request.get_json(silent=True))
    except ValidationError as error:
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), 400
    except NotFoundError as error:
        abort(404, description=str(error))
    return jsonify(result), 201
```
Real examples to copy: `routes/invites.py` + `services/invite_service.py` (400/404/409, "only the recipient can answer").
- Validate every incoming field (type, length, allowed values). Reject unknown fields.
- Error shape: `{"error": {"message": "...", "fields": {...}}}`. Use 400 / 404 / 409 appropriately.
- Never take "who am I" from the request body/query. Anything that belongs to a user is looked up through `me`, and someone else's row should look like a 404.
- Test: happy path, 404, invalid input, and **401 when logged out** at minimum. Fixtures (`tests/conftest.py`): `client` = logged in as `jordan-dev`, `anon_client` = logged out, `log_in(client, "samfullstack")`. Two users: `a = log_in(app.test_client(), "jordan-dev")`, `b = log_in(app.test_client(), "samfullstack")` (see `tests/test_auth.py`).

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
- New pages go inside `<RequireAuth />` in `App.tsx` (logged-in only). `useAuth()` gives the current `user`. `request()` already sends the login cookie, so don't call `fetch` yourself.
- Reuse `LoadingState`, `ErrorState`, `EmptyState` (`components/common/States.tsx`), `SkillBadge`, `TagInput`, `Navbar`.
- Style with Tailwind + theme tokens (`bg-surface`, `bg-surface-raised`, `border-line`, `text-muted`, violet/cyan accents). Form inputs use the `field` class.
- Icons from `lucide-react` with `aria-hidden`; icon-only buttons need `aria-label`.

## 5. Verify
```bash
cd backend && pytest
cd frontend && npm run build
```
Then click through the feature with both servers running: `flask seed --reset && flask seed-test-users --reset`, log in as `user1` (normal window) and `user2` (incognito) at http://localhost:5173. Reset again when done.
If you changed a model: `flask db migrate -m "..."`, read the file, `flask db upgrade`, `flask db check`.

## 6. Commit + PR
```bash
git add -A
git commit -m "feat: <what it does>"
git push -u origin feat/<short-name>
gh pr create --base dev --fill
```
PR description: what changed, screenshot for UI, how to test, and anything teammates must run after pulling (`flask db upgrade`, `flask seed`, new env vars).
`gh` may not be installed: if `gh pr create` fails, push the branch and share `https://github.com/Phinx149/social-coding-Hackathon/compare/dev...<branch>?expand=1`.
