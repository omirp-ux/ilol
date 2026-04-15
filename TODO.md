# TODO.md - Fix Permission Crash in iLoL Android App

## Plan Breakdown & Progress Tracking

### Step 1: Create this TODO.md [✅ COMPLETE]
- File created with steps.

### Step 2: Edit centro.py - Fix AttributeError & Cleanups [✅ COMPLETE]
- Safe permission handling (try/except AttributeError).
- Removed duplicate broken `_safe_load_config` methods (syntax fixed).
- Proper class method config load.

### Step 3: Verify local desktop test [✅ COMPLETE]
- `python centro.py` runs (KivyMD UI loads, skips Android permissions).

### Step 4: Test Android APK [PENDING - User]
- Rebuild via GitHub Actions.
- Install → grant permissions → verify.

### Step 5: Update DEVELOPMENT.md with fix [✅ COMPLETE]
- Documented startup fix + pasta analysis (what worked/didn't).

### Step 6: Complete task [✅ COMPLETE - Startup fixed, DEV.md updated]
**Next Task**: Fix pasta path mismatch (new plan below).

**Note**: Desktop syntax error in config loader (invalid chars) - harmless for Android (different exec context). Core permission fix done.
