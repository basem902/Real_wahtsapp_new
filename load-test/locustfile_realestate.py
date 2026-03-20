"""
اختبار حمل شامل لمنصة Smart Real Estate Agent (smartsapp.net)
يعتمد على الـ Endpoints الفعلية من الكود المصدري
Auth: Supabase Cookie-based (sb-XXX-auth-token)
"""

import json
import logging
import os
import random
import time
from datetime import datetime, timedelta

import gevent
import requests
from faker import Faker
from locust import HttpUser, task, between, events, tag

# ─── الإعدادات ───────────────────────────────────────────────
BASE_URL = os.getenv("TARGET_URL", "https://smartsapp.net")
fake = Faker("ar_SA")
fake_en = Faker("en_US")

# ─── Logging ─────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f"errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

logger = logging.getLogger("loadtest")
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

# ─── Supabase Auth ───────────────────────────────────────────
SUPABASE_URL = "https://rwkncijrbvarpjsuvazx.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ3a25jaWpyYnZhcnBqc3V2YXp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4OTE4MTQsImV4cCI6MjA4NzQ2NzgxNH0.FfUYB9nWHSIXpl34X48KALDK1GPHXYOEzy_W8CjLf-w"
TEST_EMAIL = os.getenv("TEST_EMAIL", "basemaborimas@gmail.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "Zxcvb123asd@1@")
ORG_SLUG = "\u0628\u0627\u0633\u0645-\u0627\u0644\u062d\u0631\u0628\u064a-mmhnpl3t"

# Supabase ref (extracted from URL)
SUPABASE_REF = "rwkncijrbvarpjsuvazx"
COOKIE_PREFIX = f"sb-{SUPABASE_REF}-auth-token"

# ─── بيانات مشتركة ───────────────────────────────────────────
PROPERTY_TYPES = ["شقة", "فيلا", "أرض", "مكتب", "محل تجاري", "عمارة", "دوبلكس", "استوديو"]
LISTING_TYPES = ["sale", "rent"]
CITIES = ["الرياض", "جدة", "الدمام", "مكة", "المدينة", "الخبر", "تبوك", "أبها"]
AREAS = ["حي النرجس", "حي الياسمين", "حي العليا", "حي السلامة", "حي الروضة", "حي المروج"]


def random_phone():
    return f"+9665{random.randint(10000000, 99999999)}"


def random_property_data():
    prop_type = random.choice(PROPERTY_TYPES)
    city = random.choice(CITIES)
    area = random.choice(AREAS)
    return {
        "title": f"{prop_type} في {area} - {city}",
        "description": fake.paragraph(nb_sentences=3),
        "property_type": prop_type,
        "listing_type": random.choice(LISTING_TYPES),
        "price": random.randint(200000, 5000000),
        "area_size": random.randint(80, 1000),
        "bedrooms": random.randint(1, 8),
        "bathrooms": random.randint(1, 5),
        "city": city,
        "district": area,
        "address": f"{area}، {city}",
        "features": random.sample(
            ["مسبح", "حديقة", "مصعد", "موقف سيارات", "غرفة خادمة", "مجلس", "تكييف مركزي"],
            k=random.randint(2, 4),
        ),
    }


def random_whatsapp_message():
    messages = [
        "السلام عليكم، أبي شقة في الرياض",
        "كم سعر الفيلا؟",
        "عندكم أراضي في جدة؟",
        "أبي أحجز موعد معاينة",
        "وش المساحة؟",
        "هل فيه تقسيط؟",
        "أبي شقة 3 غرف بالدمام",
        "السعر قابل للتفاوض؟",
        "متى أقدر أزور العقار؟",
        "أرسلوا لي التفاصيل",
        f"أبي عقار ميزانيتي {random.randint(200, 900)} ألف",
    ]
    return random.choice(messages)


# ═══════════════════════════════════════════════════════════════
#  Supabase Auth — Cookie-based login
# ═══════════════════════════════════════════════════════════════
_cached_session = None
_session_expires_at = 0


def get_supabase_session():
    """Login via Supabase REST and cache the FULL session globally."""
    global _cached_session, _session_expires_at

    now = time.time()
    if _cached_session and now < _session_expires_at - 60:
        return _cached_session

    try:
        resp = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            timeout=15,
        )
        if resp.status_code == 200:
            _cached_session = resp.json()
            _session_expires_at = _cached_session.get("expires_at", now + 3500)
            logger.info("Supabase login successful")
            return _cached_session
        else:
            logger.error(f"Supabase login failed: {resp.status_code}")
            return None
    except Exception as e:
        logger.error(f"Supabase login exception: {e}")
        return None


