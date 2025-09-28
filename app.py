import streamlit as st
import os, datetime
from db import get_db, init_db, now_iso
from config import TIERS, SELLER_SUBSCRIPTIONS, PREVIEW_SEC, BID_WINDOW_SEC

st.set_page_config(page_title="Beppa Sandbox", layout="wide")

if "db_init" not in st.session_state:
    init_db()
    st.session_state["db_init"] = True

st.title("Beppa Sandbox (دموی ساده)")

tab_home, tab_seller, tab_buyer, tab_admin = st.tabs(["خانه", "فروشنده", "خریدار", "ادمین (Sandbox)"])

def seed_items_if_needed(conn):
    itc = conn.execute("SELECT COUNT(*) c FROM item").fetchone()["c"]
    if itc == 0:
        conn.executemany(
            "INSERT INTO item(category,title,description,price_min,price_max) VALUES(?,?,?,?,?)",
            [
                ("shoes", "Nike Air Demo", "کفش اصل (نمونه آزمایشی)", 500_000, 5_000_000),
                ("watches", "Seiko 5 Demo", "ساعت اصل (نمونه آزمایشی)", 5_000_000, 10_000_000),
            ]
        )
        conn.commit()

with tab_home:
    st.markdown(
        f"""        این یک **نمونهٔ ساده (Sandbox)** از هستهٔ منطقی Beppa است:
        - ثبت فروشنده با احراز هویت و **اشتراک** (Basic/Silver/Gold) و **یک فروشگاه** به‌ازای هر شناسه.
        - ثبت خریدار و انجام **بلوکه وجه (Hold)** بر اساس ردهٔ قیمتی (تومان) برای شرکت در مزایده.
        - ثبت **Bid** روی اقلام نمونه و **تسویه** (Capture/Release) شبیه‌سازی‌شده.
        """
    )
    st.caption(f"قوانین زمان‌بندی Sandbox: پیش‌نمایش {PREVIEW_SEC} ثانیه و پنجرهٔ بید {BID_WINDOW_SEC} ثانیه (نمایشی).")
    st.info("توجه: هیچ پرداخت واقعی انجام نمی‌شود. این محیط برای نمایش منطق است.")

with tab_seller:
    st.header("ثبت فروشنده و ایجاد فروشگاه")
    with st.form("seller_form"):
        first = st.text_input("نام")
        last = st.text_input("نام خانوادگی")
        codemeli = st.text_input("کدملی (اختیاری برای غیرایرانی)")
        addr = st.text_area("نشانی فیزیکی")
        identity_key = st.text_input("شناسه یکتا (مثلاً ایمیل یا شماره گذرنامه)")
        tier = st.selectbox("طرح اشتراک فروشنده", list(SELLER_SUBSCRIPTIONS.keys()))
        submitted = st.form_submit_button("ثبت فروشگاه")
        if submitted:
            if not (first and last and addr and identity_key):
                st.error("فیلدهای نام، نام خانوادگی، نشانی و شناسه یکتا الزامی‌اند.")
            else:
                conn = get_db()
                try:
                    conn.execute(
                        "INSERT INTO seller(first_name,last_name,codemeli,address,subscription_tier,user_identity,created_at) VALUES(?,?,?,?,?,?,?)",
                        (first, last, codemeli, addr, tier, identity_key, now_iso())
                    )
                    conn.commit()
                    st.success(
                        f"فروشگاه ثبت شد. طرح: {tier} – محدودیت‌ها: "
                        f"{SELLER_SUBSCRIPTIONS[tier]['auctions_per_week']} مزایده/هفته، "
                        f"{SELLER_SUBSCRIPTIONS[tier]['items_per_auction']} آیتم/مزایده"
                    )
                except Exception as e:
                    st.error(f"خطا: {e}")

