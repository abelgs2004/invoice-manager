# Deployment Guide: Invoice Manager on Koyeb

## Overview
This document outlines the procedures for deploying the Invoice Manager application to Koyeb. This platform is selected for its ease of use and student-friendly free tier.

## Prerequisites
1.  **GitHub Account**: Ensure the project is pushed to your remote repository.
2.  **Koyeb Account**: Active account at [koyeb.com](https://www.koyeb.com/).
3.  **Google Cloud Console Access**: Access to the project containing your Google Drive API credentials.
4.  **Local Credentials**: Access to your local `backend/credentials.json` file.

---

## Deployment Procedure

### Phase 1: Preparation of Credentials
Koyeb requires your Google Service Account credentials to authorize file uploads. These cannot be uploaded securely as a file, so they will be injected as an environment variable.

1.  Navigate to your local project directory: `invoice-project/backend/`.
2.  Open `credentials.json` in a text editor.
3.  Copy the entire content of this file to your clipboard. Ensure you capture the full JSON structure including the opening `{` and closing `}` braces.

### Phase 2: Application Creation on Koyeb
1.  Log in to the [Koyeb Dashboard](https://app.koyeb.com/).
2.  Select **Create App**.
3.  Under **Deployment Method**, select **GitHub**.
4.  Select the repository `invoice-manager` (or your specific repository name).
5.  Set the branch to `main`.

### Phase 3: Service Configuration
Use the following settings to configure the build and runtime environment:

**Build Settings**
*   **Builder**: Select **Dockerfile**.
*   **Location**: Root directory (default).

**Environment Variables**
This step is critical for application authentication.
1.  Expand the **Environment Variables** section.
2.  Click **Add Variable**.
3.  **Key**: `GOOGLE_CREDENTIALS_JSON`
4.  **Value**: Paste the JSON content copied in Phase 1.
5.  **Click "Add Variable" again.**
6.  **Key**: `GOOGLE_REDIRECT_URI`
7.  **Value**: `https://<YOUR_APP_NAME>.koyeb.app/oauth/callback` (You will know your app name in the next step, so you might need to come back and edit this, or guess it now. It usually follows the pattern `https://<app-name>-<org-name>.koyeb.app`. If unsure, deploy first, get the URL, then update this variable).

**Instance Settings**
*   **Instance Type**: Select **Nano** or **Free** (based on availability).
*   **App Name**: Enter a unique name (e.g., `invoice-manager-george`). This defines your public URL.

**Finalize**
*   Click **Deploy**.

### Phase 4: Google Cloud Authorization
Once deployment starts, Koyeb generates a public URL. You must authorize this URL in Google Cloud Console to permit OAuth logins.

1.  Wait for the deployment Status to change to **Healthy**.
2.  Copy your application URL (e.g., `https://invoice-manager-george.koyeb.app`).
3.  Navigate to [Google Cloud Console > Credentials](https://console.cloud.google.com/apis/credentials).
4.  Locate your **OAuth 2.0 Client ID** and click the **Edit** (pencil) icon.
5.  **Authorized JavaScript origins**:
    *   Add your Koyeb URL (e.g., `https://invoice-manager-george.koyeb.app`).
    *   *Note: Do not include a trailing slash.*
6.  **Authorized redirect URIs**:
    *   Add the callback URL: `https://invoice-manager-george.koyeb.app/oauth/callback`
7.  Click **Save**.

### Phase 5: Verification
1.  Navigate to your Koyeb App URL in a web browser.
2.  Verify the frontend interface loads correctly.
3.  Click **Connect Google Drive**.
4.  Complete the Google authentication flow.
5.  Upload a test file to verify end-to-end functionality.