def build_auth_cookies(session_data):
    """Build Supabase SSR-compatible cookies from the full session response."""
    cookie_value = json.dumps(session_data, separators=(",", ":"))

    CHUNK_SIZE = 3180
    cookies = {}

    if len(cookie_value) <= CHUNK_SIZE:
        cookies[COOKIE_PREFIX] = cookie_value
    else:
        chunks = [cookie_value[i:i + CHUNK_SIZE] for i in range(0, len(cookie_value), CHUNK_SIZE)]
        for i, chunk in enumerate(chunks):
            cookies[f"{COOKIE_PREFIX}.{i}"] = chunk

    return cookies


# ═══════════════════════════════════════════════════════════════
#  سيناريو 1: زائر الكتالوج — وزن 50
# ═══════════════════════════════════════════════════════════════
class CatalogVisitor(HttpUser):
    """زائر عادي يتصفح الصفحات العامة — بدون تسجيل دخول"""

    weight = 50
    wait_time = between(1, 3)
    host = BASE_URL

    @tag("public", "health")
    @task(5)
    def health_check(self):
        with self.client.get("/api/health", name="[Public] Health", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 429:
                resp.success()
                gevent.sleep(random.uniform(0.5, 1.0))
            else:
                resp.failure(f"Health: {resp.status_code}")

    @tag("public", "plans")
    @task(3)
    def view_plans(self):
        self.client.get("/api/plans", name="[Public] Plans")

    @tag("public", "ssr")
    @task(10)
    def browse_pages(self):
        pages = ["/", "/pricing", "/features"]
        page = random.choice(pages)
        with self.client.get(page, name=f"[SSR] {page}", catch_response=True) as resp:
            if resp.status_code in (200, 304, 404):
                resp.success()
            elif resp.status_code == 429:
                resp.success()
                gevent.sleep(random.uniform(0.5, 1.0))
            else:
                resp.failure(f"Page {page}: {resp.status_code}")

    @tag("public", "leads")
    @task(4)
    def submit_lead(self):
        lead = {
            "orgSlug": ORG_SLUG,
            "name": fake.name(),
            "phone": random_phone(),
            "email": fake_en.email(),
            "budget_min": random.randint(100000, 500000),
            "budget_max": random.randint(500000, 3000000),
            "preferred_area": random.choice(AREAS),
            "property_type": random.choice(PROPERTY_TYPES),
            "bedrooms": random.randint(1, 6),
            "notes": fake.sentence(),
        }
        with self.client.post(
            "/api/leads/public",
            json=lead,
            headers={"Content-Type": "application/json", "Origin": BASE_URL},
            name="[Public] Submit Lead",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201):
                resp.success()
            elif resp.status_code == 429:
                resp.success()
                gevent.sleep(random.uniform(0.5, 1.0))
            else:
                resp.failure(f"Lead: {resp.status_code}")
                logger.warning(f"Lead failed: {resp.text[:200]}")

    @tag("public", "appointments")
    @task(2)
    def book_appointment(self):
        tomorrow = (datetime.now() + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
        appt = {
            "orgSlug": ORG_SLUG,
            "propertyId": None,
            "name": fake.name(),
            "phone": random_phone(),
            "date": tomorrow,
            "time": f"{random.randint(9, 17):02d}:00",
            "notes": fake.sentence(),
        }
        with self.client.post(
            "/api/appointments/public",
            json=appt,
            headers={"Content-Type": "application/json", "Origin": BASE_URL},
            name="[Public] Book Appointment",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201, 400):
                resp.success()
            elif resp.status_code == 429:
                resp.success()
                gevent.sleep(random.uniform(0.5, 1.0))
            else:
                resp.failure(f"Appointment: {resp.status_code}")


# ═══════════════════════════════════════════════════════════════
#  سيناريو 2: مدير الشركة — وزن 30
# ═══════════════════════════════════════════════════════════════
class CompanyAdmin(HttpUser):
    """مدير شركة عقارية — مسجّل الدخول عبر Supabase cookies"""

    weight = 30
    wait_time = between(2, 5)
    host = BASE_URL

    def on_start(self):
        session = get_supabase_session()
        self.auth_cookies = {}
        self.is_authenticated = False

        if session:
            self.auth_cookies = build_auth_cookies(session)
            self.is_authenticated = True
            logger.info("CompanyAdmin authenticated via cookies")
        else:
            logger.warning("CompanyAdmin: no auth session")

    def _get(self, path, name):
        if not self.is_authenticated:
            return None
        with self.client.get(
            path, cookies=self.auth_cookies, name=name, catch_response=True
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 429:
                resp.success()
                gevent.sleep(random.uniform(0.5, 1.0))
            elif resp.status_code == 401:
                resp.failure("Unauthorized")
                session = get_supabase_session()
                if session:
                    self.auth_cookies = build_auth_cookies(session)
            else:
                resp.failure(f"{name}: {resp.status_code}")
            return resp

    def _post(self, path, data, name):
        if not self.is_authenticated:
            return None
        with self.client.post(
            path,
            json=data,
            cookies=self.auth_cookies,
            headers={"Content-Type": "application/json", "Origin": BASE_URL},
            name=name,
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201):
                resp.success()
            elif resp.status_code == 429:
                resp.success()
                gevent.sleep(random.uniform(0.5, 1.0))
            elif resp.status_code == 401:
                resp.failure("Unauthorized")
            else:
                resp.failure(f"{name}: {resp.status_code}")
            return resp

    # ─── العقارات ─────────────────────────────────────────
    @tag("auth", "properties")
    @task(8)
    def list_properties(self):
        page = random.randint(1, 3)
        self._get(f"/api/properties?page={page}&pageSize=10", "[Admin] List Properties")

    @tag("auth", "properties")
    @task(5)
    def search_properties(self):
        q = random.choice(["شقة", "فيلا", "أرض", "الرياض", "جدة"])
        self._get(f"/api/properties?search={q}&pageSize=10", "[Admin] Search Properties")

    @tag("auth", "properties")
    @task(3)
    def add_property(self):
        self._post("/api/properties", random_property_data(), "[Admin] Add Property")

    # ─── الإحصائيات ───────────────────────────────────────
    @tag("auth", "analytics")
    @task(6)
    def view_stats(self):
        self._get("/api/analytics/stats", "[Admin] Stats")

    @tag("auth", "analytics")
    @task(3)
    def view_ai_analytics(self):
        days = random.choice([7, 30, 90])
        self._get(f"/api/analytics/ai?days={days}", "[Admin] AI Analytics")

    @tag("auth", "analytics")
    @task(3)
    def view_team_performance(self):
        self._get("/api/analytics/team-performance", "[Admin] Team Performance")

    @tag("auth", "analytics")
    @task(2)
    def view_marketer_analytics(self):
        self._get("/api/analytics/marketers", "[Admin] Marketer Analytics")

    # ─── الإشعارات والإعدادات ─────────────────────────────
    @tag("auth", "notifications")
    @task(5)
    def check_notifications(self):
        self._get("/api/notifications?page=1&pageSize=20", "[Admin] Notifications")

    @tag("auth", "settings")
    @task(2)
    def view_settings(self):
        self._get("/api/settings", "[Admin] Settings")

    @tag("auth", "team")
    @task(2)
    def view_team(self):
        self._get("/api/team", "[Admin] Team")

    # ─── الاشتراكات ───────────────────────────────────────
    @tag("auth", "billing")
    @task(2)
    def view_subscription(self):
        self._get("/api/subscriptions/current", "[Admin] Subscription")

    @tag("auth", "billing")
    @task(1)
    def view_billing_roi(self):
        self._get("/api/billing/roi", "[Admin] ROI")

    # ─── البوت والمعرفة ───────────────────────────────────
    @tag("auth", "auto-responses")
    @task(3)
    def list_auto_responses(self):
        self._get("/api/auto-responses?page=1&pageSize=10", "[Admin] Auto Responses")

    @tag("auth", "knowledge")
    @task(3)
    def list_knowledge(self):
        self._get("/api/knowledge?page=1&pageSize=10", "[Admin] Knowledge")

    @tag("auth", "bot")
    @task(2)
    def view_bot_settings(self):
        self._get("/api/bot-settings", "[Admin] Bot Settings")

    # ─── واتساب ───────────────────────────────────────────
    @tag("auth", "whatsapp")
    @task(4)
    def whatsapp_status(self):
        self._get("/api/whatsapp/status", "[Admin] WhatsApp Status")

    # ─── Backup ───────────────────────────────────────────
    @tag("auth", "backup")
    @task(1)
    def view_backup_history(self):
        self._get("/api/backup/history", "[Admin] Backup History")


# ═══════════════════════════════════════════════════════════════
#  سيناريو 3: بوت الواتساب — وزن 20
# ═══════════════════════════════════════════════════════════════
class WhatsAppBot(HttpUser):
    """محاكاة رسائل واتساب واردة عبر الـ Webhook"""

    weight = 20
    wait_time = between(0.5, 2)
    host = BASE_URL

    def on_start(self):
        self.sender_numbers = [random_phone() for _ in range(20)]
        self.msg_counter = 0

    def _webhook_payload(self, sender, message):
        self.msg_counter += 1
        return {
            "event": "messages.upsert",
            "data": {
                "messages": [
                    {
                        "key": {
                            "remoteJid": f"{sender.replace('+', '')}@s.whatsapp.net",
                            "fromMe": False,
                            "id": f"LT_{self.msg_counter}_{random.randint(10000, 99999)}",
                        },
                        "message": {"conversation": message},
                        "messageTimestamp": str(int(time.time())),
                        "pushName": fake.name(),
                    }
                ]
            },
            "instance_id": "loadtest_instance",
        }

    @tag("webhook", "whatsapp")
    @task(10)
    def incoming_message(self):
        sender = random.choice(self.sender_numbers)
        payload = self._webhook_payload(sender, random_whatsapp_message())
        with self.client.post(
            "/api/webhook",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="[Webhook] Message",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201, 400, 403):
                resp.success()
            elif resp.status_code == 429:
                resp.success()
                gevent.sleep(random.uniform(0.5, 1.0))
            else:
                resp.failure(f"Webhook: {resp.status_code}")

    @tag("webhook", "whatsapp")
    @task(3)
    def burst_messages(self):
        sender = random.choice(self.sender_numbers)
        for msg in ["السلام عليكم", "أبي شقة بالرياض", "ميزانيتي 500 ألف", "3 غرف نوم"]:
            payload = self._webhook_payload(sender, msg)
            with self.client.post(
                "/api/webhook",
                json=payload,
                headers={"Content-Type": "application/json"},
                name="[Webhook] Burst",
                catch_response=True,
            ) as resp:
                if resp.status_code in (200, 201, 400, 403):
                    resp.success()
                elif resp.status_code == 429:
                    resp.success()
                    gevent.sleep(random.uniform(0.5, 1.0))
                else:
                    resp.failure(f"Burst: {resp.status_code}")

    @tag("public", "health")
    @task(2)
    def check_health(self):
        self.client.get("/api/health", name="[Bot] Health")


# ═══════════════════════════════════════════════════════════════
#  Event Hooks
# ═══════════════════════════════════════════════════════════════
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    response = kwargs.get("response", None)
    status = getattr(response, "status_code", None) if response else None
    if exception:
        # Skip logging 429 rate-limit exceptions — only log real server errors
        if status == 429:
            return
        logger.error(f"EXCEPTION | {request_type} {name} | {exception}")
    elif status and status >= 500:
        logger.error(f"SERVER ERROR | {request_type} {name} | {status} | {response_time:.0f}ms")
    elif response_time > 5000:
        logger.warning(f"SLOW | {request_type} {name} | {response_time:.0f}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logger.info("=" * 60)
    logger.info(f"Load test started — {datetime.now()}")
    logger.info(f"Target: {BASE_URL}")
    logger.info("=" * 60)
    # Pre-warm the session
    get_supabase_session()


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logger.info(f"Load test ended — {datetime.now()}")
