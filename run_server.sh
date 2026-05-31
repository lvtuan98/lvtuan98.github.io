#!/bin/bash

# Load .env if it exists
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# Substitute env variables into a temporary config
cp _config.yml _config_local.yml
sed -i '' "s|GOOGLE_SCHOLAR_ID|${GOOGLE_SCHOLAR_ID:-GOOGLE_SCHOLAR_ID}|g" _config_local.yml
sed -i '' "s|AUTHOR_EMAIL|${AUTHOR_EMAIL:-AUTHOR_EMAIL}|g" _config_local.yml
sed -i '' "s|AUTHOR_GITHUB|${AUTHOR_GITHUB:-AUTHOR_GITHUB}|g" _config_local.yml
sed -i '' "s|AUTHOR_LINKEDIN|${AUTHOR_LINKEDIN:-AUTHOR_LINKEDIN}|g" _config_local.yml
sed -i '' "s|AUTHOR_ORCID|${AUTHOR_ORCID:-AUTHOR_ORCID}|g" _config_local.yml
sed -i '' "s|CHAT_BACKEND_URL|${CHAT_BACKEND_URL:-http://localhost:8000}|g" _config_local.yml

trap "rm -f _config_local.yml" EXIT

case "${1:-rbenv}" in
  docker)
    docker run --rm \
      -v "$PWD:/srv/jekyll" \
      -p 4000:4000 \
      jekyll/jekyll:4 \
      bash -c "bundle install && jekyll serve --host 0.0.0.0 --config _config_local.yml --watch --force_polling"
    ;;
  rbenv)
    eval "$(rbenv init -)"
    bundle exec jekyll serve --config _config_local.yml --watch
    ;;
  *)
    echo "Usage: bash run_server.sh [rbenv|docker]"
    exit 1
    ;;
esac
