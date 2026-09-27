import streamlit as st
from api import register_user,login_user,get_feed,upload_post,delete_post


st.set_page_config(
    page_title="Frame",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ---------------- SESSION STATE ----------------

if "token" not in st.session_state:
    st.session_state.token = None

if "page" not in st.session_state:
    st.session_state.page = "Feed"


# ---------------- CUSTOM CSS ----------------

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    .stApp {
        background: #0b0b0b;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .brand {
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -1px;
        margin-bottom: 0;
    }

    .subtitle {
        color: #888;
        margin-top: -8px;
        font-size: 14px;
    }

    .post-card {
        background: #151515;
        border: 1px solid #262626;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 25px;
    }

    .user-name {
        font-size: 15px;
        font-weight: 600;
    }

    .post-date {
        font-size: 12px;
        color: #777;
    }

    .caption {
        font-size: 15px;
        margin-top: 12px;
        margin-bottom: 12px;
    }

    .divider {
        height: 1px;
        background: #252525;
        margin: 20px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------- LOGIN PAGE ----------------

def login_page():

    st.markdown(
        """
        <div style="text-align:center;margin-top:80px;">
            <div style="font-size:55px;">◈</div>
            <div class="brand">FRAME</div>
            <div class="subtitle">Share moments. Keep them yours.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    col1,col2,col3 = st.columns([1,1.5,1])

    with col2:

        tab1,tab2 = st.tabs(["Login","Create account"])


        # ---------------- LOGIN ----------------

        with tab1:

            email = st.text_input(
                "Email",
                key="login_email"
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            if st.button(
                "Login",
                use_container_width=True
            ):

                response = login_user(
                    email,
                    password
                )

                if response.status_code == 200:

                    data = response.json()

                    st.session_state.token = data["access_token"]

                    st.success("Logged in successfully.")

                    st.rerun()

                else:

                    st.error(
                        "Login failed. Check your email and password."
                    )


        # ---------------- REGISTER ----------------
        # ---------------- REGISTER ----------------

        with tab2:

            with st.form("register_form"):

                email = st.text_input(
                    "Email",
                    key="register_email"
                )

                register_password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password"
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    key="register_confirm_password"
                )

                create_account = st.form_submit_button(
                    "Create account",
                    use_container_width=True
                )

            if create_account:

                if register_password != confirm_password:

                    st.error("Passwords do not match.")

                elif not email or not register_password:

                    st.error("Please fill in all fields.")

                else:

                    response = register_user(
                        email,
                        register_password
                    )

                    if response.status_code == 201:

                        st.success(
                            "Account created. You can now log in."
                        )

                    else:

                        try:

                            detail = response.json().get(
                                "detail",
                                "Registration failed."
                            )

                        except:

                            detail = "Registration failed."

                        st.error(detail)
# ---------------- NAVBAR ----------------

def navbar():

    col1,col2,col3 = st.columns([2,3,2])

    with col1:

        st.markdown(
            """
            <div class="brand">FRAME</div>
            <div class="subtitle">Your visual space</div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        selected = st.radio(
            "",
            ["Feed","Upload"],
            horizontal=True,
            label_visibility="collapsed"
        )

        st.session_state.page = selected

    with col3:

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.token = None

            st.rerun()

    st.markdown(
        '<div class="divider"></div>',
        unsafe_allow_html=True
    )


# ---------------- FEED ----------------

def feed_page():

    st.markdown(
        """
        <div style="margin-bottom:25px;">
            <h1 style="margin-bottom:0;">Your feed</h1>
            <p style="color:#777;">
                Moments from the people you follow.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    response = get_feed(
        st.session_state.token
    )

    if response.status_code != 200:

        st.error(
            f"Could not load feed. Error {response.status_code}"
        )

        return

    data = response.json()

    posts = data.get(
        "posts",
        []
    )

    if not posts:

        st.info(
            "No posts yet. Upload your first moment."
        )

        return

    for post in posts:

        st.markdown(
            '<div class="post-card">',
            unsafe_allow_html=True
        )

        col1,col2 = st.columns([5,1])

        with col1:

            st.markdown(
                f"""
                <div class="user-name">
                    {post.get("email","Unknown")}
                </div>

                <div class="post-date">
                    {post.get("created_at","")}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            if post.get("is_owner"):

                if st.button(
                    "Delete",
                    key=f"delete_{post['id']}"
                ):

                    response = delete_post(
                        st.session_state.token,
                        post["id"]
                    )

                    if response.status_code == 200:

                        st.success(
                            "Post deleted."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Could not delete post."
                        )

        st.write("")

        file_type = post.get(
            "file_type"
        )

        url = post.get(
            "url"
        )

        if file_type == "video":

            st.video(url)

        else:

            st.image(
                url,
                use_container_width=True
            )

        caption = post.get(
            "caption",
            ""
        )

        if caption:

            st.markdown(
                f"""
                <div class="caption">
                    {caption}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ---------------- UPLOAD ----------------

def upload_page():

    st.markdown(
        """
        <div style="margin-bottom:25px;">
            <h1 style="margin-bottom:0;">Create a post</h1>
            <p style="color:#777;">
                Share an image or video with your feed.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1,col2,col3 = st.columns(
        [1,2,1]
    )

    with col2:

        uploaded_file = st.file_uploader(
            "Choose an image or video",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp",
                "mp4",
                "mov",
                "webm"
            ]
        )

        caption = st.text_area(
            "Caption",
            placeholder="Write something about this moment...",
            max_chars=500
        )

        if uploaded_file:

            st.markdown(
                "### Preview"
            )

            if uploaded_file.type.startswith(
                "video/"
            ):

                st.video(
                    uploaded_file
                )

            else:

                st.image(
                    uploaded_file,
                    use_container_width=True
                )

        if st.button(
            "Publish",
            use_container_width=True
        ):

            if uploaded_file is None:

                st.error(
                    "Please select a file first."
                )

            else:

                with st.spinner(
                    "Uploading..."
                ):

                    response = upload_post(
                        st.session_state.token,
                        uploaded_file,
                        caption
                    )

                if response.status_code == 200:

                    st.success(
                        "Your post has been published."
                    )

                    st.session_state.page = "Feed"

                    st.rerun()

                else:

                    try:

                        detail = response.json().get(
                            "detail",
                            "Upload failed."
                        )

                    except:

                        detail = "Upload failed."

                    st.error(detail)


# ---------------- MAIN ----------------

if st.session_state.token is None:

    login_page()

else:

    navbar()

    if st.session_state.page == "Feed":

        feed_page()

    elif st.session_state.page == "Upload":

        upload_page()