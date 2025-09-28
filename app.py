import streamlit as st
import os, datetime, re
from db import get_db, init_db, now_iso, hash_password
from config import TIERS, SELLER_SUBSCRIPTIONS, PREVIEW_SEC, BID_WINDOW_SEC, PASSWORD_BLACKLIST

st.set_page_config(page_title="Beppa Sandbox v2", layout="wide")

if "db_init" not in st.session_state:
    init_db()
    st.session_state["db_init"] = True

st.title("Beppa Sandbox v2 (دموی ارتقاء یافته)")
tab_home, tab_seller, tab_items, tab_buyer, tab_admin = st.tabs(["خانه", "فروشنده", "آیتم‌ها", "خریدار", "ادمین"])

def save_file(uploaded, folder="uploads"):
    if not uploaded:
        return None
    base_dir = os.path.dirname(__file__)
    updir = os.path.join(base_dir, folder)
    os.makedirs(updir, exist_ok=True)
    path = os.path.join(updir, f"{datetime.datetime.utcnow().timestamp()}_{uploaded.name}")
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())
    return path

with tab_home:
    st.markdown(f"""    این نسخه شامل:
    - فرم فروشنده با **کدملی فقط عددی**، **دو نشانی (منزل/فروشگاه)**، **ایمیل**، **رمزعبور حداقل ۱۲ کاراکتر** با اعتبارسنجی، انتخاب **طرح اشتراک** و **تم فروشگاه**.
    - مدیریت آیتم: انتخاب دسته (کفش/ساعت)، **آپلود تا ۵ عکس** برای هر آیتم.
    - قوانین زمان‌بندی: پیش‌نمایش {PREVIEW_SEC}s و پنجرهٔ بید {BID_WINDOW_SEC}s (نمایشی).
    """)
    st.info("Sandbox برای نمایش منطق است؛ پرداخت و احراز هویت واقعی در این فاز انجام نمی‌شود.")

with tab_seller:
    st.header("ثبت فروشنده / ایجاد فروشگاه")
    with st.form("seller_form"):
        col1, col2 = st.columns(2)
        with col1:
            first = st.text_input("نام")
            codemeli = st.text_input("کدملی (فقط عدد)")
            home_addr = st.text_area("نشانی منزل")
            email = st.text_input("ایمیل")
            tier = st.selectbox("طرح اشتراک", list(SELLER_SUBSCRIPTIONS.keys()), format_func=lambda k: f"{k} ({'—' if SELLER_SUBSCRIPTIONS[k]['price'] is None else SELLER_SUBSCRIPTIONS[k]['price']} {SELLER_SUBSCRIPTIONS[k]['currency']})")
        with col2:
            last = st.text_input("نام خانوادگی")
            store_addr = st.text_area("نشانی فروشگاه")
            password = st.text_input("رمز عبور (حداقل ۱۲ کاراکتر)", type="password")
            theme = st.selectbox("تم فروشگاه", ["black","blue","white"])
            identity_key = st.text_input("شناسه یکتا (ایمیل/گذرنامه)", value="")

        submit = st.form_submit_button("ثبت فروشنده")

        if submit:
            errors = []
            if not (first and last): errors.append("نام و نام خانوادگی الزامی است.")
            if not codemeli or not codemeli.isdigit(): errors.append("کدملی باید فقط عدد باشد.")
            if not (home_addr and store_addr): errors.append("نشانی منزل و نشانی فروشگاه الزامی است.")
            if not email or "@" not in email: errors.append("ایمیل معتبر وارد کنید.")
            if not password or len(password) < 12: errors.append("رمز عبور باید حداقل ۱۲ کاراکتر باشد.")
            # basic password checks
            pw_lower = password.lower()
            name_parts = [first.lower(), last.lower(), email.split("@")[0].lower() if "@" in email else ""]
            if any(p and p in pw_lower for p in name_parts):
                errors.append("رمز عبور نباید شامل نام/نام‌خانوادگی/بخش نام کاربری ایمیل باشد.")
            if any(bad in pw_lower for bad in PASSWORD_BLACKLIST):
                errors.append("رمز عبور نباید شامل واژه‌های ساده/لغت‌نامه‌ای باشد.")
            if not identity_key: identity_key = email  # fallback

            if errors:
                for e in errors: st.error(e)
            else:
                conn = get_db()
                try:
                    conn.execute(
                        """INSERT INTO seller(first_name,last_name,codemeli,email,password_hash,home_address,store_address,
                               subscription_tier,theme,user_identity,created_at)
                               VALUES(?,?,?,?,?,?,?,?,?,?,?)""",                        (first,last,codemeli,email,hash_password(password),home_addr,store_addr,tier,theme,identity_key,now_iso())
                    )
                    conn.commit()
                    st.success("فروشنده ثبت شد.")
                except Exception as ex:
                    st.error(f"خطا در ثبت: {ex}")

