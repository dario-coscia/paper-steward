"""Verify the six annotated stage tags and their linear, six-commit history."""
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
TAGS = (
    'stage-0-broken-project', 'stage-1-project-instructions',
    'stage-2-maintenance-skill', 'stage-3-health-check',
    'stage-4-hooks', 'stage-5-complete-agent',
)
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
def main():
    if set(git('tag', '--list').splitlines()) != set(TAGS):
        raise ValueError('Expected exactly the six workshop tags')
    commits = []
    for tag in TAGS:
        if git('cat-file', '-t', tag) != 'tag':
            raise ValueError(f'{tag} is not annotated')
        commit = git('rev-parse', tag + '^{commit}')
        parents = git('rev-list', '--parents', '-n', '1', commit).split()[1:]
        if parents != (commits[-1:] if commits else []):
            raise ValueError(f'{tag} is not the next sequential commit')
        commits.append(commit)
        print(f'{tag}: {commit[:7]}')
    if len(set(commits)) != 6 or git('rev-parse', 'HEAD') != commits[-1]:
        raise ValueError('HEAD must be Stage 5 and all commits must be distinct')
    if git('rev-list', '--count', 'HEAD') != '6':
        raise ValueError('Expected exactly six commits')
    print('Six annotated tags, six sequential commits, HEAD at Stage 5: PASS')
if __name__ == '__main__':
    main()
