# Offline Setup Instructions for Servos

This file explains how to prepare all dependencies ahead of time, so the
application can be built and run on an air-gapped machine. The repository
delivers everything needed once the packages are downloaded.

## Python dependencies

1. **Download wheel packages.**
   From a machine with internet access run:

   ```powershell
   cd d:\fyeshi\project\servos
   python -m pip download -r requirements.txt -d offline_pkgs\python
   ```

   - The `offline_pkgs/python` directory (already created in this repo) will
     be populated with ~40 `.whl` files for every requirement and its
     dependencies.  The `requirements.txt` has been tuned for compatibility
     (the `python-magic` line replaced by `python-magic-bin`).
   - **Commit `offline_pkgs/python`** to git so it is available offline.

2. **Install from the local cache.**  On the air-gapped system use:

   ```powershell
   cd d:\fyeshi\project\servos
   python -m pip install --no-index --find-links=offline_pkgs\python -r requirements.txt
   ```

   This will pull wheels from the `offline_pkgs` folder and will not
   attempt any network connections.  If new packages are required later,
   repeat step 1 on an online machine and copy the new wheels.

## Node / npm dependencies (frontend)

The web UI lives in `servos-ui`.  Two options are available:

1. **Commit `node_modules`**
   - Run `npm ci` or `npm install` once on an internet-connected machine.
   - Add `servos-ui/node_modules` to the repository (it is currently
     `.gitignore`d) so that `npm run dev` or `npm run build` will work
     offline.  This is the simplest approach.

2. **Cache packages manually**
   - Use a tool like `npm pack` or a local npm registry (e.g. `verdaccio`)
     to prefetch all tarballs referenced by `package-lock.json`.
   - Store the resulting `node_modules` or registry data alongside the repo.

For a hackathon submission the first option (checking in `node_modules`)
usually suffices; just make sure the `package-lock.json` is up to date when
changing dependencies.

## LLM models

The offline assistant relies on an Ollama/llama_cpp server running locally.
Before disconnecting, pull the desired model(s) with:

```powershell
ollama pull llama3.1:8b
# or whichever model you plan to use
```

Copy the Ollama installation directory or model files to the air‑gapped host.

## Summary of what to commit

- `offline_pkgs/python/` (wheel files)
- either `servos-ui/node_modules/` or a packed npm cache
- `requirements.txt` has already been adjusted and is versioned
- `package-lock.json` is already in the repo
- (optional) `OFFLINE_INSTRUCTIONS.md` - this file

Once the dependencies are in place, the app can be built and run entirely
without any network connectivity.
