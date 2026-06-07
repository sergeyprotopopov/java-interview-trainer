# 📋 Learning Backlog — приоритизированный план подготовки

Единый список слабых тем, собранный из всех источников и **отсортированный по частоте × важности**.
Каждая тема встречается **один раз** (дубли между собеседованиями объединены).

## Источники
- **Чек-лист** `JAVA Checklist/JV_CHCLST2.xlsx` (с критичностью и компаниями)
- **Основное собеседование** (разбор easyoffer): БД, транзакции, сети, JVM, многопоточность, паттерны
- **T-Bank** (`tbank.txt`, `tbank_interview.xlsx`, логи): коллекции, многопоточность, блокировки, REST
- **Alfabank** (`alfabank.txt`): реактивность, инфраструктура
- **VK** (`screen_logs`): system design, `volatile`, алгоритмы

## Легенда
- **🔁 Частота** — в скольких источниках/компаниях встречалась тема (выше = чаще спрашивают)
- **⭐ Важность** — 1–6 (из чек-листа или экспертная оценка)
- **Покрытие**: ✅ разобрано в `topics/` · ⚠️ частично · ⛔ пробел (нет конспекта)
- **‼️** — на собеседовании был дан неверный ответ (учить обязательно)

---

## 🟥 Tier S — учить в первую очередь (частые + критичные / были ошибки)

- [ ] **Транзакции и уровни изоляции** (+ MVCC, грязное чтение, дефолт в БД) — 🔁5 (Berkut, иннотех, T-Bank, 1c, осн.) · ⭐6 · ✅[02](topics/02-transactions-isolation.md) ‼️ `READ UNCOMMITTED`=`READ COMMITTED` в PG
- [ ] **JMM: `volatile`, happens-before, публикация данных** — 🔁4 (цб, T-Bank, VK, осн.) · ⭐6 · ✅[08](topics/08-jvm-memory.md)/[10](topics/10-concurrency.md) ‼️ задача «0 или 13» (`result` не volatile)
- [ ] **Spring внутри: DI-контейнер, загрузка аннотаций, `@Lazy` для циклических** — 🔁4 (сбер, иннотех, 1c, пятерочка) · ⭐6 · ⛔ gap
- [ ] **Deadlock + race condition** (многопоточные переводы, порядок локов, Wait-Die/Wound-Wait) — 🔁4 (T-Bank, пятерочка, VK, осн.) · ⭐5 · ✅[10](topics/10-concurrency.md) — нужна практика кода
- [ ] **Блокировки в БД: оптимистичная/пессимистичная, `SELECT FOR UPDATE`, DDL в транзакциях** — 🔁3 (иннотех, T-Bank, 1c) · ⭐5 · ⛔ gap

## 🟧 Tier A — высокий приоритет (частые, важные)

- [ ] **`equals`/`hashCode` контракт + immutable-ключи в hash-структурах** — 🔁3 (пятерочка, T-Bank, VK) · ⭐5 · ⚠️[09](topics/09-java-core.md)
- [ ] **ООП: 5 принципов, композиция vs агрегация vs наследование, интерфейс vs абстрактный класс** — 🔁3 (Berkut, цб, пятерочка) · ⭐6 · ⚠️[11](topics/11-methodologies.md)
- [ ] **Коллекции: ArrayList vs LinkedList, HashMap/TreeMap/LinkedHashMap (LRU)** — 🔁2 (T-Bank, VK) · ⭐5 · ⚠️[09](topics/09-java-core.md)
- [ ] **Comparable vs Comparator** (`compareTo`/`compare`, лямбды, несколько критериев) — 🔁2 (T-Bank) · ⭐4 · ⛔ gap
- [ ] **Виды GC: G1, Parallel, ZGC, Shenandoah** (+ как работает сборщик) — 🔁2 (Berkut, пятерочка) · ⭐5 · ⚠️[08](topics/08-jvm-memory.md)
- [ ] **Числовые типы: размеры/ограничения `Integer`/`Long`/`BigDecimal`/`double`, разрядности** — 🔁2 (яндекс, VK) · ⭐6 · ⛔ gap
- [ ] **Индексы: типы, составные, частичные, кластеризованный, стоимость записи** — 🔁3 (T-Bank, чек-лист, осн.) · ⭐4 · ✅[04](topics/04-indexes-queries-optimization.md)
- [ ] **Reflection + ClassLoader** (цепочка загрузчиков, RetentionPolicy) — 🔁2 (VK, осн.) · ⭐5 · ✅[08](topics/08-jvm-memory.md)
- [ ] **MVCC + SERIALIZABLE/snapshot в PostgreSQL** — 🔁2 (1c, T-Bank) · ⭐5 · ⚠️[02](topics/02-transactions-isolation.md)
- [ ] **Atomic / CAS** (lock-free, реализация на уровне JVM/CPU) — 🔁2 (Berkut, осн.) · ⭐4 · ✅[10](topics/10-concurrency.md)
- [ ] **Паттерны проектирования: 3 типа + конкретные примеры** — 🔁2 (корона пэй, осн.) · ⭐5 · ✅[06](topics/06-design-patterns.md)
- [ ] **Сети: OSI, DNS, ARP, NAT, DHCP** (кто что делает, уровни) — 🔁2 (чек-лист, осн.) · ⭐4 · ✅[07](topics/07-containers-networking.md) ‼️ путаница ARP/DNS/NAT

## 🟨 Tier B — средний приоритет

