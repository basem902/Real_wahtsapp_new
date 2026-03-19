# تقرير اختبار الحمل — منصة Smart Real Estate Agent
## smartsapp.net | 2026-03-19

---

## ملخص تنفيذي

| المؤشر | المرحلة 1 (50 مستخدم) | المرحلة 2 (200 مستخدم) | المرحلة 3 (500 مستخدم) |
|--------|----------------------|----------------------|----------------------|
| **إجمالي الطلبات** | 1,268 | 8,112 | 14,345 |
| **طلبات/ثانية (RPS)** | 21.8 | 69.1 | 120.9 |
| **نسبة الأخطاء** | 6.1% | 25.3% | 32.5% |
| **متوسط الاستجابة** | 341ms | 907ms | 1,974ms |
| **P50 (الوسيط)** | 280ms | 540ms | 970ms |
| **P90** | 550ms | 1,900ms | 4,200ms |
| **P95** | 700ms | 2,900ms | 6,200ms |
| **P99** | 1,100ms | 4,100ms | 16,000ms |
| **أبطأ طلب** | 1,644ms | 12,230ms | 85,552ms |

---

## تحليل الأداء حسب نوع الـ Endpoint

### 1. الصفحات العامة (Public Endpoints) — الأفضل أداءً

| Endpoint | P50 (50 users) | P50 (200 users) | P50 (500 users) | تقييم |
|----------|---------------|-----------------|-----------------|-------|
| Health Check | 260ms | 540ms | 860ms | جيد |
| Plans | 290ms | 600ms | 890ms | جيد |
| SSR / (الرئيسية) | 260ms | 550ms | 1,300ms | مقبول |
| SSR /features | 270ms | 560ms | 1,100ms | مقبول |
| SSR /pricing | 260ms | 560ms | 1,100ms | مقبول |
| Submit Lead | 260ms | 600ms | 800ms | جيد |
| Book Appointment | 250ms | 610ms | 870ms | جيد |

### 2. Webhook (WhatsApp) — أداء ممتاز

| Endpoint | P50 (50 users) | P50 (200 users) | P50 (500 users) | تقييم |
|----------|---------------|-----------------|-----------------|-------|
| Incoming Message | 290ms | 420ms | 800ms | ممتاز |
| Burst Messages | 280ms | 370ms | 690ms | ممتاز |

### 3. Admin Endpoints (مع Auth) — أبطأ

| Endpoint | P50 (50 users) | P50 (200 users) | P50 (500 users) | تقييم |
|----------|---------------|-----------------|-----------------|-------|
| List Properties | 440ms | 770ms | 1,200ms | مقبول |
| Search Properties | 440ms | 780ms | 1,300ms | مقبول |
| Stats | 410ms | 820ms | 1,400ms | ضعيف |
| Notifications | 440ms | 710ms | 1,400ms | ضعيف |
| Bot Settings | 440ms | 1,000ms | 1,400ms | ضعيف |
| WhatsApp Status | 540ms | 940ms | 1,300ms | مقبول |
| Subscription | 680ms | 1,000ms | 1,400ms | ضعيف |
| ROI | 460ms | 990ms | 1,400ms | ضعيف |

---

## أبطأ 5 Endpoints (عند 500 مستخدم — P95)

| الترتيب | Endpoint | P95 | P99 | Max |
|---------|----------|-----|-----|-----|
| 1 | Bot Settings | 11,000ms | 14,000ms | 14,136ms |
| 2 | Subscription | 12,000ms | 40,000ms | 40,130ms |
| 3 | Stats | 10,000ms | 30,000ms | 49,770ms |
| 4 | Auto Responses | 5,800ms | 38,000ms | 44,956ms |
| 5 | ROI | 10,000ms | 46,000ms | 45,934ms |

---

## تحليل الأخطاء

### توزيع أنواع الأخطاء (المرحلة 3 — 500 مستخدم)

| نوع الخطأ | العدد | النسبة | التفسير |
|-----------|-------|--------|---------|
| **429 (Rate Limited)** | ~4,200 | 90% | Rate limiter يعمل بشكل صحيح |
| **500 (Server Error)** | 84 | 2% | خطأ في List Properties |
| **400 (Bad Request)** | 38 | 1% | Validation errors في Add Property |
| **Connection Reset/Timeout** | ~50 | 1% | السيرفر يقطع الاتصال تحت الضغط |
| **RemoteDisconnected** | ~12 | <1% | إغلاق اتصال بدون رد |

### Rate Limiting Analysis
- الـ Rate Limiter يبدأ بالتفعيل عند ~100 مستخدم
- عند 200 مستخدم: 25% من الطلبات ترجع 429
- عند 500 مستخدم: 32% من الطلبات ترجع 429
- **Health endpoint** أكثر endpoint يتأثر بالـ rate limiting (1,252 من 1,437 طلب)

