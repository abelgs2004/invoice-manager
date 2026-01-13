# Deployment Guide: Invoice Manager on Google Cloud Run

## Overview
This document outlines the procedures for deploying the Invoice Manager application to Google Cloud Run. Cloud Run is a fully managed serverless platform that automatically scales containers.

## Prerequisites
1.  **Google Cloud Project**: A project with billing enabled.
    *   *Note*: New accounts receive $300 in free credits. Cloud Run includes a generous free tier (2 million requests/month).
2.  **GitHub Repository**: The application source code must be hosted on GitHub.
3.  **Required Credentials**:
    *   `credentials.json` content (Client ID and Secret).
    *   `GROQ_API_KEY` (from your local `.env`).

---

## Deployment Procedure

### Phase 1: Service Activation
Enable the necessary APIs to allow Google Cloud to build and run your application.

1.  Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Search for **Cloud Run API** and click **Enable**.
3.  Search for **Cloud Build API** and click **Enable**.

### Phase 2: Deployment Configuration
1.  Navigate to **Cloud Run** in the console.
2.  Click **Create Service**.
3.  Select **Continuously deploy new revisions from a source repository**.
4.  Click **Set up with Cloud Build**.
    *   **Repository Provider**: GitHub.
    *   **Repository**: Select `invoice-manager`.
    *   **Branch**: `^main$`
    *   **Build Type**: Select **Dockerfile** (path: `Dockerfile`).
    *   Click **Save**.

### Phase 3: Service Settings
Configure the runtime environment for the application.

**General Settings**
*   **Service Name**: `invoice-manager`.
*   **Region**: `us-central1` or `us-east1` (Recommended for tier availability).

**Authentication**
*   Select **Allow unauthenticated invocations**.
    *   *Requirement*: This setting makes the web application publicly accessible via the internet.

**Container Resources**
*   **CPU**: `1`
*   **Memory**: `512MiB`.
*   **Container Port**: `8000`.

**Environment Variables**
These variables are required for the application to function.
1.  Click the **Container, Networking, Security** dropdown.
2.  Select the **Variables & Secrets** tab.
3.  Add the following variables:
    *   `GOOGLE_CLIENT_ID`: *[Value from credentials.json]*
    *   `GOOGLE_CLIENT_SECRET`: *[Value from credentials.json]*
    *   `GROQ_API_KEY`: *[Your Groq API Key]*
    *   `GOOGLE_REDIRECT_URI`: Enter a placeholder (e.g., `http://localhost:8000`) for now. We will update this in the final phase.

4.  Click **Create**.

### Phase 4: Final Configuration
After the initial deployment completes (approx. 2-5 minutes), you must update the callback configuration with the live URL.

**Step 4.1: Retrieve Service URL**
1.  Copy the URL displayed at the top of the service dashboard (e.g., `https://invoice-manager-uc.a.run.app`).

**Step 4.2: Update Environment Variable**
1.  Click **Edit & Deploy New Revision**.
2.  Navigate to **Variables & Secrets**.
3.  Update `GOOGLE_REDIRECT_URI` to match your live URL pattern:
    *   Format: `https://<YOUR_SERVICE_URL>/oauth/callback`
    *   Example: `https://invoice-manager-uc.a.run.app/oauth/callback`
4.  Click **Deploy**.

**Step 4.3: Authorize Google Client**
1.  Navigate to **APIs & Services > Credentials**.
2.  Edit the active **OAuth 2.0 Client ID**.
3.  **Authorized JavaScript origins**:
    *   Add the service URL (e.g., `https://invoice-manager-uc.a.run.app`).
4.  **Authorized redirect URIs**:
    *   Add the full callback path (e.g., `https://invoice-manager-uc.a.run.app/oauth/callback`).
5.  Click **Save**.

---

## Verification
1.  Open the Service URL in a browser.
2.  Verify the application loads.
3.  Click **Connect Google Drive** to test the OAuth flow.
4.  Confirm successful redirection back to the application.

## Persistence Note
Cloud Run services are stateless.
*   **Files**: Local files (like `token.json` or temp uploads) are deleted when the instance scales to zero.
*   **Data Safety**: The application is designed to upload files directly to Google Drive, ensuring data persistence despite the stateless nature of the server.
