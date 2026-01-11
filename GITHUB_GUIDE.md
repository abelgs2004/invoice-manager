# How to Push Your Invoice Project to GitHub

This guide will walk you through the steps to safely upload your project to GitHub.

## 1. Prerequisites: Install Git
Since Git is not currently installed on your system, you need to install it first.

1.  **Download Git for Windows**: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2.  **Run the Installer**:
    *   Click "Next" through most options.
    *   **Important**: When asked about "Adjusting your PATH environment", select **"Git from the command line and also from 3rd-party software"** (Recommended).
3.  **Verify Installation**:
    *   Open a **NEW** Command Prompt window (close any old ones).
    *   Type: `git --version`
    *   If it prints a version number (like `git version 2.43.0`), you are ready!

---

## 2. Safety Check (Already Done)
We have already configured your `.gitignore` file to ensure the following **sensitive files are NEVER uploaded**:
*   `credentials.json` (Google API Keys)
*   `token.json` (Your personal login session)
*   `.env` (Environment variables)
*   `storage/` (Your local database of invoices)
*   `*.pdf` (Any actual invoice files)

---

## 3. Create the Repository on GitHub
1.  Log in to [GitHub.com](https://github.com/).
2.  Click the **+** icon in the top-right corner and select **New repository**.
3.  **Repository name**: Enter `invoice-project` (or any name you like).
4.  **Description**: (Optional) e.g., "Automated Invoice Processing with AI".
5.  **Public/Private**: Choose **Private** if you want to keep your code hidden, or **Public** to share it.
6.  **Initialize this repository**: **DO NOT CHECK ANY OF THESE BOXES.** (Leave README, .gitignore, and License unchecked).
7.  Click **Create repository**.

---

## 4. Upload Your Code (First Time)
Copy and run these commands one by one in your Command Prompt inside the `C:\Users\georg\invoice-project` folder:

```cmd
REM 1. Initialize Git in your project folder
git init

REM 2. Add all your files (this respects the .gitignore rules)
git add .

REM 3. Save your first version
git commit -m "Initial setup: Invoice extraction with AI"

REM 4. Rename the default branch to 'main'
git branch -M main

REM 5. Link your local project to GitHub
REM REPLACE 'YOUR_USERNAME' with your actual GitHub username!
git remote add origin https://github.com/YOUR_USERNAME/invoice-project.git

REM 6. Push the code up!
git push -u origin main
```

*Note: You may be asked to sign in to GitHub in a browser window during the push step.*

---

## 5. How to Save Future Changes
Whenever you make changes to your code in the future, just run these three commands:

```cmd
git add .
git commit -m "Describe what you changed"
git push
```
