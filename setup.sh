#!/bin/bash
set -e

RUBY_VERSION="3.3.11"

echo "==> Checking Homebrew..."
if ! command -v brew &>/dev/null; then
  echo "Homebrew not found. Installing..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "Homebrew found: $(brew --version | head -1)"
fi

echo ""
echo "==> Installing rbenv and ruby-build..."
brew install rbenv ruby-build 2>/dev/null || true

echo ""
echo "==> Setting up rbenv in shell..."
if ! grep -q 'rbenv init' ~/.zshrc 2>/dev/null; then
  echo 'eval "$(rbenv init -)"' >> ~/.zshrc
  echo "Added rbenv init to ~/.zshrc"
else
  echo "rbenv init already in ~/.zshrc"
fi
eval "$(rbenv init -)"

echo ""
echo "==> Installing Ruby $RUBY_VERSION..."
if rbenv versions --bare | grep -q "^${RUBY_VERSION}$"; then
  echo "Ruby $RUBY_VERSION already installed"
else
  rbenv install "$RUBY_VERSION"
fi
rbenv local "$RUBY_VERSION"
echo "Using Ruby $(ruby --version)"

echo ""
echo "==> Installing bundler..."
gem install bundler --no-document

echo ""
echo "==> Installing gem dependencies..."
bundle install

echo ""
echo "==> Setting up .env..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — please fill in your values"
else
  echo ".env already exists"
fi

echo ""
echo "================================================"
echo "  Setup complete!"
echo "================================================"
echo ""
echo "  1. Fill in your values in .env"
echo "  2. Run: bash run_server.sh"
echo "  3. Open: http://localhost:4000"
echo ""
