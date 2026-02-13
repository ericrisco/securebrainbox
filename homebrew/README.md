# Homebrew Tap for SecureBrainBox

## Setup Instructions

To publish SecureBrainBox on Homebrew:

### 1. Create the tap repository

Create a new GitHub repo: `ericrisco/homebrew-tap`

### 2. Add the formula

Copy `securebrainbox.rb` to `Formula/securebrainbox.rb` in the new repo.

### 3. Update the SHA256 hash

When you create a release tag (e.g., v0.1.0):

```bash
# Download the tarball
curl -sL https://github.com/ericrisco/securebrainbox/archive/refs/tags/v0.1.0.tar.gz -o release.tar.gz

# Get SHA256
shasum -a 256 release.tar.gz

# Update the formula with the hash
```

### 4. Users can then install with:

```bash
brew tap ericrisco/tap
brew install securebrainbox
```

Or in one line:

```bash
brew install ericrisco/tap/securebrainbox
```

## Testing Locally

```bash
# Install from local formula
brew install --build-from-source ./securebrainbox.rb

# Or install HEAD (latest main branch)
brew install --HEAD ericrisco/tap/securebrainbox
```

## Updating

When releasing a new version:

1. Create a new git tag (e.g., v0.2.0)
2. Update the formula with new URL and SHA256
3. Push to homebrew-tap repo
4. Users update with: `brew upgrade securebrainbox`
