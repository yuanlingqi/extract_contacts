# Fix Git Push Error

The error is because `User_Data/` folder (137MB) is being tracked. Run these commands:

```bash
# Remove User_Data from git tracking (but keep local files)
git rm -r --cached User_Data/

# Remove other large files if needed
git rm --cached first_party_sets.db 2>/dev/null || true
git rm --cached *.pma 2>/dev/null || true

# Add the updated .gitignore
git add .gitignore

# Commit the changes
git commit -m "Remove User_Data and large files from git tracking"

# Push again
git push -u origin main
```

If you still get errors, try pushing in smaller chunks or increase git buffer:

```bash
# Increase git buffer size
git config http.postBuffer 524288000

# Try push again
git push -u origin main
```
