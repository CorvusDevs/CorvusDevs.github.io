# User Preferences

## Git Commits
- NEVER include "Co-Authored-By: Claude" or any Claude attribution in commit messages
- NEVER add Claude as a contributor on any GitHub repository
- All commits should appear as solely authored by the user

## Xcode Copy-Paste Bug
- Copying text from Claude responses in Xcode inserts invisible zero-width unicode characters
- This has broken secret names, URLs, and CLI commands in the past
- NEVER ask the user to copy-paste text from responses — always run commands directly or write to a file instead
