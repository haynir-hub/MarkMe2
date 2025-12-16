# Branch Access Guide

## Overview

This repository now supports full access to all branches. You can view, checkout, and work with any branch available in the remote repository.

## Available Branches

The repository currently has the following branches:

- **main** - The main production branch
- **feature/two-phase-tracking** - Feature branch for two-phase tracking implementation
- **copilot/create-url-association-branch** - Branch for URL association feature

## Repository URL

The main repository URL is: `https://github.com/haynir-hub/MarkMe2`

You can access this URL to:
- View all branches
- Browse code in different branches
- Compare branches
- Create pull requests

## Working with Branches

### View All Branches

To see all available branches (local and remote):

```bash
git branch -a
```

### Checkout a Different Branch

To switch to the main branch:

```bash
git checkout main
```

To switch to the feature branch:

```bash
git checkout feature/two-phase-tracking
```

To create a local tracking branch from a remote branch:

```bash
git checkout -b feature/two-phase-tracking origin/feature/two-phase-tracking
```

### Update Branches

To fetch the latest changes from all branches:

```bash
git fetch origin
```

To pull changes for your current branch:

```bash
git pull
```

## Branch-Specific URLs

GitHub allows you to view specific branches directly via URL:

- **Main branch**: https://github.com/haynir-hub/MarkMe2/tree/main
- **Feature branch**: https://github.com/haynir-hub/MarkMe2/tree/feature/two-phase-tracking
- **Copilot branch**: https://github.com/haynir-hub/MarkMe2/tree/copilot/create-url-association-branch

## Viewing Branch Differences

To compare branches on GitHub:

```
https://github.com/haynir-hub/MarkMe2/compare/main...feature/two-phase-tracking
```

## Git Configuration

The repository is now configured to fetch all branches from the remote:

```
fetch = +refs/heads/*:refs/remotes/origin/*
```

This allows you to work with any branch without permission issues.

## Troubleshooting

### If you can't see a branch

Run:

```bash
git fetch origin
git branch -a
```

### If you need to reset to match the remote

```bash
git fetch origin
git reset --hard origin/branch-name
```

### View remote branches only

```bash
git branch -r
```

## Notes

- All branches are now accessible via the same remote origin
- No separate URLs are needed for different branches
- You can switch between branches freely using `git checkout`
- All branches share the same repository permissions
