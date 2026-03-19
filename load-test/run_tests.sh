#!/bin/bash
# ══════════════════════════════════════════════════════════════
#  اختبار حمل منصة Smart Real Estate Agent
#  smartsapp.net
# ══════════════════════════════════════════════════════════════

set -e

# الألوان
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# الإعدادات
TARGET_URL="${TARGET_URL:-https://smartsapp.net}"
RESULTS_DIR="results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  اختبار حمل منصة الواتس العقاري — Smart Real Estate Agent${NC}"
echo -e "${BLUE}  الهدف: ${TARGET_URL}${NC}"
echo -e "${BLUE}  الوقت: $(date)${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"

# إنشاء مجلد النتائج
mkdir -p "$RESULTS_DIR"

# ─── التحقق من المتطلبات ─────────────────────────────────────
echo -e "\n${YELLOW}[1/5] التحقق من المتطلبات...${NC}"
command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || {
    echo -e "${RED}خطأ: Python غير مثبت${NC}"
    exit 1
}

PYTHON=$(command -v python3 || command -v python)

$PYTHON -c "import locust" 2>/dev/null || {
    echo -e "${YELLOW}تثبيت المكتبات المطلوبة...${NC}"
    pip install locust faker requests
}

# ─── فحص الاتصال ──────────────────────────────────────────────
echo -e "\n${YELLOW}[2/5] فحص الاتصال بالسيرفر...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET_URL/api/health" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "000" ]; then
    echo -e "${RED}خطأ: لا يمكن الاتصال بـ $TARGET_URL${NC}"
    echo -e "${RED}تأكد أن السيرفر يعمل${NC}"
    exit 1
fi
echo -e "${GREEN}السيرفر يعمل (HTTP $HTTP_CODE)${NC}"

# ─── المرحلة 1: إحماء ────────────────────────────────────────
echo -e "\n${YELLOW}[3/5] المرحلة 1: إحماء (50 مستخدم — 60 ثانية)${NC}"
locust -f locustfile_realestate.py --headless \
    --host "$TARGET_URL" \
    --users 50 --spawn-rate 5 --run-time 60s \
    --csv "$RESULTS_DIR/${TIMESTAMP}_phase1_warmup" \
    --csv-full-history \
    --html "$RESULTS_DIR/${TIMESTAMP}_phase1_report.html" \
    --only-summary 2>&1 | tail -5

echo -e "${GREEN}✓ المرحلة 1 انتهت${NC}"

# ─── المرحلة 2: حمل متوسط ─────────────────────────────────────
echo -e "\n${YELLOW}[4/5] المرحلة 2: حمل متوسط (200 مستخدم — 180 ثانية)${NC}"
locust -f locustfile_realestate.py --headless \
    --host "$TARGET_URL" \
    --users 200 --spawn-rate 20 --run-time 180s \
    --csv "$RESULTS_DIR/${TIMESTAMP}_phase2_medium" \
    --csv-full-history \
    --html "$RESULTS_DIR/${TIMESTAMP}_phase2_report.html" \
    --only-summary 2>&1 | tail -5

echo -e "${GREEN}✓ المرحلة 2 انتهت${NC}"

# ─── المرحلة 3: حمل عالي ──────────────────────────────────────
echo -e "\n${YELLOW}[5/5] المرحلة 3: حمل عالي (500 مستخدم — 180 ثانية)${NC}"
locust -f locustfile_realestate.py --headless \
    --host "$TARGET_URL" \
    --users 500 --spawn-rate 50 --run-time 180s \
    --csv "$RESULTS_DIR/${TIMESTAMP}_phase3_heavy" \
    --csv-full-history \
    --html "$RESULTS_DIR/${TIMESTAMP}_phase3_report.html" \
    --only-summary 2>&1 | tail -5

echo -e "${GREEN}✓ المرحلة 3 انتهت${NC}"

# ─── النتائج ──────────────────────────────────────────────────
echo -e "\n${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  انتهى الاختبار بنجاح!${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "  النتائج في: ${RESULTS_DIR}/"
echo -e "  ملفات CSV: ${TIMESTAMP}_phase*"
echo -e "  تقارير HTML: ${TIMESTAMP}_phase*_report.html"
echo ""
echo -e "  لتشغيل الاختبار بواجهة ويب:"
echo -e "  ${YELLOW}locust -f locustfile_realestate.py --host $TARGET_URL${NC}"
echo -e "  ثم افتح: http://localhost:8089"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