- [ ] **Kafka: устройство, отличие от JMS/MQ, контракты** — 🔁2 (иннотех, alfabank) · ⭐5 · ⛔ gap
- [ ] **SOAP/RPC/REST + надёжность REST** (retry, timeout, **идемпотентность**, circuit breaker) — 🔁2 (чек-лист, T-Bank) · ⭐5 · ⚠️[07](topics/07-containers-networking.md)
- [ ] **System design: лента новостей** (pull vs push, fan-out, кэш, ранжирование) — 🔁1 (VK) · ⭐5 · ⛔ gap
- [ ] **Live coding: алгоритмы на строки/коллекции** (напр. `maxConsecutiveRepeats`, O(n)) — 🔁2 (VK, T-Bank) · ⭐5 · ⛔ практика
- [ ] **Saga для распределённых транзакций** — 🔁1 (иннотех) · ⭐5 · ⛔ gap
- [ ] **Mock-тесты (Mockito): что и как мокать** — 🔁1 (яндекс) · ⭐5 · ⛔ gap
- [ ] **`identity` в Java + связка с лямбдами** — 🔁1 (1c) · ⭐5 · ⛔ gap
- [ ] **Реактивность: WebFlux/Reactor + CompletableFuture** — 🔁2 (alfabank, осн.) · ⭐4 · ✅[05](topics/05-ddd-cqrs-reactive.md) ‼️ это НЕ «для UI»
- [ ] **ConcurrentHashMap vs synchronizedMap, ThreadLocal, ExecutorService** — 🔁1 (T-Bank) · ⭐4 · ⛔ gap
- [ ] **Stream API: промежуточные/терминальные операции, ленивость** — 🔁1 (T-Bank) · ⭐4 · ⛔ gap
- [ ] **DDD + bounded context** — 🔁2 (чек-лист, осн.) · ⭐4 · ✅[05](topics/05-ddd-cqrs-reactive.md)
- [ ] **CQRS** (Command меняет состояние, Query читает) — 🔁2 (чек-лист, осн.) · ⭐4 · ✅[05](topics/05-ddd-cqrs-reactive.md) ‼️ путал Command/Query
- [ ] **Репликация / шардирование / масштабирование** — 🔁2 (осн.) · ⭐4 · ✅[03](topics/03-replication-sharding-scaling.md)
- [ ] **Singleton: написать, `volatile`, `static`, потокобезопасность** — 🔁1 (1c) · ⭐4 · ⛔ gap
- [ ] **SQL: `HAVING`, `GROUP BY`** — 🔁1 (1c) · ⭐4 · ⛔ gap

## 🟩 Tier C — низкий приоритет / nice-to-have

- [ ] **Строки: String/StringBuilder/String Pool, неизменяемость** — 🔁1 (T-Bank) · ⭐3 · ⛔ gap
- [ ] **HTTP/2 vs HTTP/1.1, gRPC** — 🔁3 (осн., T-Bank, alfabank) · ⭐3 · ✅[07](topics/07-containers-networking.md)
- [ ] **Контейнеры/Docker/Kubernetes** (vs виртуализация) — 🔁1 (осн.) · ⭐3 · ✅[07](topics/07-containers-networking.md)
- [ ] **Исключения, `final/finally/finalize`, модификаторы доступа** — 🔁1 (осн.) · ⭐3 · ✅[09](topics/09-java-core.md)
- [ ] **Optional / как избавиться от null** — 🔁1 (сбер) · ⭐3 · ⛔ gap
- [ ] **POJO, маркер-интерфейсы (`Serializable`/`Cloneable`), `var`, JNI/JNA** — 🔁1 (T-Bank) · ⭐2 · ⛔ gap
- [ ] **Инфраструктура: S3/MinIO, ClickHouse vs Cassandra vs Mongo, Avro** — 🔁1 (alfabank) · ⭐3 · ⛔ gap
- [ ] **SLA/uptime (99.9% ≈ 8.76 ч/год), оценка нагрузки (RPS, JMeter)** — 🔁1 (T-Bank) · ⭐3 · ⛔ gap
- [ ] **Micronaut фреймворк** — 🔁1 (рексофт) · ⭐1 · ⛔ gap
- [ ] **STAR — структура ответов про опыт** — soft · ✅[11](topics/11-methodologies.md)

---

## ⛔ Топ пробелов без конспектов (написать первыми)

Высокая частота/важность, но ещё нет разбора в `topics/`:

1. Spring внутри: DI-контейнер + загрузка аннотаций (Tier S)
2. Блокировки в БД: optimistic/pessimistic + `SELECT FOR UPDATE` + DDL-транзакции (Tier S)
3. Числовые типы: точные размеры и ограничения (Tier A)
4. Comparable vs Comparator (Tier A)
5. Kafka: устройство + vs JMS/MQ (Tier B)
6. Saga, Mock-тесты, `identity`+лямбды (Tier B)
7. System design (лента) + практика live coding (Tier B)

## ✅ Уже закрыто конспектами (повторять, не писать заново)
`topics/02` транзакции · `topics/03` репликация · `topics/04` индексы · `topics/05` DDD/CQRS/reactive · `topics/06` паттерны · `topics/07` сети/контейнеры · `topics/08` JVM/память · `topics/09` Java Core · `topics/10` многопоточность · `topics/11` SOLID/STAR
(⚠️ внутри есть места, помеченные `‼️` выше — доразобрать акценты)
