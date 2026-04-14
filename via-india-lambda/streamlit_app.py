import streamlit as st

st.set_page_config(page_title="Via India", page_icon="🌏", layout="centered")

# ---------------------------------------------------------------------------
# Access control — add allowed emails or domains here
# ---------------------------------------------------------------------------
ALLOWED_EMAILS = [
    "anton.theapp@gmail.com",
    "narsi.seelam@gmail.com",
    "narsijntu@gmail.com",
]
ALLOWED_DOMAINS = [
    # "yourcompany.com",
]


def is_authorized(email: str) -> bool:
    """Check if the logged-in user's email is allowed."""
    # If both lists are empty, allow everyone (open access)
    if not ALLOWED_EMAILS and not ALLOWED_DOMAINS:
        return True
    if email in ALLOWED_EMAILS:
        return True
    domain = email.split("@")[-1]
    if domain in ALLOWED_DOMAINS:
        return True
    return False

# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

def login_screen():
    """Render the login prompt for unauthenticated users."""
    st.title("🌏 Via India")
    st.subheader("Travel Companion Matching Platform")
    st.markdown(
        "Connect parents traveling internationally with colleagues "
        "willing to help — verified through your company email."
    )
    st.divider()
    st.markdown("#### Sign in to get started")
    st.button("🔐 Log in with Google", on_click=st.login, use_container_width=True)

# ---------------------------------------------------------------------------
# Main app (post-login)
# ---------------------------------------------------------------------------

def main_app():
    """Render the main application for authenticated users."""

    # -- Sidebar --
    with st.sidebar:
        st.image(
            "https://api.dicebear.com/7.x/initials/svg?seed="
            + st.user.name,
            width=80,
        )
        st.markdown(f"**{st.user.name}**")
        st.caption(st.user.email)
        st.divider()
        page = st.radio(
            "Navigate",
            ["🏠 Home", "✈️ My Requests", "🔍 Find Matches", "⚙️ Settings"],
            label_visibility="collapsed",
        )
        st.divider()
        st.button("Log out", on_click=st.logout, use_container_width=True)

    # -- Pages --
    if page == "🏠 Home":
        page_home()
    elif page == "✈️ My Requests":
        page_requests()
    elif page == "🔍 Find Matches":
        page_matches()
    elif page == "⚙️ Settings":
        page_settings()


# ---------------------------------------------------------------------------
# Page: Home
# ---------------------------------------------------------------------------

def page_home():
    st.title(f"Welcome, {st.user.name}! 👋")
    st.markdown(
        "Use **Via India** to find travel companions for your parents' "
        "international flights, or offer to help a colleague's family."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.info("**Need help?**\nPost a request for a travel companion.")
    with col2:
        st.success("**Offer help?**\nLet others know you're available.")

    st.divider()
    st.caption("More features coming soon — request management, matching, and notifications.")


# ---------------------------------------------------------------------------
# Page: My Requests (stub)
# ---------------------------------------------------------------------------

def page_requests():
    st.title("✈️ My Requests")
    st.info("This section will let you create, view, and manage your travel requests and offers.")
    st.caption("🚧 Under construction")


# ---------------------------------------------------------------------------
# Page: Find Matches (stub)
# ---------------------------------------------------------------------------

def page_matches():
    st.title("🔍 Find Matches")
    st.info("This section will display potential matches for your travel requests.")
    st.caption("🚧 Under construction")


# ---------------------------------------------------------------------------
# Page: Settings (stub)
# ---------------------------------------------------------------------------

def page_settings():
    st.title("⚙️ Settings")
    st.info("Profile and notification preferences will go here.")
    st.caption("🚧 Under construction")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if not st.user.is_logged_in:
    login_screen()
elif not is_authorized(st.user.email):
    st.error("⛔ Access denied. Your email is not authorized to use this app.")
    st.caption(f"Signed in as: {st.user.email}")
    st.button("Log out", on_click=st.logout)
else:
    main_app()
