#!/bin/bash
set -euo pipefail

# Deploy docs/ to the gh-pages branch

git fetch
if ! git switch gh-pages; then
  git switch -c gh-pages
fi
rsync -a --delete docs/ .

git add .
if git commit -m "braggard: $(date +%F)"; then
  echo "Committed deployment"
else
  echo "No changes to commit"
fi

git push origin gh-pages