with tab_buyer:
    st.header("ثبت خریدار و شرکت در مزایده")
    with st.form("buyer_form"):
        b_first = st.text_input("نام ", key="b_first")
        b_last = st.text_input("نام خانوادگی ", key="b_last")
        b_addr = st.text_area("نشانی پستی برای ارسال", key="b_addr")
        bank_info = st.text_input("اطلاعات بانکی (صرفاً جهت نمایش و تست در Sandbox)")
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

    st.subheader("انتخاب ردهٔ قیمتی و بلوکه وجه (Hold)")
    conn = get_db()
    seed_items_if_needed(conn)
    buyers = conn.execute("SELECT id, first_name||' '||last_name AS name FROM buyer ORDER BY id DESC").fetchall()
    buyer_map = {f"{r['id']} – {r['name']}": r["id"] for r in buyers}
    buyer_sel = st.selectbox("انتخاب خریدار", ["—"] + list(buyer_map.keys()))
    if buyer_sel != "—":
        tier_code = st.selectbox("رده", list(TIERS.keys()), format_func=lambda k: TIERS[k]['name_fa'])
        if st.button("بلوکه وجه (Hold)"):
            t = TIERS[tier_code]
            conn.execute(
                "INSERT INTO hold(buyer_id,tier_code,hold_amount,status,created_at) VALUES(?,?,?,?,?)",
                (buyer_map[buyer_sel], tier_code, t["hold"], "active", now_iso())
            )
            conn.commit()
            st.success(f"بلوکه وجه {t['hold']:,} تومان برای {t['name_fa']} انجام شد.")

    st.subheader("انتخاب آیتم و ثبت Bid")
    items = conn.execute("SELECT * FROM item ORDER BY id").fetchall()
    item_map = {f"{r['id']} – {r['category']} – {r['title']}": r for r in items}
    col1, col2 = st.columns(2)
    with col1:
        item_sel_key = st.selectbox("آیتم", list(item_map.keys()) if item_map else ["(آیتمی نیست)"])
    with col2:
        bid_amount = st.number_input("مبلغ Bid (تومان)", min_value=1, step=10000)

    if st.button("ثبت Bid"):
        if buyer_sel == "—":
            st.error("اول خریدار را انتخاب کنید.")
        elif not item_map:
            st.error("ابتدا آیتم‌های نمونه را بسازید.")
        else:
            r = item_map[item_sel_key]
            active_hold = conn.execute(
                "SELECT * FROM hold WHERE buyer_id=? AND status='active' ORDER BY id DESC",
                (buyer_map[buyer_sel],)
            ).fetchone()
            if not active_hold:
                st.error("ابتدا Hold انجام دهید.")
            elif bid_amount > active_hold['hold_amount']:
                st.error("مبلغ Bid از Hold فعال شما بیشتر است.")
            else:
                conn.execute(
                    "INSERT INTO bid(buyer_id,item_id,amount,created_at) VALUES(?,?,?,?)",
                    (buyer_map[buyer_sel], r['id'], int(bid_amount), now_iso())
                )
                conn.commit()
                st.success("Bid ثبت شد. (Sandbox)")

    st.subheader("تسویه (Capture/Release) – شبیه‌سازی")
    if st.button("تسویه آخرین مزایده خریدار انتخاب‌شده"):
        if buyer_sel == "—":
            st.error("خریدار را انتخاب کنید.")
        else:
            b_id = buyer_map[buyer_sel]
            last_bid = conn.execute("SELECT * FROM bid WHERE buyer_id=? ORDER BY id DESC", (b_id,)).fetchone()
            hold = conn.execute("SELECT * FROM hold WHERE buyer_id=? AND status='active' ORDER BY id DESC", (b_id,)).fetchone()
            if not last_bid or not hold:
                st.error("Bid یا Hold فعالی یافت نشد.")
            else:
                win_price = last_bid['amount']
                conn.execute("UPDATE hold SET status='captured' WHERE id=?", (hold['id'],))
                conn.commit()
                st.success(f"Capture به مبلغ {win_price:,} تومان انجام شد. باقی‌مانده Hold آزاد می‌شود (شبیه‌سازی).")

with tab_admin:
    st.header("ادمین Sandbox")
    conn = get_db()
    c1, c2, c3, c4 = st.columns(4)
    sellers = conn.execute("SELECT COUNT(*) c FROM seller").fetchone()["c"]
    buyers = conn.execute("SELECT COUNT(*) c FROM buyer").fetchone()["c"]
    holds = conn.execute("SELECT COUNT(*) c FROM hold").fetchone()["c"]
    bids = conn.execute("SELECT COUNT(*) c FROM bid").fetchone()["c"]
    c1.metric("فروشنده‌ها", sellers)
    c2.metric("خریداران", buyers)
    c3.metric("Holdها", holds)
    c4.metric("Bidها", bids)
