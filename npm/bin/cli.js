#!/usr/bin/env node

/**
 * SecureBrainBox npm CLI wrapper
 * 
 * This is a thin wrapper that installs/runs the Python-based CLI.
 * Usage: npx securebrainbox install
 */

import { spawn, execSync } from 'child_process';
import { existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const INSTALL_DIR = join(homedir(), '.securebrainbox', 'app');
const SBB_BIN = join(homedir(), '.local', 'bin', 'sbb');
const args = process.argv.slice(2);

// Colors for terminal
const colors = {
  reset: '\x1b[0m',
  blue: '\x1b[34m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  dim: '\x1b[2m'
};

function log(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function checkInstallation() {
  return existsSync(INSTALL_DIR) && existsSync(SBB_BIN);
}

async function runInstaller() {
  log('blue', '🧠 SecureBrainBox');
  log('dim', 'Installing via curl script...\n');

  return new Promise((resolve, reject) => {
    const installer = spawn('bash', ['-c', 
      'curl -sSL https://raw.githubusercontent.com/ericrisco/securebrainbox/main/scripts/install.sh | bash'
    ], { 
      stdio: 'inherit',
      shell: true
    });

    installer.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Installation failed with code ${code}`));
      }
    });

    installer.on('error', reject);
  });
}

async function runSbb(args) {
  return new Promise((resolve) => {
    const sbb = spawn(SBB_BIN, args, {
      stdio: 'inherit',
      cwd: process.cwd()
    });

    sbb.on('close', (code) => {
      resolve(code);
    });

    sbb.on('error', (err) => {
      if (err.code === 'ENOENT') {
        log('red', '❌ sbb command not found');
        log('dim', 'Try adding ~/.local/bin to your PATH');
      } else {
        log('red', `Error: ${err.message}`);
      }
      resolve(1);
    });
  });
}

async function main() {
  try {
    // Check if already installed
    const installed = await checkInstallation();

    if (!installed) {
      log('yellow', '⚠️  SecureBrainBox not installed locally.\n');
      
      // Auto-install
      await runInstaller();
      
      console.log('');
    }

    // If no args or install was requested, we're done after installation
    if (args.length === 0) {
      if (!installed) {
        log('green', '\n✅ Installation complete!');
        log('dim', 'Run: sbb install');
      } else {
        // Show help
        await runSbb(['--help']);
      }
      return;
    }

    // Run the sbb command with args
    const exitCode = await runSbb(args);
    process.exit(exitCode);

  } catch (error) {
    log('red', `Error: ${error.message}`);
    process.exit(1);
  }
}

main();
