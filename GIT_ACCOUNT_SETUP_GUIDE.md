# GitHub Multi-Account Setup & Management Guide
**Personal Account Isolation (AntiGravity) vs. Company Account (VS Code)**

This guide explains how your Mac is configured to seamlessly run both your **Company GitHub account** (in VS Code) and your **Personal GitHub account** (`shoaibmumtaz`, in Google AntiGravity) without any cross-account conflicts or credential mix-ups.

---

## 1. Core Architecture & Isolation

* **Company Work (VS Code):**
  * Operates completely untouched.
  * Uses your company credentials stored in macOS Keychain or VS Code's GitHub auth extension.
* **Personal Work (AntiGravity):**
  * All repositories under `~/Documents/Google_AntiGravity/` automatically route to your personal GitHub.
  * Author identity is locked to:
    * **Name:** `shoaibmumtaz`
    * **Email:** `shoaibmumtaz28@gmail.com`
  * Dedicated SSH key used: `~/.ssh/id_ed25519_personal`.
  * **Automatic URL Translation:** Even if you paste a standard web link (`https://github.com/...`), Git translates it to use your personal SSH key, preventing macOS Keychain from attempting to use your company login.

---

## 2. Active Configuration Details

| Component | Location / Setting | Purpose |
| :--- | :--- | :--- |
| **Personal SSH Key** | `~/.ssh/id_ed25519_personal` | Dedicated key registered to your `shoaibmumtaz` GitHub account |
| **Global Folder Rule** | `~/.gitconfig` (`includeIf`) | Tells Git: *If inside `Google_AntiGravity`, load personal rules* |
| **Personal Git Config** | `~/.gitconfig-antigravity` | Defines personal name, email, SSH command, and URL rewrite |
| **Local Backup System** | `./backup.sh` | Saves timestamped `.zip` and `.bundle` archives to `_Backups/` |

---

## 3. Step-by-Step: Connecting a Project to GitHub Manually

When you create a new repository on your personal GitHub account and want to link your local code:

1. **Add the remote URL** (HTTPS or SSH both work automatically):
   ```bash
   git remote add origin https://github.com/shoaibmumtaz/your-repo-name.git
   ```
2. **Push your code**:
   ```bash
   git push -u origin main
   ```

---

## 4. Step-by-Step: Verifying Current Account & Remotes

To verify which identity or destination any repository is currently using:

```bash
# Check commit author name & email:
git config user.name
git config user.email

# Check where the repository pushes to:
git remote -v
```

---

## 5. Step-by-Step: Changing Settings for a Single Project

If you ever need to override settings for just one specific project:

```bash
# Set a custom author name or email for ONLY this repository:
git config user.name "Your Name"
git config user.email "your-email@example.com"

# Change the remote GitHub repository URL:
git remote set-url origin https://github.com/shoaibmumtaz/new-repo.git

# Disconnect from GitHub entirely (reverts to local-only):
git remote remove origin
```

---

## 6. Step-by-Step: Managing or Modifying the Automatic Rule

Your personal settings are stored cleanly in dedicated configuration files:

* **View active global Git settings:**
  ```bash
  git config --global --list
  ```
* **Edit your personal AntiGravity settings (email, key, etc.):**
  ```bash
  nano ~/.gitconfig-antigravity
  ```
* **Disable the automatic folder rule completely in the future:**
  ```bash
  git config --global --unset "includeIf.gitdir:~/Documents/Google_AntiGravity/.path"
  ```

---

## 7. Local Backup Workflow Reminder

Per the project version control rules, local snapshots can be saved without pushing to GitHub:

```bash
./backup.sh "Describe what changed"    # Saves local commit, tag, and zip archive
./backup.sh list                       # Displays all saved backups
```