---

## RPS (Requests Per Second) — خلال المراحل

```
المرحلة 1 (50 مستخدم):   ████████████████████▌ 21.8 RPS
المرحلة 2 (200 مستخدم):  ████████████████████████████████████████████████████████████████████▌ 69.1 RPS
المرحلة 3 (500 مستخدم):  █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▌ 120.9 RPS
```

---

## نقاط القوة

1. **Webhook endpoints (WhatsApp)** — أفضل أداء في المنصة. P50 = 690ms حتى عند 500 مستخدم. هذا مهم جداً لأن الواتساب هو القناة الأساسية.
2. **Public endpoints** — أداء مستقر ومقبول. Submit Lead و Book Appointment يستجيبون بسرعة.
3. **Rate Limiting** — يعمل بشكل صحيح ويحمي السيرفر من الإغراق.
4. **SSR Pages** — صفحات الموقع تستجيب بشكل جيد حتى 200 مستخدم متزامن.
5. **استقرار عام** — لا يوجد crashes أو downtime كامل حتى عند 500 مستخدم.

---

## نقاط الضعف والمشاكل

1. **List Properties → 500 Error** — 84 خطأ server error. يحتاج فحص logs.
2. **Admin endpoints بطيئة** — P95 يصل 10-12 ثانية عند 500 مستخدم.
3. **تدهور كبير بين 200→500 مستخدم** — متوسط الاستجابة تضاعف (907ms → 1,974ms).
4. **Connection resets** — السيرفر يبدأ يقطع اتصالات عند 500 مستخدم.
5. **Rate limiting عدواني جداً على Health endpoint** — 87% من طلبات Health ترجع 429.

---

## التوصيات

### أولوية عالية (تأثير كبير)

#### 1. Redis Cache للبيانات المتكررة
```
الأثر المتوقع: تقليل الاستجابة 50-70%
```
- **Stats/Analytics**: نتائج ثابتة لمدة 5-10 دقائق → cache مع TTL
- **Bot Settings**: نادراً ما تتغير → cache مع invalidation عند التعديل
- **Subscription**: بيانات لا تتغير كثيراً → cache 15 دقيقة
- **Plans**: بيانات ثابتة → cache ساعة أو أكثر

#### 2. PgBouncer لـ Connection Pooling
```
الأثر المتوقع: تقليل الأخطاء 500 بنسبة 90%
```
- أخطاء 500 في List Properties غالباً من استنزاف connection pool
- PgBouncer في وضع `transaction` يحل المشكلة
- Supabase يدعمه مباشرة عبر port 6543

#### 3. تعديل Rate Limiting
```
الأثر المتوقع: تقليل 429 errors بنسبة 60%
```
- Health endpoint: رفع الحد لأنه lightweight (500/min بدل 120/min)
- Plans endpoint: رفع الحد لأنه public و cacheable
- فصل rate limits حسب: public vs authenticated vs admin

### أولوية متوسطة

#### 4. CDN (Cloudflare)
- SSR pages تستفيد من edge caching
- Static assets (images, CSS, JS) يجب أن تكون على CDN
- الأثر: تقليل P50 لصفحات SSR من 1,300ms إلى ~200ms

#### 5. تحسين Query الـ Properties
- List Properties أبطأ admin endpoint
- فحص: هل يوجد indexes على الحقول المستخدمة في الفلترة؟
- استخدام `select` محدد بدل `select *`

#### 6. Horizontal Scaling
- عند 500 مستخدم، سيرفر واحد يبدأ يتعب
- الحل: 2-3 instances خلف load balancer
- Vercel/Railway يدعمون auto-scaling

### أولوية منخفضة

#### 7. WebSocket بدل Polling للإشعارات
- حالياً كل مستخدم يعمل poll على /api/notifications
- WebSocket يقلل عدد الطلبات بشكل كبير

#### 8. Queue للـ Webhook Processing
- Webhook messages حالياً تُعالج synchronously
- Queue (BullMQ/Redis) يسمح بمعالجة غير متزامنة
- يحسن الاستجابة ويمنع فقدان الرسائل

---

## الخلاصة

المنصة تتحمل **200 مستخدم متزامن** بأداء مقبول (P50 < 1s).
عند **500 مستخدم**، الأداء يتدهور بشكل ملحوظ لكن المنصة لا تسقط.

**الأولوية الأولى**: Redis Cache + PgBouncer → سيحل 80% من المشاكل.

---

*تم إنشاء هذا التقرير تلقائياً من نتائج اختبار Locust*
*تاريخ التقرير: 2026-03-19*
