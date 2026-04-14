# Via India Project Specification

## 1. Project Goal
A serverless platform to match non-immigrant employees' parents needing travel assistance with colleagues willing to help, using automated matching, Google OAuth authentication, and a Streamlit web interface.

## 2. Components & Usage
- **AWS CDK**: Infrastructure as code for DynamoDB, Lambda, API Gateway, and supporting resources (3-stack architecture).
- **AWS Lambda (ARM64)**: Serverless compute running FastAPI + Mangum adapter.
- **Amazon API Gateway**: Regional REST API with API Key authentication.
- **FastAPI**: REST API for user, request, and matching logic.
- **DynamoDB**: Three tables (Users, Requests, Matches) with GSIs for efficient querying.
- **Streamlit**: Web UI hosted on Streamlit Community Cloud with Google OAuth login.
- **API Client**: `api_client.py` module connecting Streamlit to API Gateway with API Key auth.
- **Cloudflare Pages**: Static landing page at `via-india.me`.
- **Google Cloud Auth Platform**: OAuth 2.0 / OIDC for user authentication.

## 3. Functional Specs & Status

| Feature/Functionality                | Description                                                      | Status     |
|--------------------------------------|------------------------------------------------------------------|------------|
| **Authentication & Access**          |                                                                  |            |
| Google OAuth Login                   | Native Streamlit OIDC auth (st.login/st.logout/st.user)         | Completed  |
| App-Level Access Control             | ALLOWED_EMAILS / ALLOWED_DOMAINS whitelist in Streamlit          | Completed  |
| Auto User Lookup by Email            | Auto-detect existing user via `/users/email/{email}` on login    | Completed  |
| Auto User Verification               | Auto-verify users on login (Google OAuth = email verified)       | Completed  |
| **User Management**                  |                                                                  |            |
| User Registration                    | Signup with Google email, auto-register from Streamlit UI        | Completed  |
| User Domain Restriction              | Only allowed email domains/addresses can access the app          | Completed  |
| User Profile Display                 | Settings page shows name, email, user ID, verification status    | Completed  |
| **Travel Requests**                  |                                                                  |            |
| Create Travel Request/Offer          | Users can post need_help or offer_help requests via Streamlit    | Completed  |
| View User Requests                   | List all requests for the logged-in user with details            | Completed  |
| Get Request by ID                    | Retrieve a specific travel request via API                       | Completed  |
| **Matching**                         |                                                                  |            |
| Automated Matching                   | Find potential matches by route/dates via API                    | Completed  |
| Find Matches from Request            | "Find matches" button per request in Streamlit UI                | Completed  |
| Search Matches by Request ID         | Dedicated Find Matches page with request ID search               | Completed  |
| Match Consent Flow                   | Users accept/decline matches, mutual consent required            | TODO       |
| Match Status Updates                 | Update match status (pending, accepted, declined, completed)     | TODO       |
| Contact Exchange                     | Share contact info after mutual consent                          | TODO       |
| **Infrastructure**                   |                                                                  |            |
| CDK 3-Stack Architecture             | DatabaseStack, LayerStack, CdkStack deployed independently      | Completed  |
| API Gateway API Key Auth             | API Key + Usage Plan protecting all endpoints                    | Completed  |
| API Gateway Public Access            | Regional endpoint with open resource policy (no IAM auth)        | Completed  |
| Streamlit ↔ API Gateway Integration  | api_client.py sends x-api-key header on all requests             | Completed  |
| Streamlit Community Cloud Deployment | App auto-deploys from GitHub, secrets managed in Cloud settings  | Completed  |
| **Pending / Future**                 |                                                                  |            |
| Notifications                        | Notify users on match/updates (email/WhatsApp)                   | TODO       |
| Request/Match Completion             | Mark requests/matches as completed                               | TODO       |
| Error Handling & Feedback            | Report issues, submit feedback, post-travel status               | TODO       |
| Advanced Matching                    | Preferences, flexible dates, compatibility scoring               | TODO       |
| Custom Domain for Streamlit App      | Migrate to Lightsail/EC2 for custom domain + SSL (see notes)     | TODO       |

---

### Architecture

```
User → Google OAuth → Streamlit (Community Cloud)
                          ↓ (x-api-key header)
                   API Gateway (Regional, API Key auth)
                          ↓
                   Lambda (ARM64, FastAPI + Mangum)
                          ↓
                   DynamoDB (Users, Requests, Matches)
```

### Launch Notes

- **Streamlit Hosting**: Currently on Streamlit Community Cloud (free). Community Cloud does not support custom domains with SSL. When ready for launch, migrate to **AWS Lightsail** ($3.50/mo) or **EC2 free tier** to host Streamlit behind `via-india.me` (or `app.via-india.me`) with a proper SSL certificate via Let's Encrypt. Update Cloudflare DNS and Google OAuth redirect URIs accordingly.

**This file is the single source of truth for implementation status and planning. Update as features are completed or added.**
