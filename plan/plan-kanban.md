# Kanban تنفيذي - عقاري جدة

> تاريخ البدء: 23 فبراير 2026  
> مدة الدورة: 10 أيام عمل  
> تحديث يومي: نهاية كل يوم

---

## قواعد التشغيل

1. حدّ العمل الجاري `In Progress` = 4 بطاقات كحد أقصى.
2. لا يتم بدء بطاقة جديدة قبل إنهاء بطاقة أو إزالة عائق.
3. كل بطاقة يجب أن تحتوي: `Owner` + `Due Date` + `Definition of Done`.
4. أي طلب خارج أهداف Sprint ينتقل مباشرة إلى Backlog.

---

## KPI Snapshot (يُحدّث يوميًا)

| KPI | الهدف | اليوم | الحالة |
|-----|-------|-------|--------|
| First Response Time | < 3 دقائق | - | 🟡 |
| SLA Compliance | > 85% | - | 🟡 |
| Lead Conversion (مهتم -> مغلق_ناجح) | +20% | - | 🟡 |
| Unassigned Open Leads | < 5% | - | 🟡 |

---

## Backlog (خارج Sprint)

- [ ] BK-01: إشعارات Push متكاملة.
- [ ] BK-02: تطبيق Mobile (React Native).
- [ ] BK-03: تكاملات إضافية (منصات محلية/حكومية).
- [ ] BK-04: نظام اشتراكات وفوترة متقدم.
- [ ] BK-05: تحليلات تنبؤية AI.

---

## To Do

- [x] TD-01: تدقيق شامل للمفاتيح السرية والتأكد أنها من `.env` فقط.  
  Owner: Backend | Due: يوم 2 | DoD: لا يوجد أي Secret داخل الكود. (تم التنفيذ عبر فحص آلي `security:secrets`)

- [x] TD-02: تفعيل مراقبة أخطاء الإنتاج (Sentry أو بديل) مع Test Event.  
  Owner: Backend | Due: يوم 2 | DoD: وصول خطأ تجريبي فعلي للـ Dashboard. (تم التنفيذ عبر Monitoring Route + Dashboard Trigger)

- [x] TD-03: Health Check Endpoint شامل (DB + API + Queue).  
  Owner: Backend | Due: يوم 3 | DoD: `/health` يعكس حالات الخدمات بدقة. (تم التنفيذ)

- [x] TD-04: اختبار تدفق WhatsApp الكامل (استقبال -> رد -> حفظ -> Lead).  
  Owner: QA + Backend | Due: يوم 4 | DoD: نجاح 5 سيناريوهات متتالية. (تم التنفيذ عبر اختبارات آلية 5 سيناريوهات)

- [ ] TD-05: مراجعة دقة توزيع Leads على المسوقين في الإنتاج.  
  Owner: Backend | Due: يوم 5 | DoD: لا يوجد Lead جديد بدون مسار توزيع واضح.

- [ ] TD-06: مراجعة لوحة أداء المسوقين وتطابق الأرقام مع البيانات الخام.  
  Owner: Frontend + QA | Due: يوم 6 | DoD: فروقات القياس أقل من 2%.

- [x] TD-07: تفعيل تنبيهات SLA للـ Leads المتأخرة.  
  Owner: Backend + Frontend | Due: يوم 7 | DoD: تنبيه واضح يظهر خلال دورة التحديث. (تم التنفيذ)

- [ ] TD-08: UAT سريع مع مستخدمين فعليين (مدير + مسوق).  
  Owner: QA | Due: يوم 9 | DoD: تقرير UAT + قائمة ملاحظات مرتبة.

- [ ] TD-09: إغلاق Sprint Report (KPI + المخاطر + قرارات الدورة القادمة).  
  Owner: PM | Due: يوم 10 | DoD: تقرير مكتمل ومعتمد.

---

## In Progress

- [ ] IP-01: تحسين رسائل الأخطاء وتجربة المستخدم في واجهات التشغيل.  
  Owner: Frontend | Started: 23-02-2026 | DoD: رسائل واضحة + بدون أخطاء حرجة UX.

- [ ] IP-02: مراجعة صلاحيات الأدوار (Owner/Admin/Agent/Viewer) على الصفحات الحساسة.  
  Owner: Backend + Frontend | Started: 23-02-2026 | DoD: صلاحيات متوافقة مع السياسة الرسمية.

---

## Blocked

- [ ] BL-01: اعتماد سياسة النشر النهائية (Vercel/Backend Host) من الإدارة.  
  Owner: PM | Blocker: قرار بنية الاستضافة | Next Action: اجتماع اعتماد.

---

## Done

- [x] DN-01: إعداد خطة تنفيذية مختصرة (`plan.md`).
- [x] DN-02: إنشاء لوحة تحكم التسويق داخل النظام.
- [x] DN-03: إضافة تقييم الجدية Lead Score + Priority.
- [x] DN-04: إضافة توزيع تلقائي للـ Leads (Round Robin / Least Load).
- [x] DN-05: إضافة Agent تحويل الصوت إلى كتابة ضمن التدفق.
- [x] DN-06: إنشاء صفحة تسويق مستقلة (HTML/CSS/JS) في `marketing-html`.
- [x] DN-07: إضافة Endpoint صحة `api/health` مع فحص DB/API/Queue.
- [x] DN-08: إضافة فحص أسرار آلي (`npm run security:secrets`) لمنع المفاتيح داخل الكود.
- [x] DN-09: إضافة تنبيهات SLA تشغيلية (API + إشعار + تحديث تلقائي في لوحة التسويق).
- [x] DN-10: إضافة مراقبة أخطاء تشغيلية + `Test Event` من لوحة الإعدادات.
- [x] DN-11: إضافة اختبارات تدفق WhatsApp (5 سيناريوهات) لمسار `api/webhook`.

---

## قالب التحديث اليومي (نسخ ولصق)

### Daily Update - [التاريخ]

- **Done Today:**  
  - ...

- **In Progress:**  
  - ...

- **Blocked:**  
  - ...

- **KPI Today:**  
  - First Response Time: ...  
  - SLA Compliance: ...  
  - Lead Conversion: ...  
  - Unassigned Leads: ...

- **Plan Tomorrow:**  
  - ...
