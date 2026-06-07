# -*- coding: utf-8 -*-
"""Questions derived from learning-backlog.md and topics/*.md."""


def add_questions(Q):
    BL = "learning-backlog.md"

    # ── Tier S ───────────────────────────────────────────────────────────
    Q("S", "Транзакции", "Что такое атомарность (A) в ACID?",
      "Все операции транзакции выполняются целиком или откатываются",
      ["Только одна SQL-команда в транзакции",
       "Данные видны другим до COMMIT",
       "После COMMIT данные хранятся в Redis"],
      "Atomicity — «всё или ничего». Если одна операция упала — ROLLBACK всей транзакции. Классика: перевод между счетами.",
      note=f"{BL} · Tier S · topics/02")

    Q("S", "Транзакции", "Чем REPEATABLE READ отличается от SERIALIZABLE?",
      "REPEATABLE READ фиксирует снимок; SERIALIZABLE запрещает несериализуемые пересечения",
      ["SERIALIZABLE разрешает dirty read",
       "REPEATABLE READ сильнее SERIALIZABLE по блокировкам",
       "Разницы нет в PostgreSQL"],
      "REPEATABLE READ: повторный SELECT в транзакции даёт тот же результат. SERIALIZABLE (SSI в PG) дополнительно отлавливает опасные параллельные пересечения и откатывает.",
      note=f"{BL} · Tier S · topics/02")

    Q("S", "Транзакции", "Как обеспечивается долговечность (D) после COMMIT?",
      "WAL (write-ahead log) — изменения сначала на диск, потом commit",
      ["Данные только в RAM до следующего SELECT",
       "COMMIT сразу удаляет WAL",
       "Durability обеспечивает только Redis"],
      "Durability: после COMMIT данные переживут сбой. В Postgres — WAL, fsync, репликация для HA.",
      note=f"{BL} · Tier S · topics/02")

    Q("S", "БД блокировки", "Можно ли выполнять DDL (ALTER TABLE) внутри транзакции в PostgreSQL?",
      "Да, DDL транзакционен — можно ROLLBACK",
      ["Нет — DDL всегда autocommit как в MySQL",
       "Только DBA может DDL в транзакции",
       "DDL блокирует только SELECT, не INSERT"],
      "В PostgreSQL DDL участвует в транзакции и откатывается вместе с DML. Это важно при миграциях и откате схемы.",
      note=f"{BL} · Tier S · gap: DDL в транзакциях")

    Q("S", "Многопоточность", "Чем race condition отличается от deadlock?",
      "Race — результат зависит от порядка без синхронизации; deadlock — взаимное ожидание локов",
      ["Это синонимы",
       "Race condition только в distributed systems",
       "Deadlock — когда один поток быстрее другого"],
      "Race condition: два потока читают и инкрементят — один update теряется. Deadlock: A ждёт B, B ждёт A. Лечение race — sync/Atomic.",
      note=f"{BL} · Tier S · topics/10")

    Q("S", "Многопоточность", "Wait-Die и Wound-Wait — это про что?",
      "Стратегии предотвращения deadlock при блокировках с таймстампами",
      ["Способы garbage collection в JVM",
       "Алгоритмы сортировки в ConcurrentHashMap",
       "Режимы Kafka consumer group"],
      "Wait-Die: старый процесс ждёт молодого. Wound-Wait: старый «ранит» (откатывает) молодого. Применяют в СУБД для deadlock prevention.",
      note=f"{BL} · Tier S · deadlock")

    Q("S", "Spring", "Как Spring находит классы с @Component/@Service?",
      "Component-scan (@ComponentScan) + BeanDefinitionRegistry",
      ["Компилятор Java автоматически регистрирует бины",
       "Только через application.properties spring.beans.list",
       "Только классы в пакете java.lang"],
      "Spring сканирует указанные пакеты, находит stereotype-аннотации, регистрирует BeanDefinition, затем создаёт и внедряет бины. @Lazy — отложенная инициализация.",
      note=f"{BL} · Tier S · gap: загрузка аннотаций")

    Q("S", "JMM", "Когда volatile достаточно вместо synchronized?",
      "Один поток пишет флаг, другие только читают — простой флаг состояния",
      ["Для increment счётчика посетителей",
       "Для изменения нескольких связанных полей",
       "Для любой критической секции с записью"],
      "volatile — visibility + ordering для одного поля. Не для read-modify-write и не для инвариантов на нескольких полях.",
      note=f"{BL} · Tier S · topics/10")

    # ── Tier A ───────────────────────────────────────────────────────────
    Q("A", "Коллекции", "HashMap vs TreeMap vs LinkedHashMap?",
      "HashMap O(1); TreeMap — sorted O(log n); LinkedHashMap — порядок вставки/доступа",
      ["TreeMap быстрее HashMap для get",
       "LinkedHashMap не допускает null key",
       "HashMap хранит элементы отсортированными"],
      "HashMap — хэш, без порядка. TreeMap — красно-чёрное дерево, сортировка по ключу. LinkedHashMap — порядок + LRU через accessOrder.",
      note=f"{BL} · Tier A · topics/09")

    Q("A", "DDD", "Entity vs Value Object?",
      "Entity имеет идентичность (id); Value Object — равенство по значению",
      ["Value Object всегда mutable",
       "Entity без id — это Value Object только в DDD",
       "Разницы нет — оба хранятся в одной таблице"],
      "Entity: User, Order — важен id. Value Object: Money, Address — immutable, сравнение по полям.",
      note=f"{BL} · Tier A · topics/05")

    Q("A", "DDD", "Что такое aggregate root?",
      "Единственная точка входа для изменений группы связанных объектов",
      ["Корень XML-конфигурации Spring",
       "Главная таблица в star schema",
       "Singleton в паттерне GoF"],
      "Агрегат — кластер объектов с корнем (Order → OrderLine). Все изменения только через корень, граница транзакции.",
      note=f"{BL} · Tier A · topics/05")

    Q("A", "Java Core", "RetentionPolicy: когда аннотация видна в runtime?",
      "RUNTIME — доступна через reflection; CLASS — только в .class; SOURCE — только компилятор",
      ["SOURCE — доступна в runtime",
       "CLASS — Spring читает на лету из .java",
       "RUNTIME — удаляется после компиляции"],
      "Spring/Hibernate/Jackson нужны RUNTIME-аннотации. SOURCE — Lombok/компилятор. CLASS — bytecode без reflection.",
      note=f"{BL} · Tier A · topics/09")

    Q("A", "SOLID", "Принцип Open/Closed — что значит на практике?",
      "Расширяем поведение новым кодом, не меняя рабочий существующий",
      ["Класс нельзя наследовать",
       "Все методы должны быть final",
       "Open — все поля public"],
      "OCP: новая фича через новый класс/стратегию/impl, а не правку стабильного модуля. Пример: новый PaymentProcessor вместо if-else в старом коде.",
      note=f"{BL} · Tier A · topics/11")

    Q("A", "SOLID", "Interface Segregation и Dependency Inversion — суть?",
      "Много узких интерфейсов; зависимость от абстракций, не реализаций",
      ["Один fat interface на весь проект",
       "DIP — всегда inject через new",
       "ISP — запрет интерфейсов в Java"],
      "ISP: клиент не зависит от методов, которые не использует. DIP: high-level модули зависят от абстракций (интерфейсов), DI в Spring — пример.",
      note=f"{BL} · Tier A · topics/11")

    Q("A", "Индексы", "Что такое кластеризованный индекс?",
      "Задаёт физический порядок строк; листья содержат данные",
      ["Отдельная копия таблицы в Redis",
       "Индекс только для FULLTEXT поиска",
       "В PostgreSQL их может быть сколько угодно на таблицу"],
      "Clustered index = порядок хранения. InnoDB — PK clustered. PG — heap + separate indexes (index-only scan иначе).",
      note=f"{BL} · Tier A · topics/04")

    Q("A", "SQL", "Когда оптимизатор выбирает nested loop join?",
      "Маленькая таблица + индекс на большой — для каждой строки probe",
      ["Всегда для двух таблиц по 10 млн строк",
       "Только для CROSS JOIN",
       "Когда нет индексов — nested loop быстрее hash"],
      "Nested loop: для каждой строки outer — поиск во inner. Хорош с индексом и малой outer. Иначе hash/merge join.",
      note=f"{BL} · Tier A · topics/04")

    Q("A", "ORM", "Что такое проблема N+1 в Hibernate?",
      "1 запрос за список + N запросов за lazy-связи",
      ["N таблиц в одном JOIN",
       "N потоков выполняют один SQL",
       "N индексов на одной колонке"],
      "Загрузили 100 Order, потом lazy OrderLine для каждого — 101 запрос. Лечение: fetch join, @EntityGraph, batch size.",
      note=f"{BL} · Tier A · topics/04")

    Q("A", "Транзакции", "Что такое неповторяемое чтение (non-repeatable read)?",
      "Повторный SELECT в транзакции видит другие данные после commit другой TX",
      ["Чтение незакоммиченных данных",
       "Два одинаковых SELECT всегда дают одно и то же на READ UNCOMMITTED",
       "Фантомные строки — это и есть non-repeatable read"],
      "Non-repeatable read — между двумя SELECT другая транзакция закоммитила изменение. REPEATABLE READ это блокирует. Phantom — отдельная аномалия.",
      note=f"{BL} · Tier A · topics/02")

    # ── Tier B ───────────────────────────────────────────────────────────
    Q("B", "REST", "SOAP vs REST vs gRPC — когда что?",
      "SOAP — enterprise XML/WS-*; REST — HTTP+JSON API; gRPC — бинарный RPC между сервисами",
      ["gRPC только для браузерных UI",
       "REST всегда быстрее gRPC",
       "SOAP — единственный способ идемпотентности"],
      "REST — простой HTTP API наружу. gRPC+protobuf — межсервисное, стриминг. SOAP — legacy enterprise, тяжёлый XML.",
      note=f"{BL} · Tier B · gap: SOAP/RPC/REST")

    Q("B", "Java Core", "Почему переменная в lambda должна быть effectively final?",
      "Lambda захватывает копию значения; изменяемая переменная ломает семантику",
      ["Компилятор не поддерживает mutable capture",
       "Только для parallelStream",
       "effectively final — это keyword Java 17"],
      "Локальные переменные в lambda — effectively final (не переприсваиваются). Поля объекта можно менять. Это про predictable capture.",
      note=f"{BL} · Tier B · gap: identity + лямбды")

    Q("B", "Многопоточность", "Зачем ExecutorService?",
      "Пул потоков для переиспользования — не создавать Thread на каждую задачу",
      ["Замена synchronized блоков",
       "Только для ScheduledTask в Spring",
       "ExecutorService = virtual threads в Java 21"],
      "ExecutorService управляет пулом worker threads, очередью задач, graceful shutdown. Fixed/cached/thread-per-task executors.",
      note=f"{BL} · Tier B · gap: ExecutorService")

    Q("B", "Реактивность", "CompletableFuture vs WebFlux — в чём разница?",
      "CompletableFuture — async на пуле; WebFlux — non-blocking reactive stack end-to-end",
      ["Это одно и то же API",
       "CompletableFuture блокирует carrier thread при I/O",
       "WebFlux только для UI в браузере"],
      "CompletableFuture хорош для параллельных вызовов нескольких сервисов. WebFlux/Reactor — event loop + non-blocking I/O, backpressure. ⚠ Не «для UI».",
      err=True, note=f"{BL} · Tier B · topics/05")

    Q("B", "Многопоточность", "Когда virtual threads (Java 21+) полезны?",
      "Много блокирующих I/O задач — не привязывать OS-thread 1:1",
      ["CPU-bound математика на всех ядрах",
       "Замена synchronized везде",
       "Только в Android Dalvik"],
      "Virtual threads легковесны: при блокировке на I/O освобождают carrier. Не для CPU-bound. Platform threads — для тяжёлой CPU работы.",
      note=f"{BL} · Tier B · topics/10")

    Q("B", "Soft skills", "Расшифруй STAR для ответов про опыт.",
      "Situation, Task, Action, Result",
      ["Skill, Time, Action, Review",
       "Scope, Team, Agile, Retro",
       "System, Test, Accept, Release"],
      "Situation — контекст. Task — задача. Action — что сделал ты. Result — измеримый итог. Структура для behavioral вопросов.",
      note=f"{BL} · Tier C · topics/11")

    Q("B", "Java Core", "Что такое POJO?",
      "Plain Old Java Object — без обязательного наследования от framework-классов",
      ["Только record в Java 16+",
       "Объект с одним public полем",
       "Persistent Object в Hibernate only"],
      "POJO — обычный Java-класс с полями/геттерами, не tied to EJB/legacy frameworks. Spring/Hibernate работают с POJO + аннотации.",
      note=f"{BL} · Tier C · gap: POJO")

    Q("B", "Java Core", "Зачем marker interface Serializable?",
      "Сигнал JVM/фреймворку: объект можно сериализовать в byte stream",
      ["Обязательный метод serialize()",
       "Автоматически делает класс immutable",
       "Заменяет JSON в REST"],
      "Serializable — marker без методов. Нужен для ObjectOutputStream, некоторых API. Лучше явные форматы (JSON, protobuf) для API.",
      note=f"{BL} · Tier C · gap")

    Q("B", "Java Core", "Ограничение local var (var) в Java?",
      "Только локальные переменные с инициализацией; тип выводится компилятором",
      ["var для полей класса и параметров",
       "var запрещён в for-each",
       "var делает тип Object всегда"],
      "var — local type inference. Нельзя для полей, параметров без типа, lambda params (до Java 11). Нужна инициализация.",
      note=f"{BL} · Tier C · gap")

    Q("B", "Инфраструктура", "ClickHouse vs Cassandra vs MongoDB — профиль?",
      "ClickHouse — OLAP аналитика; Cassandra — write-heavy wide-column; Mongo — документы гибкая схема",
      ["Mongo — только OLAP",
       "Cassandra — только реляционные JOIN",
       "ClickHouse — primary OLTP bank core"],
      "ClickHouse — колоночная аналитика, агрегации. Cassandra — AP, масштаб записи. MongoDB — документы, гибкая схема, не замена Postgres OLTP.",
      note=f"{BL} · Tier C · gap: alfabank infra")

    Q("B", "Инфраструктура", "SLA 99.9% uptime — сколько простоя в год?",
      "Около 8.76 часов в год",
      ["Около 1 часа",
       "Около 30 дней",
       "99.9% = 0 простоя"],
      "99.9% = 0.1% downtime ≈ 8.76 ч/год. 99.99% ≈ 52 мин. Важно для SRE/собесов по нагрузке.",
      note=f"{BL} · Tier C · gap: SLA")

    Q("B", "Kafka", "Зачем Avro (или Schema Registry) с Kafka?",
      "Эволюция схемы сообщений с совместимостью и компактным бинарным форматом",
      ["Avro заменяет партиции",
       "Только для XML SOAP",
       "Schema Registry хранит offset consumer"],
      "Avro/Protobuf + Schema Registry — версионирование схем, backward/forward compatibility, меньше payload чем JSON.",
      note=f"{BL} · Tier C · gap: Avro")

    Q("B", "Масштабирование", "Eventual consistency после репликации — риск для приложения?",
      "Чтение с lagging replica сразу после write может не увидеть данные",
      ["Невозможно в PostgreSQL",
       "Всегда решается автоматическим retry SELECT",
       "Eventual consistency только в NoSQL"],
      "После COMMIT на primary реплика может отставать. Read-your-writes: читать с primary или ждать/retries. UI/API должны это учитывать.",
      note=f"{BL} · Tier B · topics/03")

    Q("B", "Масштабирование", "Бэкап vs репликация — ключевая разница?",
      "Бэкап — снимок для восстановления; репликация — живая копия, не спасает от DELETE",
      ["Репликация заменяет бэкап полностью",
       "Бэкап обновляется в реальном времени как реплика",
       "Разницы нет"],
      "Ошибочный DELETE реплицируется на standby. Бэкап/PITR восстанавливает состояние до ошибки. Нужны оба.",
      note=f"{BL} · Tier B · topics/03")

    Q("B", "SQL", "INNER JOIN vs LEFT JOIN — когда LEFT?",
      "LEFT — все строки левой таблицы + совпадения справа (NULL если нет)",
      ["LEFT — только совпадающие строки",
       "INNER — сохраняет строки без пары с NULL",
       "LEFT быстрее INNER всегда"],
      "INNER — только match. LEFT — все из left + optional right. «Клиенты без заказов» — LEFT + WHERE right IS NULL.",
      note=f"{BL} · Tier B · topics/04")

    Q("B", "Реактивность", "Почему WebFlux не даёт выигрыша при блокирующем JDBC?",
      "Event loop блокируется на JDBC — нужен non-blocking driver (R2DBC) вся цепь",
      ["WebFlux автоматически делает JDBC async",
       "Проблема только в Tomcat, не Netty",
       "WebFlux ускоряет CPU-bound код"],
      "Реактивный стек работает, если вся цепочка non-blocking. Блокирующий call в reactive thread убивает scalability.",
      err=True, note=f"{BL} · Tier B · topics/05")

    Q("B", "CQRS", "Когда CQRS оправдан?",
      "Большой перекос read/write, сложные read-модели, отдельные витрины",
      ["На любом CRUD из 3 таблиц",
       "Только когда одна таблица",
       "CQRS обязателен с Spring Data"],
      "CQRS — не для маленьких CRUD. Оправдан при разных моделях чтения/записи, search/reporting, масштабировании read side.",
      note=f"{BL} · Tier B · topics/05")

    Q("B", "Масштабирование", "Порядок масштабирования БД на практике?",
      "Индексы/SQL → кэш → read replicas → partition → shard",
      ["Сразу шардирование → потом индексы",
       "Только vertical scale без оптимизации",
       "Удалить индексы для ускорения write"],
      "Сначала дешёвое: EXPLAIN, индексы, query tuning. Потом Redis cache, реплики read, партиционирование, шардирование.",
      note=f"{BL} · Tier B · topics/03")

    Q("B", "Тестирование", "verify() в Mockito — зачем?",
      "Проверить, что mock-метод вызван с ожидаемыми аргументами",
      ["Заменить assertEquals",
       "Создать новый mock объект",
       "Запустить интеграционный тест"],
      "when().thenReturn() — stub поведения. verify() — проверка взаимодействия. Не мокать SUT, мокать границы.",
      note=f"{BL} · Tier B · gap: Mock-тесты")

    # ── Tier C ───────────────────────────────────────────────────────────
    Q("C", "Сети", "Сколько уровней в модели OSI?",
      "7 уровней",
      ["5 уровней",
       "4 уровня — как TCP/IP только",
       "10 уровней"],
      "OSI: Physical, Data Link, Network, Transport, Session, Presentation, Application. На собесах часто: L2 MAC, L3 IP, L4 TCP/UDP.",
      note=f"{BL} · Tier A · topics/07")

    Q("C", "Сети", "TCP vs UDP — главное отличие?",
      "TCP — надёжность, порядок, handshake; UDP — быстрее, без гарантий",
      ["UDP всегда шифрует трафик",
       "TCP не использует порты",
       "UDP только для DNS и больше нигде"],
      "TCP: connection, ACK, retransmit. UDP: datagram, fire-and-forget — DNS, streaming, games где допустима потеря.",
      note=f"{BL} · Tier C · topics/07")

    Q("C", "Java Core", "Модификатор protected — кто видит?",
      "Пакет + наследники (даже из другого пакета)",
      ["Только класс-наследник в том же файле",
       "Везде как public",
       "Только внутри interface"],
      "private — класс. package-private — пакет. protected — пакет + subclasses. public — все.",
      note=f"{BL} · Tier C · topics/09")

    Q("C", "Java Core", "JNI vs JNA — зачем?",
      "Вызов native C/C++ кода из Java (JNI — низкоуровневый; JNA — проще без генерации заголовков)",
      ["Способы сериализации JSON",
       "Только для Android NDK exclusive",
       "Замена JDBC"],
      "JNI — Java Native Interface для perf/legacy libs. JNA — обёртка без javah. Осторожно: crashes, portability.",
      note=f"{BL} · Tier C · gap: JNI/JNA")

    Q("C", "Spring", "Micronaut vs Spring Boot — ключевое отличие DI?",
      "Micronaut — DI на этапе компиляции (AOT); Spring — runtime + reflection",
      ["Micronaut не поддерживает DI",
       "Spring Boot только для Groovy",
       "Micronaut требует EJB container"],
      "Micronaut/AOT меньше reflection, быстрее cold start — интересно для serverless. Spring — richer ecosystem.",
      note=f"{BL} · Tier C · gap: Micronaut")

    Q("C", "Контейнеры", "Docker vs Kubernetes — роли?",
      "Docker — образы и контейнеры на узле; Kubernetes — оркестрация кластера",
      ["Kubernetes заменяет Docker Engine",
       "Docker — только для Windows containers без Linux",
       "Kubernetes — язык описания Dockerfile"],
      "Docker build/run container. K8s scheduling, scaling, service discovery, self-healing across nodes.",
      note=f"{BL} · Tier C · topics/07")

    Q("C", "Java Core", "Что такое final class (пример String)?",
      "Класс нельзя наследовать — защита инвариантов и immutability",
      ["Все методы класса final",
       "Класс нельзя инстанцировать",
       "final class = record"],
      "final class запрещает extends. String — final для immutability и безопасности. Отдельно final method — нельзя override.",
      note=f"{BL} · Tier C · topics/09")

    Q("B", "Kafka", "Push vs Pull модель — RabbitMQ vs Kafka?",
      "RabbitMQ push to consumer; Kafka pull by consumer по offset",
      ["Kafka push сообщения consumer-ам",
       "RabbitMQ только pull",
       "Обе только broadcast без groups"],
      "Rabbit — broker push (prefetch/backpressure у consumer). Kafka — consumer pull, контролирует offset, replay.",
      note=f"{BL} · Tier B · gap: Kafka vs Rabbit")

    Q("A", "Java Core", "Максимальное значение int и что при переполнении?",
      "±2.1 млрд; переполнение int молча wrap-around",
      ["2^64",
       "Exception на overflow",
       "Автоматический promote в BigDecimal"],
      "int 32-bit signed. Overflow без exception (кроме Math.multiplyExact). Деньги/счётчики — long/BigDecimal.",
      note=f"{BL} · Tier A · gap: числовые типы")

    Q("A", "Многопоточность", "AtomicInteger vs synchronized для счётчика?",
      "AtomicInteger — CAS без блокировки; проще и быстрее для одного счётчика",
      ["synchronized всегда быстрее Atomic",
       "Atomic блокирует весь класс",
       "Для счётчика нужен только volatile"],
      "Простой increment — Atomic*. synchronized/Lock — если несколько связанных действий в критической секции.",
      note=f"{BL} · Tier A · topics/10")
