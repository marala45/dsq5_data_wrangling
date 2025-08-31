from pathlib import Path
    import subprocess, sys

    def test_scaffold_creates_dirs(tmp_path, monkeypatch):
        # run step01 in a temp cwd
        monkeypatch.chdir(tmp_path)
        (tmp_path / "configs").mkdir()
        (tmp_path / "logs/013").mkdir(parents=True)
        (tmp_path / "reports/013").mkdir(parents=True)
        (tmp_path / "results/013").mkdir(parents=True)
        (tmp_path / "configs/013_audit.yaml").write_text(
            "input_glob: 'data/013/input/*.csv'\nreport_dir: 'reports/013'\nresults_dir: 'results/013'\n",
            encoding="utf-8"
        )
        rc = subprocess.call([sys.executable, "-c", "import scripts.XXXXXXXX"], cwd=tmp_path)
        # keep as placeholder; in your repo, import step01 module or call via path

# (You can replace this with a simpler check later; the point is to keep a test entry ready.)
