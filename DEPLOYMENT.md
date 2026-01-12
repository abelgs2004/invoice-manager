# Deployment Guide: Invoice Manager on Koyeb

This guide will walk you through deploying your Invoice Manager application for **free** using [Koyeb](https://www.koyeb.com/).

## Prerequisites
1.  **GitHub Account**: You must have the project pushed to your GitHub repository (which we have already done).
2.  **Koyeb Account**: Sign up for a free account at [koyeb.com](https://www.koyeb.com/).
3.  **Google Cloud Console Access**: You will need to assume the same Google account you used to set up the Drive API.

---

## Step 1: Prepare Your Google Credentials
Koyeb needs your Google Drive permissions to upload files. Since we cannot securely upload the `credentials.json` file, we will paste its content as a "secret" text.

1.  On your computer, navigate to your project folder: `c:\Users\georg\invoice-project\backend\`.
2.  Open the file named **`credentials.json`** using Notepad or any text editor.
3.  **Select All** (Ctrl+A) and **Copy** (Ctrl+C).
    *   *Keep this copied text ready for Step 3.*

---

## Step 2: Create a Koyeb App
1.  Log in to your [Koyeb Dashboard](https://app.koyeb.com/).
2.  Click the **"Create App"** button.
3.  **Select Deployment Method**: Choose **GitHub**.
4.  **Select Repository**:
    *   Search for your repository: `invoice-manager` (or `abelgs2004/invoice-manager`).
    *   Click to select it.
    *   Branch: `main`.

---

## Step 3: Configure the Service
1.  **Builder Configuration**:
    *   Make sure **"Dockerfile"** is selected (Not "Buildpack").
    *   It should automatically detect the `Dockerfile` in your root folder.

2.  **Environment Variables** (Crucial Step):
    *   Scroll down to the "Environment Variables" section.
    *   Click **"Add Variable"**.
    *   **Name**: `GOOGLE_CREDENTIALS_JSON`
    *   **Value**: *Paste the JSON content you copied in Step 1*.
    *   *Note: Ensure you paste the entire content, starting with `{` and ending with `}`.*

3.  **Instance Size**:
    *   Select **"Nano"** or **"Free"** (whatever is available in the free tier).

4.  **App Name**:
    *   Give your app a name, e.g., `invoice-manager-george`.
    *   This will determine your URL (e.g., `https://invoice-manager-george.koyeb.app`).

5.  Click **"Deploy"**.

---

## Step 4: Update Google Cloud Console
Your app will take 2-4 minutes to build. Once it is "Healthy" and "Running", Koyeb will show you a public URL (e.g., `https://your-app-name.koyeb.app`).

1.  Copy your new Koyeb URL.
2.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
3.  Navigate to **APIs & Services** > **Credentials**.
4.  Under "OAuth 2.0 Client IDs", click the pencil icon to edit your client.
5.  **Authorized JavaScript origins**:
    *   Click "Add URI".
    *   Paste your Koyeb URL (e.g., `https://your-app-name.koyeb.app`).
    *   *Note: Do not include a trailing slash `/`.*
6.  **Authorized redirect URIs**:
    *   Click "Add URI".
    *   Paste your Koyeb URL with `/oauth/callback` at the end on it.
    *   Example: `https://your-app-name.koyeb.app/oauth/callback`
7.  Click **Save**.

---

## Step 5: Final Test
1.  Open your Koyeb App URL in a browser.
2.  You should see your Invoice Manager frontend.
3.  Click **"Connect Google Drive"**.
4.  Complete the Google Login flow.
5.  Try uploading a file test!
