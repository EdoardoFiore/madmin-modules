#!/usr/bin/env python3
"""
MADMIN Registry Builder

Generates modules.json from individual module definitions in /modules/
and enriches them with data from module repositories (manifest.json, GitHub stats).

Run manually or via GitHub Actions.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests")
    import requests


GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
MODULES_DIR = Path(__file__).parent.parent / "modules"
OUTPUT_FILE = Path(__file__).parent.parent / "modules.json"


def get_repo_info(repo_url: str) -> tuple:
    """Extract owner/repo from GitHub URL."""
    if not repo_url or "github.com" not in repo_url:
        return None, None
    parts = repo_url.rstrip("/").rstrip(".git").split("/")
    return parts[-2], parts[-1]


def get_manifest_from_repo(owner: str, repo: str) -> dict:
    """Fetch manifest.json from the module repository."""
    headers = {"Accept": "application/vnd.github.v3.raw"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    try:
        # Try main branch first, then master
        for branch in ["main", "master"]:
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/manifest.json"
            r = requests.get(url, headers=headers, timeout=10)
            if r.ok:
                return r.json()
    except Exception as e:
        print(f"  Warning: Could not fetch manifest: {e}")
    
    return {}


def get_github_stats(owner: str, repo: str) -> dict:
    """Fetch stats from GitHub API."""
    if not owner or not repo:
        return {}
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    stats = {}
    
    try:
        # Get repo info
        r = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers,
            timeout=10
        )
        if r.ok:
            data = r.json()
            stats["stars"] = data.get("stargazers_count", 0)
            stats["updated_at"] = data.get("pushed_at")
        
        # Get releases for changelog
        r = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/releases",
            headers=headers,
            timeout=10
        )
        if r.ok:
            releases = r.json()
            if releases:
                stats["changelog"] = {
                    rel["tag_name"]: rel.get("body", "")[:500]
                    for rel in releases[:5]
                }
                # Sum download counts from release assets
                stats["downloads"] = sum(
                    asset.get("download_count", 0)
                    for rel in releases
                    for asset in rel.get("assets", [])
                )
    except Exception as e:
        print(f"  Warning: Could not fetch GitHub stats: {e}")
    
    return stats


def build_registry():
    """Build the main modules.json registry file."""
    modules = []
    
    print(f"Building registry from {MODULES_DIR}")
    
    for module_file in sorted(MODULES_DIR.glob("*.json")):
        print(f"  Processing {module_file.name}...")
        
        try:
            with open(module_file, "r", encoding="utf-8") as f:
                module_data = json.load(f)
            
            repo_url = module_data.get("repository", "")
            owner, repo = get_repo_info(repo_url)
            
            if owner and repo:
                # Fetch manifest.json from module repo for accurate version
                manifest = get_manifest_from_repo(owner, repo)
                if manifest:
                    print(f"    Found manifest: v{manifest.get('version', '?')}")
                    # Override with manifest data
                    module_data["version"] = manifest.get("version", module_data.get("version", "0.0.0"))
                    module_data["name"] = manifest.get("name", module_data.get("name"))
                    module_data["description"] = manifest.get("description", module_data.get("description"))
                    
                    # Merge features if present
                    if "features" not in module_data and manifest.get("permissions"):
                        module_data["features"] = [p.get("description", p.get("slug")) for p in manifest.get("permissions", [])]
                
                # Fetch GitHub stats
                stats = get_github_stats(owner, repo)
                if stats.get("stars") is not None:
                    module_data["stars"] = stats["stars"]
                if stats.get("downloads") is not None:
                    module_data["downloads"] = stats["downloads"]
                if stats.get("changelog"):
                    module_data["changelog"] = stats["changelog"]
                if stats.get("updated_at"):
                    module_data["updated_at"] = stats["updated_at"]
            
            # Set defaults
            module_data.setdefault("version", "0.0.0")
            module_data.setdefault("stars", 0)
            module_data.setdefault("downloads", 0)
            module_data.setdefault("verified", False)
            
            modules.append(module_data)
            print(f"    Added: {module_data['name']} v{module_data['version']}")
            
        except Exception as e:
            print(f"  Error processing {module_file.name}: {e}")
    
    # Build final registry
    registry = {
        "version": "1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "modules": modules
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\nGenerated {OUTPUT_FILE} with {len(modules)} modules")


if __name__ == "__main__":
    build_registry()