with tab_items:
    st.header("ثبت آیتم برای فروشنده")
    conn = get_db()
    sellers = conn.execute("SELECT id, first_name||' '||last_name AS name FROM seller ORDER BY id DESC").fetchall()
    seller_map = {f"{r['id']} – {r['name']}": r["id"] for r in sellers}
    seller_sel = st.selectbox("انتخاب فروشنده", ["—"] + list(seller_map.keys()))
    if seller_sel != "—":
        with st.form("item_form"):
            category = st.selectbox("دسته", ["shoes","watches"])
            title = st.text_input("عنوان کالا")
            desc = st.text_area("توضیحات")
            price_min = st.number_input("حداقل قیمت (تومان)", min_value=0, step=10000)
            price_max = st.number_input("حداکثر قیمت (تومان)", min_value=0, step=10000)
            photos = st.file_uploader("عکس‌ها (حداکثر ۵ فایل)", accept_multiple_files=True, type=["png","jpg","jpeg","webp"])
            sub = st.form_submit_button("ثبت آیتم")
            if sub:
                if not title:
                    st.error("عنوان الزامی است.")
                elif photos and len(photos) > 5:
                    st.error("حداکثر ۵ عکس مجاز است.")
                else:
                    conn.execute(
                        "INSERT INTO item(seller_id,category,title,description,price_min,price_max,created_at) VALUES(?,?,?,?,?,?,?)",
                        (seller_map[seller_sel], category, title, desc, int(price_min), int(price_max), now_iso())
                    )
                    item_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
                    if photos:
                        for p in photos[:5]:
                            path = save_file(p)
                            conn.execute("INSERT INTO item_photo(item_id,blob_path,created_at) VALUES(?,?,?)",
                                         (item_id, path, now_iso()))
                    conn.commit()
                    st.success("آیتم ثبت شد و عکس‌ها ذخیره شدند.")

with tab_buyer:
    st.header("ثبت خریدار و Hold/Bid")
    with st.form("buyer_form"):
        b_first = st.text_input("نام ", key="b_first")
        b_last = st.text_input("نام خانوادگی ", key="b_last")
        b_addr = st.text_area("نشانی پستی برای ارسال", key="b_addr")
        bank_info = st.text_input("اطلاعات بانکی (نمایشی)")
        b_submitted = st.form_submit_button("ثبت خریدار")
        if b_submitted:
            if not (b_first and b_last and b_addr):
                st.error("نام، نام خانوادگی و نشانی الزامی است.")
            else:
                conn = get_db()
                conn.execute(
                    "INSERT INTO buyer(first_name,last_name,address,bank_info,created_at) VALUES(?,?,?,?,?)",
                    (b_first, b_last, b_addr, bank_info, now_iso())
                )
                conn.commit()
                st.success("خریدار ثبت شد.")

    st.subheader("Hold وجه")
    conn = get_db()
    buyers = conn.execute("SELECT id, first_name||' '||last_name AS name FROM buyer ORDER BY id DESC").fetchall()
    buyer_map = {f"{r['id']} – {r['name']}": r['id'] for r in buyers}
    buyer_sel = st.selectbox("انتخاب خریدار", ["—"] + list(buyer_map.keys()))
    if buyer_sel != "—":
        tier_code = st.selectbox("رده", list(TIERS.keys()), format_func=lambda k: TIERS[k]["name_fa"])
        if st.button("بلوکه وجه (Hold)"):
            t = TIERS[tier_code]
            conn.execute(
                "INSERT INTO hold(buyer_id,tier_code,hold_amount,status,created_at) VALUES(?,?,?,?,?)",
                (buyer_map[buyer_sel], tier_code, t["hold"], "active", now_iso())
            )
            conn.commit()
            st.success(f"Hold {t['hold']:,} تومان ثبت شد.")

    st.subheader("ثبت Bid روی آخرین آیتم‌ها")
    items = conn.execute("SELECT i.*, s.first_name||' '||s.last_name AS sname FROM item i JOIN seller s ON s.id=i.seller_id ORDER BY i.id DESC").fetchall()
    item_map = {f"{r['id']} – {r['category']} – {r['title']} – فروشنده: {r['sname']}": r for r in items}
    col1, col2 = st.columns(2)
    with col1:
        item_sel_key = st.selectbox("آیتم", list(item_map.keys()) if item_map else ["(آیتمی نیست)"])
    with col2:
        bid_amount = st.number_input("مبلغ Bid (تومان)", min_value=1, step=10000)

    if st.button("ثبت Bid"):
        if buyer_sel == "—":
            st.error("اول خریدار را انتخاب کنید.")
        elif not item_map:
            st.error("آیتمی برای Bid وجود ندارد.")
        else:
            r = item_map[item_sel_key]
            hold = conn.execute("SELECT * FROM hold WHERE buyer_id=? AND status='active' ORDER BY id DESC", (buyer_map[buyer_sel],)).fetchone()
            if not hold:
                st.error("ابتدا Hold انجام دهید.")
            elif bid_amount > hold['hold_amount']:
                st.error("مبلغ Bid از Hold فعال شما بیشتر است.")
            else:
                conn.execute("INSERT INTO bid(buyer_id,item_id,amount,created_at) VALUES(?,?,?,?)",
                             (buyer_map[buyer_sel], r['id'], int(bid_amount), now_iso()))
                conn.commit()
                st.success("Bid ثبت شد.")

with tab_admin:
    st.header("آمار کلی")
    conn = get_db()
    c1, c2, c3, c4, c5 = st.columns(5)
    sellers = conn.execute("SELECT COUNT(*) c FROM seller").fetchone()["c"]
    items = conn.execute("SELECT COUNT(*) c FROM item").fetchone()["c"]
    buyers = conn.execute("SELECT COUNT(*) c FROM buyer").fetchone()["c"]
    holds = conn.execute("SELECT COUNT(*) c FROM hold").fetchone()["c"]
    bids = conn.execute("SELECT COUNT(*) c FROM bid").fetchone()["c"]
    c1.metric("فروشنده‌ها", sellers)
    c2.metric("آیتم‌ها", items)
    c3.metric("خریداران", buyers)
    c4.metric("Holdها", holds)
    c5.metric("Bidها", bids)
