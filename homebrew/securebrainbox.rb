# Homebrew formula for SecureBrainBox
# 
# To use this formula:
# 1. Create repo: github.com/ericrisco/homebrew-tap
# 2. Copy this file to: Formula/securebrainbox.rb
# 3. Users install with: brew tap ericrisco/tap && brew install securebrainbox

class Securebrainbox < Formula
  include Language::Python::Virtualenv

  desc "100% local AI agent for Telegram with vector + graph memory"
  homepage "https://github.com/ericrisco/securebrainbox"
  url "https://github.com/ericrisco/securebrainbox/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256_HASH"
  license "MIT"
  head "https://github.com/ericrisco/securebrainbox.git", branch: "main"

  depends_on "python@3.11"

  # Core dependencies
  resource "click" do
    url "https://files.pythonhosted.org/packages/96/d3/f04c7bfcf5c1862a2a5b845c6b2b360488cf47af55dfa79c98f6a6bf98b5/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/11/23/814edf09ec6470d52022b9e95c23c1bef77f0bc451761e1a4f87cc21d795/rich-13.7.1.tar.gz"
    sha256 "9be308cb1fe2f1f57d67ce99e95af38a1e2bc71ad9813b0e247cf7ffbcc3a432"
  end

  # Add more resources as needed for dependencies

  def install
    virtualenv_install_with_resources
    
    # Install the package
    system libexec/"bin/pip", "install", "."
    
    # Create wrapper scripts
    (bin/"sbb").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python" -m src.cli.main "$@"
    EOS
    
    (bin/"securebrainbox").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python" -m src.cli.main "$@"
    EOS
  end

  def caveats
    <<~EOS
      SecureBrainBox requires Docker to run the AI services.

      To complete setup, run:
        sbb install

      This will guide you through:
        1. Telegram bot configuration
        2. Docker services setup
        3. AI model download (~4GB)

      For more information:
        https://github.com/ericrisco/securebrainbox
    EOS
  end

  test do
    assert_match "SecureBrainBox", shell_output("#{bin}/sbb --version")
  end
end
