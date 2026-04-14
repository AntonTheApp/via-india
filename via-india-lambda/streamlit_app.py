import streamlit as st
import api_client as api

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

    # API health check
    st.divider()
    with st.expander("🔌 API Status"):
        try:
            status = api.health_check()
            st.success(f"API is **{status.get('status', 'unknown')}**")
        except Exception as e:
            st.error(f"API unreachable: {e}")


# ---------------------------------------------------------------------------
# Page: My Requests (stub)
# ---------------------------------------------------------------------------

def page_requests():
    st.title("✈️ My Requests")

    # --- Auto-detect or register user by Google email ---
    if "via_user" not in st.session_state:
        st.session_state.via_user = None

    # Try to auto-lookup user by email if not yet loaded
    if not st.session_state.via_user:
        with st.spinner("Looking up your account..."):
            lookup_email = st.user.email
            try:
                existing = api.get_user_by_email(lookup_email)
                if existing:
                    # Auto-verify if pending (Google OAuth already verified email)
                    if existing.get("verification_status") != "verified":
                        api.verify_user(existing["user_id"])
                        existing["verification_status"] = "verified"
                    st.session_state.via_user = existing
            except Exception as e:
                st.warning(f"⚠️ Could not look up account for `{lookup_email}`: {e}")

    if not st.session_state.via_user:
        st.info("No account found for your email. Register to get started.")
        with st.form("register_form"):
            reg_name = st.text_input("Full Name", value=st.user.name)
            reg_email = st.text_input("Email", value=st.user.email, disabled=True)
            reg_phone = st.text_input("Phone (optional)")
            submitted = st.form_submit_button("Register / Link Account")
            if submitted:
                try:
                    user = api.create_user(reg_name, st.user.email, reg_phone)
                    # Auto-verify since Google OAuth already confirmed the email
                    api.verify_user(user["user_id"])
                    user["verification_status"] = "verified"
                    st.session_state.via_user = user
                    st.success(f"Registered! Your user ID: `{user['user_id']}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        return

    user = st.session_state.via_user
    st.caption(f"User ID: `{user['user_id']}`")

    # --- View existing requests ---
    st.subheader("Your Requests")
    try:
        reqs = api.get_user_requests(user["user_id"])
        if reqs:
            for req in reqs:
                with st.expander(
                    f"{req['type']} — {req['route']['origin']} → {req['route']['destination']}  "
                    f"({req['status']})"
                ):
                    st.json(req)
                    if st.button("Find matches", key=f"match_{req['request_id']}"):
                        try:
                            matches = api.find_matches(req["request_id"])
                            st.write(f"**{matches['matches_found']}** potential match(es) found")
                            if matches["matches"]:
                                for m in matches["matches"]:
                                    st.write(
                                        f"- {m['type']} | {m['route']['origin']} → "
                                        f"{m['route']['destination']} | "
                                        f"Departs: {m['travel_dates'].get('departure', 'N/A')}"
                                    )
                            else:
                                st.caption("No matches yet — check back later.")
                        except Exception as e:
                            st.error(f"Matching error: {e}")
        else:
            st.caption("No requests yet. Create one below!")
    except Exception as e:
        st.error(f"Error loading requests: {e}")

    # --- Create new request ---
    st.divider()
    st.subheader("Create a New Request")
    with st.form("new_request_form"):
        req_type = st.selectbox("Type", ["need_help", "offer_help"])
        col_a, col_b = st.columns(2)
        with col_a:
            origin = st.text_input("Origin airport code", placeholder="DEL")
        with col_b:
            dest = st.text_input("Destination airport code", placeholder="JFK")
        departure = st.date_input("Departure date")
        return_date = st.date_input("Return date (optional)", value=None)
        flexible = st.checkbox("Flexible dates")

        if req_type == "need_help":
            st.markdown("**Passenger Details**")
            p_name = st.text_input("Passenger name")
            p_age = st.number_input("Age", min_value=1, max_value=120, value=60)
            p_needs = st.text_input("Special needs (optional)")
            p_langs = st.text_input("Languages (comma-separated)", value="Hindi, English")
        else:
            st.markdown("**Helper Details**")
            h_exp = st.text_input("Travel experience")
            h_langs = st.text_input("Languages (comma-separated)", value="Hindi, English")
            h_avail = st.text_input("Availability notes")

        create_btn = st.form_submit_button("Submit Request")
        if create_btn:
            try:
                passenger = None
                helper = None
                if req_type == "need_help":
                    passenger = {
                        "name": p_name,
                        "age": p_age,
                        "special_needs": p_needs,
                        "languages": [l.strip() for l in p_langs.split(",") if l.strip()],
                    }
                else:
                    helper = {
                        "experience": h_exp,
                        "languages": [l.strip() for l in h_langs.split(",") if l.strip()],
                        "availability": h_avail,
                    }
                result = api.create_request(
                    user_id=user["user_id"],
                    request_type=req_type,
                    origin=origin.upper(),
                    destination=dest.upper(),
                    departure=str(departure),
                    return_date=str(return_date) if return_date else None,
                    flexible=flexible,
                    passenger_details=passenger,
                    helper_details=helper,
                )
                st.success(f"Request created! ID: `{result['request_id']}`")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating request: {e}")


# ---------------------------------------------------------------------------
# Page: Find Matches (stub)
# ---------------------------------------------------------------------------

def page_matches():
    st.title("🔍 Find Matches")
    st.markdown("Enter a request ID to search for compatible travel companions.")

    request_id = st.text_input("Request ID")
    if st.button("Search", disabled=not request_id):
        try:
            result = api.find_matches(request_id)
            st.write(f"**{result['matches_found']}** match(es) found")
            if result["matches"]:
                for m in result["matches"]:
                    st.markdown(
                        f"- **{m['type']}** | {m['route']['origin']} → "
                        f"{m['route']['destination']} | "
                        f"Departs: {m['travel_dates'].get('departure', 'N/A')} | "
                        f"User: `{m['user_id']}`"
                    )
            else:
                st.info("No matches found yet. Check back later!")
        except Exception as e:
            st.error(f"Error: {e}")


# ---------------------------------------------------------------------------
# Page: Settings (stub)
# ---------------------------------------------------------------------------

def page_settings():
    st.title("⚙️ Settings")

    st.subheader("Your Profile")
    st.markdown(f"**Name:** {st.user.name}")
    st.markdown(f"**Email:** {st.user.email}")

    if st.session_state.get("via_user"):
        user = st.session_state.via_user
        st.markdown(f"**User ID:** `{user['user_id']}`")
        st.markdown(f"**Verification:** {user.get('verification_status', 'unknown')}")

    st.divider()
    st.caption("More settings (notification preferences, profile updates) coming soon.")


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
