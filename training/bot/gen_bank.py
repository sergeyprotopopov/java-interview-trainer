# -*- coding: utf-8 -*-
"""Generate questions.py from structured bank. Run: python gen_bank.py"""

from __future__ import annotations

import json
import textwrap

# Each item: t, topic, err, q, correct, wrong[3-4], a, note?
RAW: list[dict] = []

def Q(t, topic, q, correct, wrong, a, err=False, note=None):
    assert len(wrong) >= 3
    item = {"t": t, "topic": topic, "err": err, "q": q, "correct": correct, "wrong": wrong[:4], "a": a}
    if note:
        item["note"] = note
    RAW.append(item)


# ── S tier ──────────────────────────────────────────────────────────────
Q("S", "Транзакции", "Какие уровни изоляции транзакций определены в SQL?",
  "READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE",
  ["READ COMMITTED, REPEATABLE READ, SERIALIZABLE, SNAPSHOT",
   "READ UNCOMMITTED, READ COMMITTED, SERIALIZABLE, READ SNAPSHOT",
   "READ COMMITTED, REPEATABLE READ, PHANTOM READ, SERIALIZABLE"],
  "Стандарт SQL определяет четыре уровня: READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE. Чем выше уровень — тем меньше аномалий чтения, но ниже параллелизм.")

Q("S", "Транзакции", "Какой уровень изоляции по умолчанию в PostgreSQL и MySQL (InnoDB)?",
  "PostgreSQL — READ COMMITTED; MySQL InnoDB — REPEATABLE READ",
  ["Оба — REPEATABLE READ",
   "PostgreSQL — REPEATABLE READ; MySQL — READ COMMITTED",
   "PostgreSQL — SERIALIZABLE; MySQL — READ UNCOMMITTED"],
  "PostgreSQL и Oracle по умолчанию используют READ COMMITTED. MySQL с движком InnoDB — REPEATABLE READ.")

Q("S", "Транзакции", "Что такое грязное чтение (dirty read)?",
  "Транзакция читает незакоммиченные изменения другой транзакции",
  ["Транзакция читает только закоммиченные данные дважды с разным результатом",
   "Две транзакции одновременно пишут в одну строку без блокировки",
   "Чтение данных из другой схемы БД без прав доступа"],
  "Грязное чтение — когда транзакция видит незакоммиченные изменения другой. На уровне READ COMMITTED и выше это запрещено.",
  err=True, note="Раньше отвечал неверно — учить.")

Q("S", "Транзакции", "Почему в PostgreSQL READ UNCOMMITTED фактически = READ COMMITTED?",
  "MVCC не показывает незакоммиченные версии строк — dirty read невозможен",
  ["PostgreSQL автоматически повышает уровень до SERIALIZABLE",
   "READ UNCOMMITTED в PG блокирует все чтения shared lock",
   "Потому что PG не поддерживает MVCC для чтения"],
  "В PostgreSQL из-за MVCC каждая транзакция видит свой снимок данных; незакоммиченные версии строк ей недоступны, поэтому настоящего dirty read нет.",
  err=True)

Q("S", "JMM", "Делает ли volatile операции атомарными?",
  "Нет — volatile не делает read-modify-write атомарным",
  ["Да, любая операция над volatile полем атомарна",
   "Да, но только для примитивов int и boolean",
   "Да, если поле объявлено final и volatile одновременно"],
  "volatile даёт видимость и запрет переупорядочивания, но count++ — это read-modify-write из трёх шагов и не атомарен. Нужны Atomic*, synchronized или Lock.",
  err=True, note="Задача «0 или 13»: result не был volatile.")

Q("S", "JMM", "Что такое happens-before в Java Memory Model?",
  "Гарантия видимости: результаты действия A будут видны в B",
  ["Гарантия, что поток A завершится раньше потока B по wall-clock",
   "Порядок вызова методов в одном synchronized-блоке",
   "Синхронная очередь событий между потоками в ExecutorService"],
  "happens-before — отношение упорядочивания: если A happens-before B, результаты A видны в B. Примеры: unlock→lock, запись volatile→чтение, start потока→его код.")

Q("S", "Spring", "Как Spring DI-контейнер создаёт и связывает бины?",
  "Сканирует классы, строит BeanDefinition, создаёт бины и внедряет зависимости",
  ["Создаёт все бины через reflection без метаданных",
   "Компилирует конфигурацию в bytecode и загружает один Singleton",
   "Читает только application.properties и создаёт бины по имени свойства"],
  "При старте Spring сканирует пакеты, находит компоненты по аннотациям, строит BeanDefinition, создаёт экземпляры и внедряет зависимости через конструктор, сеттер или поле.")

Q("S", "Spring", "Как Spring решает циклические зависимости бинов?",
  "Через early reference / @Lazy; цикл через конструктор — ошибка",
  ["Всегда создаёт прокси CGLIB для обоих бинов",
   "Разрешает любые циклы через конструктор с @Autowired",
   "Откладывает создание обоих бинов до первого HTTP-запроса"],
  "Цикл через конструктор разрешить нельзя — будет ошибка. Через сеттер/поле Spring может внедрить early reference или прокси через @Lazy.")

Q("S", "Многопоточность", "Что такое deadlock?",
  "Потоки взаимно ждут ресурсы, удерживаемые друг другом",
  ["Один поток бесконечно крутится в busy-wait",
   "Главный поток завершился, а daemon-потоки ещё работают",
   "Пул потоков исчерпал лимит и отклоняет новые задачи"],
  "Deadlock — взаимная блокировка: каждый поток держит ресурс и ждёт ресурс другого. Классика: A→B и B→A.")

Q("S", "Многопоточность", "Как избежать deadlock при переводах между счетами?",
  "Захватывать локи в едином порядке (например, по id счёта)",
  ["Использовать только один глобальный synchronized на весь сервис",
   "Всегда блокировать счёт с большим балансом первым",
   "Отключить транзакции и работать только с AtomicLong"],
  "Стандартное решение — единый порядок захвата локов (по id), tryLock с таймаутом, стратегии Wait-Die/Wound-Wait.")

Q("S", "БД блокировки", "Чем отличается пессимистичная блокировка от оптимистичной?",
  "Пессимистичная блокирует строку сразу; оптимистичная проверяет версию при коммите",
  ["Пессимистичная только в NoSQL; оптимистичная только в SQL",
   "Оптимистичная использует SELECT FOR UPDATE; пессимистичная — версионное поле",
   "Пессимистичная быстрее при редких конфликтах записи"],
  "Пессимистичная — блокируем строку заранее (FOR UPDATE), другие ждут. Оптимистичная — читаем версию, при конфликте откат и повтор; подходит при редких коллизиях.")

Q("S", "БД блокировки", "Что делает SELECT ... FOR UPDATE?",
  "Блокирует выбранные строки до конца транзакции",
  ["Сразу удаляет строки после чтения",
   "Читает данные без блокировки, но с hint на индекс",
   "Обновляет строки атомарно без WHERE"],
  "SELECT FOR UPDATE берёт эксклюзивную блокировку на строки до commit/rollback — другие транзакции не могут их изменить.")

# ── A tier ──────────────────────────────────────────────────────────────
Q("A", "Java Core", "Каков контракт equals и hashCode?",
  "equals → одинаковый hashCode обязателен; обратное не гарантировано",
  ["hashCode → equals обязателен; equals может не совпадать",
   "equals и hashCode должны совпадать для всех объектов в иерархии",
   "hashCode переопределять не нужно, если есть equals"],
  "Если a.equals(b), то a.hashCode()==b.hashCode() обязательно. Обратное не обязательно (коллизии). Переопредил equals — переопредели hashCode.")

Q("A", "Java Core", "Почему ключ HashMap должен быть неизменяемым?",
  "Изменение hashCode после вставки ломает поиск в бакете",
  ["HashMap клонирует ключ при каждом put",
   "Mutable ключи запрещены компилятором Java",
   "Потому что HashMap сортирует ключи по compareTo"],
  "Хэш считается при вставке и определяет бакет. Если поле, влияющее на hashCode, изменится — get не найдёт объект. Поэтому ключи immutable (String, Integer).")

Q("A", "ООП", "Назови четыре принципа ООП.",
  "Инкапсуляция, наследование, полиморфизм, абстракция",
  ["Инкапсуляция, композиция, агрегация, абстракция",
   "SOLID, DRY, KISS, YAGNI",
   "Класс, объект, интерфейс, пакет"],
  "Инкапсуляция, наследование, полиморфизм, абстракция. На практике предпочитают композицию наследованию.")

Q("A", "ООП", "Чем композиция отличается от агрегации?",
  "Композиция — часть не живёт без целого; агрегация — части независимы",
  ["Композиция — is-a; агрегация — has-a",
   "Агрегация всегда через наследование; композиция — через интерфейс",
   "Разницы нет — это синонимы в UML"],
  "Композиция — жёсткое владение (двигатель в машине). Агрегация — слабая связь (студенты в группе живут отдельно).")

Q("A", "ООП", "Когда выбрать интерфейс, а когда абстрактный класс?",
  "Интерфейс — контракт и множественная реализация; абстрактный класс — общий код и состояние",
  ["Интерфейс только до Java 7; дальше всегда abstract class",
   "Абстрактный класс можно инстанцировать через anonymous class",
   "Интерфейс хранит поля экземпляра; abstract class — только static"],
  "Абстрактный класс — частичная реализация + состояние, одно наследование. Интерфейс — контракт, несколько реализаций, без состояния (до Java 8).")

Q("A", "Коллекции", "ArrayList vs LinkedList — когда что?",
  "ArrayList почти всегда быстрее; LinkedList — редкие вставки по итератору",
  ["LinkedList быстрее для доступа по индексу O(1)",
   "ArrayList не поддерживает null элементы",
   "LinkedList — единственный thread-safe List в JDK"],
  "ArrayList — массив, O(1) доступ, cache-friendly. LinkedList — O(n) доступ, O(1) вставка по узлу; на практике LinkedList нужен редко.")

Q("A", "Коллекции", "Как реализовать LRU-кэш в Java?",
  "LinkedHashMap(accessOrder=true) + removeEldestEntry",
  ["HashMap + PriorityQueue по timestamp",
   "TreeMap с Comparator по lastAccess",
   "ConcurrentHashMap с TTL в значениях"],
  "LinkedHashMap с accessOrder=true и переопределённым removeEldestEntry автоматически вытесняет старейший элемент при превышении размера.")

Q("A", "Java Core", "Comparable vs Comparator?",
  "Comparable — естественный порядок внутри класса; Comparator — внешний",
  ["Comparator только для примитивов; Comparable — для объектов",
   "Comparable изменяет исходный список; Comparator — нет",
   "Comparator обязателен для HashSet; Comparable — для HashMap"],
  "Comparable (compareTo) — естественный порядок в классе. Comparator (compare) — внешний, можно несколько, удобно через Comparator.comparing().")

Q("A", "JVM", "Какие основные сборщики мусора есть в JVM?",
  "Serial, Parallel, G1, ZGC, Shenandoah",
  ["Serial, CMS, G1, PermGen Cleaner",
   "Только G1 и ZGC в современных JDK",
   "Mark-Sweep, Mark-Compact, Copying — без имён реализаций"],
  "Serial, Parallel, G1 (дефолт), ZGC и Shenandoah (низкие паузы). Принцип: найти недостижимые от GC roots объекты, обычно поколенчески.")

Q("A", "Java Core", "Почему для денег не используют float/double?",
  "Двоичная плавающая точка даёт ошибки округления; нужен BigDecimal",
  ["float быстрее BigDecimal, поэтому его используют в банках",
   "double хранит точность до 10 знаков после запятой всегда",
   "Java автоматически округляет double до копеек при println"],
  "float/double — двоичная плавающая точка, ошибки округления. Для денег — BigDecimal; для счётчиков при риске переполнения — long.")

Q("A", "Индексы", "Какие типы индексов знаешь в реляционных БД?",
  "B-Tree, Hash, составной, частичный, уникальный, полнотекстовый",
  ["Только B-Tree и Hash",
   "Primary, Foreign, Unique — это типы индексов",
   "Clustered и Non-clustered — единственные два типа"],
  "B-Tree (дефолт), Hash (равенство), составной (left-prefix), частичный, уникальный, полнотекстовый, кластеризованный.")

Q("A", "Индексы", "Какова цена наличия индексов?",
  "Ускоряют чтение, замедляют запись и занимают место",
  ["Замедляют и чтение, и запись — только для уникальности",
   "Ускоряют только INSERT; SELECT не затрагивают",
   "Индексы бесплатны, если таблица меньше 1 млн строк"],
  "Индексы ускоряют SELECT/JOIN, но каждая запись требует обновления индекса — INSERT/UPDATE/DELETE медленнее, плюс место на диске.")

Q("A", "JVM", "Что такое Reflection в Java?",
  "Доступ к структуре класса в runtime: поля, методы, аннотации",
  ["Компиляция Java в нативный код на лету",
   "Подмена bytecode при загрузке класса ClassLoader",
   "Анализ исходников через AST без запуска JVM"],
  "Reflection — introspection в runtime: поля, методы, аннотации RUNTIME, динамическое создание и вызов.")

Q("A", "JVM", "Как устроена цепочка ClassLoader в Java?",
  "Bootstrap → Platform → Application; делегирование родителю",
  ["Application → Bootstrap → Platform — снизу вверх",
   "Каждый ClassLoader грузит классы независимо без делегирования",
   "Только один ClassLoader на всё приложение"],
  "Иерархия с делегированием: сначала спрашивают родителя, потом грузят сами. Bootstrap → Platform → Application.")

Q("A", "Транзакции", "Что такое MVCC в PostgreSQL?",
  "Версии строк + снимок транзакции; читатели не блокируют писателей",
  ["Блокировка всей таблицы на время SELECT",
   "Один глобальный lock на базу для записи",
   "Кэширование результатов SELECT в Redis"],
  "Multi-Version Concurrency Control: новая версия строки на изменение, читатели видят свой snapshot. SERIALIZABLE в PG — SSI поверх snapshot isolation.")

Q("A", "Многопоточность", "Как реализован CAS в Atomic-классах?",
  "Compare-And-Swap на уровне CPU; повтор в цикле при конфликте",
  ["synchronized на каждый вызов getAndIncrement",
   "Lock-free очередь в heap для каждой операции",
   "volatile + Thread.yield() до успеха"],
  "CAS: сравни с ожидаемым, замени если совпало, иначе повтор. Реализация через CMPXCHG / VarHandle. Lock-free, не просто volatile++.",
  err=True, note="Интервьюер тянул к сути реализации.")

Q("A", "Паттерны", "Назови три категории паттернов GoF с примерами.",
  "Порождающие, структурные, поведенческие",
  ["Архитектурные, инфраструктурные, доменные",
   "Singleton, Factory, Observer — три категории",
   "Creational, SOLID, Reactive"],
  "Порождающие: Singleton, Factory, Builder. Структурные: Adapter, Decorator, Proxy. Поведенческие: Strategy, Observer, Command.")

Q("A", "Сети", "Что делает DNS?",
  "Преобразует доменное имя в IP-адрес",
  ["Преобразует MAC в IP в локальной сети",
   "Выдаёт IP-адрес и маску клиенту автоматически",
   "Переводит приватный IP в публичный на роутере"],
  "DNS — Domain Name System: резолвинг имени (example.com) в IP.", err=True)

Q("A", "Сети", "Что делает ARP?",
  "Определяет MAC-адрес по IP в локальной сети",
  ["Резолвит доменное имя в IP",
   "Назначает IP клиенту при подключении к Wi‑Fi",
   "Шифрует трафик на канальном уровне"],
  "ARP — Address Resolution Protocol: IP → MAC в пределах L2-сегмента.", err=True)

Q("A", "Сети", "Что делает DHCP?",
  "Автоматически выдаёт IP и сетевые параметры клиенту",
  ["Маршрутизирует пакеты между подсетями",
   "Преобразует домен в IP через кэш",
   "Создаёт VPN-туннель между хостами"],
  "DHCP — Dynamic Host Configuration Protocol: IP, маска, шлюз, DNS при подключении.", err=True)

Q("A", "Сети", "Что делает NAT?",
  "Переводит приватные IP в публичный (и обратно) на границе сети",
  ["Определяет MAC по IP в Ethernet",
   "Выдаёт сертификаты TLS для HTTPS",
   "Балансирует HTTP-запросы между серверами"],
  "NAT — Network Address Translation: private IP ↔ public IP на выходе в интернет.", err=True)

Q("A", "Сети", "На каком уровне OSI работают IP-маршрутизация и MAC-адреса?",
  "IP — сетевой (L3); MAC/кадры — канальный (L2)",
  ["IP — канальный; MAC — сетевой",
   "Оба на транспортном уровне (L4)",
   "IP — прикладной; MAC — физический"],
  "Маршрутизация между сетями — L3 (IP). MAC и Ethernet-кадры — L2.", err=True, note="Была путаница ARP/DNS/NAT.")

# ── B tier ──────────────────────────────────────────────────────────────
Q("B", "Kafka", "Чем Kafka отличается от классической очереди (RabbitMQ)?",
  "Durable-лог с retention; сообщения не удаляются после чтения",
  ["Сообщение удаляется сразу после ack потребителя",
   "Kafka не поддерживает партиции и порядок",
   "RabbitMQ хранит все сообщения на диске бессрочно по умолчанию"],
  "Kafka — распределённый лог: retention, чтение по offset, consumer groups, упорядоченность в партиции, высокая пропускная способность.")

Q("B", "Kafka", "Что если consumer-ов меньше, чем партиций?",
  "Один consumer может читать несколько партиций; лишние партиции не простаивают",
  ["Лишние партиции блокируются до появления consumer",
   "Kafka удаляет лишние партиции автоматически",
   "Сообщения теряются в партициях без consumer"],
  "Consumer group распределяет партиции между участниками. Если consumers < partitions — один consumer берёт несколько партиций.")

Q("B", "Kafka", "Что если consumer-ов больше, чем партиций?",
  "Лишние consumer-ы простаивают без назначенных партиций",
  ["Kafka создаёт новые партиции автоматически",
   "Лишние consumer-ы получают копию всех сообщений",
   "Kafka перенаправляет их в dead-letter queue"],
  "Максимум активных consumers в группе = число партиций. Лишние idle до rebalance или добавления партиций.")

Q("B", "Kafka", "Что такое exactly-once в Kafka?",
  "Идempotent producer + транзакции + read_committed consumer",
  ["Гарантия без дубликатов без участия producer",
   "Только один consumer на топик",
   "Отключение retry у producer"],
  "Exactly-once — комбинация idempotent producer, transactional writes и consumer с isolation.level=read_committed.")

Q("B", "REST", "Как сделать REST API надёжным?",
  "Идемпотентность, таймауты, retry с backoff, circuit breaker, DLQ",
  ["Только HTTPS и JWT",
   "Увеличить timeout до 5 минут на все вызовы",
   "Всегда использовать POST вместо GET"],
  "Идемпотентность (idempotency key для POST), таймауты, экспоненциальный backoff, circuit breaker, корректные статус-коды, DLQ.")

Q("B", "System Design", "Лента новостей: fan-out on read vs fan-out on write?",
  "Read — собирать при запросе; write — разлить пост подписчикам заранее",
  ["Read быстрее для знаменитостей с миллионами подписчиков",
   "Write дешевле по записи, чем read",
   "Разницы нет — всегда используют только push"],
  "Pull (fan-out on read) — дёшево писать, дорого читать. Push (fan-out on write) — быстрое чтение, дорого для «звёзд». Обычно гибрид + кэш.")

Q("B", "Микросервисы", "Что такое Saga?",
  "Цепочка локальных транзакций с компенсирующими действиями",
  ["Двухфазный commit между всеми сервисами",
   "Один глобальный lock на все микросервисы",
   "Паттерн кэширования read-through"],
  "Saga — распределённая транзакция без 2PC: локальные шаги + компенсации при сбое. Оркестрация или хореография.")

Q("B", "Тестирование", "Что мокать в unit-тестах с Mockito?",
  "Внешние зависимости: репозитории, HTTP-клиенты, очереди",
  ["Класс, который тестируем",
   "Все private-методы через reflection",
   "Примитивы и String"],
  "Мокаем внешние зависимости для изоляции логики. when/thenReturn, verify. Не мокаем SUT и простые value-объекты.")

Q("B", "Реактивность", "Зачем Spring WebFlux / Reactor?",
  "Неблокирующий I/O: много соединений малым числом потоков",
  ["Для красивого UI в браузере",
   "Чтобы заменить все synchronized блоки",
   "Только для CPU-bound вычислений на всех ядрах"],
  "Реактивность — про non-blocking I/O и backpressure (Mono/Flux), не про UI. Выигрыш на I/O-bound.",
  err=True, note="Ранее назвал «для UI» — неверно.")

Q("B", "Многопоточность", "ConcurrentHashMap vs Collections.synchronizedMap?",
  "ConcurrentHashMap лочит сегменты; synchronizedMap — всю карту",
  ["synchronizedMap быстрее при высокой конкуренции",
   "ConcurrentHashMap блокирует всю таблицу на каждый get",
   "Разницы в производительности нет"],
  "synchronizedMap — lock на всю map. ConcurrentHashMap — lock по bin/сегменту, чтения почти без блокировок.")

Q("B", "Многопоточность", "Что такое ThreadLocal и какая ловушка?",
  "Своя копия переменной на поток; в пулах нужно remove()",
  ["Глобальная переменная для всех потоков",
   "Аналог volatile для потоков",
   "Автоматически очищается GC без remove"],
  "ThreadLocal — значение на поток. В thread pool без remove() — утечка памяти и «грязное» состояние между задачами.")

Q("B", "Stream API", "Промежуточные vs терминальные операции Stream?",
  "Промежуточные ленивы; терминальные запускают конвейер",
  ["Все операции Stream выполняются eagerly",
   "Терминальные возвращают Stream",
   "filter и map — терминальные"],
  "Промежуточные (filter, map) ленивы. Терминальные (collect, count) запускают pipeline. Short-circuit: findFirst, limit.")

Q("B", "DDD", "Что такое bounded context?",
  "Граница, где термины модели однозначны",
  ["Пакет в Java с аннотацией @Context",
   "Один микросервис = один bounded context всегда",
   "Слой DAO в Spring"],
  "Bounded context — семантическая граница DDD: «Заказ» в sales и shipping значит разное.")

Q("B", "CQRS", "Кто меняет состояние в CQRS?",
  "Command пишет; Query только читает",
  ["Query обновляет read-модель и меняет write-store",
   "Command и Query всегда в одной таблице",
   "Только Event Sourcing без команд"],
  "Command — изменение без возврата данных. Query — чтение без побочных эффектов.",
  err=True, note="Раньше путал: говорил «Query меняет».")

Q("B", "Масштабирование", "Репликация vs шардирование?",
  "Репликация — копии данных; шардирование — разные данные на узлах",
  ["Шардирование — копии одной таблицы на всех узлах",
   "Репликация — горизонтальное разбиение по ключу",
   "Это синонимы PostgreSQL partitioning"],
  "Репликация — те же данные на нескольких узлах (HA, read scale). Шардирование — данные partitioned по ключу на разные узлы.")

Q("B", "Паттерны", "Double-checked locking для Singleton — зачем volatile?",
  "Чтобы не опубликовать недоинициализированный объект",
  ["Чтобы ускорить synchronized без семантики",
   "volatile заменяет synchronized полностью",
   "Чтобы singleton был thread-local"],
  "Без volatile другой поток может увидеть partially constructed instance. DCL: volatile поле + synchronized блок + двойная проверка.")

Q("B", "SQL", "Чем WHERE отличается от HAVING?",
  "WHERE фильтрует строки до группировки; HAVING — после, по агрегатам",
  ["HAVING работает без GROUP BY всегда",
   "WHERE может фильтровать COUNT(*) > 5",
   "WHERE и HAVING — синонимы в PostgreSQL"],
  "GROUP BY группирует для агрегатов. WHERE — до группировки. HAVING — после, по результатам агрегации (HAVING COUNT(*) > 5).")

# ── C tier ──────────────────────────────────────────────────────────────
Q("C", "Java Core", "Чем String отличается от StringBuilder?",
  "String immutable; StringBuilder — изменяемый, для конкатенации в цикле",
  ["StringBuilder immutable после append",
   "String быстрее StringBuilder в цикле",
   "String хранится только в stack"],
  "String immutable, thread-safe, кэш в pool. StringBuilder — мутабельный, быстрый для сборки строк. StringBuffer — synchronized версия.")

Q("C", "Java Core", "Что такое String Pool (intern)?",
  "Пул литералов; одинаковые строки переиспользуются",
  ["Пул всех объектов String в heap без dedup",
   "Кэш только для строк из new String()",
   "Область памяти для char[] в native memory"],
  "String pool хранит литералы; intern() позволяет переиспользовать каноническую копию.")

Q("C", "Сети", "Главное отличие HTTP/2 от HTTP/1.1?",
  "Мультиплексирование потоков в одном TCP-соединении",
  ["HTTP/2 использует только UDP",
   "HTTP/1.1 уже мультиплексирует запросы по умолчанию",
   "HTTP/2 отказался от заголовков"],
  "HTTP/2 — multiplexing, binary frames, HPACK сжатие заголовков, server push (редко используется).")

Q("C", "Сети", "Что такое gRPC?",
  "RPC поверх HTTP/2 с Protobuf и кодогенерацией",
  ["REST JSON только с XML-обёрткой",
   "Очередь сообщений как Kafka",
   "Протокол только для gRPC-Gateway без HTTP"],
  "gRPC — RPC на HTTP/2, Protobuf, стриминг, контракты через .proto, компактнее JSON REST.")

Q("C", "Контейнеры", "Контейнер vs виртуальная машина?",
  "Контейнер делит ядро ОС; VM — отдельная ОС на гипервизоре",
  ["Контейнер включает полную гостевую ОС",
   "VM всегда легче контейнера",
   "Контейнер — это тип VM с меньшим RAM"],
  "VM виртуализирует железо + своя ОС. Контейнер — namespaces + cgroups, общее ядро, быстрый старт.")

Q("C", "Java Core", "Checked vs unchecked исключения?",
  "Checked — обязаны обработать; unchecked (RuntimeException) — нет",
  ["Unchecked требуют throws в сигнатуре",
   "Error — подкласс RuntimeException",
   "Checked — только в Spring приложениях"],
  "Checked (Exception) — compile-time проверка. Unchecked (RuntimeException) — ошибки логики. Error — фатальные (OutOfMemory).")

Q("C", "Java Core", "Зачем Optional в Java?",
  "Явно обозначить отсутствие значения в возвращаемом результате",
  ["Заменить null в полях entity",
   "Ускорить доступ к полям объекта",
   "Обязательный параметр каждого REST API"],
  "Optional — для return type, заставляет обработать empty (map, orElseThrow). Не для полей/параметров/DTO.")

Q("C", "JVM", "Утечка памяти — это про heap или stack?",
  "Heap: объекты достижимы по ссылкам, но логически не нужны",
  ["Stack: переменные local не удаляются",
   "Stack: frame не pop-ится при return",
   "Heap: GC намеренно не собирает young gen"],
  "Утечка — heap: статические коллекции, незакрытые ресурсы, ThreadLocal в pool. Stack overflow — другое (глубокая рекурсия).",
  err=True, note="Раньше путал heap и stack.")

Q("C", "Масштабирование", "Синхронная vs асинхронная репликация БД?",
  "Sync — ждём реплику перед commit (выше latency); async — commit сразу",
  ["Async сильнее консистентность sync",
   "Sync не влияет на latency записи",
   "Async гарантирует zero data loss всегда"],
  "Sync replication — подтверждение реплики до commit. Async — быстрее, но возможна потеря последних транзакций при сбое.")

Q("C", "БД", "Партиционирование vs шардирование?",
  "Партиционирование — части таблицы в одной БД; шардирование — по узлам",
  ["Шардирование только внутри одного PostgreSQL instance",
   "Партиционирование всегда через сеть",
   "Это одно и то же в MySQL"],
  "Partition — split таблицы в одной БД (range/hash). Sharding — partition по разным серверам для horizontal scale.")

Q("C", "Коллекции", "Почему Arrays.asList().add() падает?",
  "Возвращает fixed-size обёртку над массивом",
  ["Arrays.asList клонирует массив в новый ArrayList",
   "add запрещён только для primitive arrays",
   "List из asList thread-safe и immutable навсегда"],
  "Arrays.asList — view с фиксированным размером; add/remove → UnsupportedOperationException. Нужен new ArrayList<>(Arrays.asList(...)).")

# ── TODO: created myself ────────────────────────────────────────────────
Q("B", "JVM", "Прервётся ли поток, если в main удалить ссылку на Thread?",
  "Нет — поток живёт, пока не завершит run() (если не daemon)",
  ["Да — GC сразу останавливает поток",
   "Да — JVM завершает все потоки при null в main",
   "Только если поток помечен volatile"],
  "Ссылка в main не удерживает поток. Non-daemon потоки держат JVM живой. Daemon завершатся при exit main. GC не «убивает» потоки.",
  note="Вопрос из TODO — проверка понимания GC и потоков.")

Q("B", "JVM", "С какой версии Java G1 стал сборщиком по умолчанию?",
  "Java 9 (до этого — Parallel GC в Java 8)",
  ["Java 8",
   "Java 11 только на серверах",
   "Java 17 — первый раз G1"],
  "G1 default с Java 9. Java 8 default — Parallel GC. Современные GC (ZGC, Shenandoah) — отдельные флаги.")

Q("B", "GRASP", "Что такое Information Expert в GRASP?",
  "Назначить ответственность классу, у которого есть нужная информация",
  ["Всегда передавать логику в Controller",
   "Один Service на всё приложение",
   "Expert — это Singleton паттерн"],
  "Information Expert: метод там, где данные. Low Coupling / High Cohesion — соседние принципы GRASP.",
  note="Из TODO — GRASP редко спрашивают, но полезно.")

Q("B", "GRASP", "Low Coupling и High Cohesion — суть?",
  "Минимум зависимостей между классами; максимум связности внутри класса",
  ["Максимум зависимостей для гибкости",
   "Cohesion — число public методов > 20",
   "Coupling — использование только final классов"],
  "Low Coupling — слабая связь между модулями. High Cohesion — класс делает одну связную задачу хорошо.")

Q("B", "Миграции БД", "Flyway / Liquibase — зачем?",
  "Версионирование и автоматическое применение миграций схемы БД",
  ["ORM Hibernate замена",
   "Резервное копирование production nightly",
   "Шардирование таблиц по hash"],
  "Flyway/Liquibase — migration scripts в VCS, repeatable deploy, audit history. Hibernate ddl-auto=update не для prod.")

Q("B", "Spring", "Что делает @Transactional?",
  "Открывает/коммитит/откатывает транзакцию вокруг метода через AOP",
  ["Создаёт новый поток для каждого вызова",
   "Кэширует результат метода в Redis",
   "Заменяет synchronized на уровне JVM"],
  "Spring управляет transaction boundary: begin, commit, rollback. Работает через proxy — только public методы бина снаружи.")

Q("B", "Spring", "Сработает ли @Transactional на private методе?",
  "Нет — Spring AOP не перехватывает private",
  ["Да — если включить aspectj-weaver",
   "Да — для всех методов в @Service",
   "Да — но только для read-only"],
  "Proxy видит только public методы бина. private / internal call (this.foo()) — self-invocation, транзакция не начнётся.",
  note="Из TODO — частый лайв-coding вопрос.")

Q("B", "Spring", "Почему @Transactional не работает при вызове this.method()?",
  "Self-invocation минует Spring proxy",
  ["Transactional работает только в main()",
   "Нужен keyword synchronized",
   "Только один @Transactional на класс"],
  "Вызов через this — не через proxy, AOP не применяется. Решение: вынести в другой bean, self-injection, AspectJ weaving.")

Q("B", "SQL", "Как выбрать поле для индекса?",
  "Высокая селективность, часто в WHERE/JOIN, не слишком частые UPDATE",
  ["Всегда индексировать каждое поле таблицы",
   "Только boolean флаги",
   "Только TEXT и JSONB колонки"],
  "Индекс на колонках из WHERE/JOIN с хорошей селективностью. Не индексировать всё подряд — цена на write.")

Q("B", "SQL", "Long vs UUID для первичного ключа?",
  "Long — компактнее, быстрее индекс; UUID — глобальная уникальность, но шире и random I/O",
  ["UUID всегда быстрее B-Tree",
   "Long нельзя использовать в distributed системах",
   "UUID sequential всегда хуже Long без исключений"],
  "Long/BIGSERIAL — меньше, монотонный insert в B-Tree. UUID — merge реплик, API, но 16 байт и random UUID фрагментирует индекс.")

Q("B", "SQL", "Клиенты без заказов — какой JOIN?",
  "LEFT JOIN orders + WHERE orders.id IS NULL (или NOT EXISTS)",
  ["INNER JOIN — покажет клиентов без заказов",
   "CROSS JOIN clients orders",
   "RIGHT JOIN только orders"],
  "Классика: SELECT c.* FROM clients c LEFT JOIN orders o ON o.client_id = c.id WHERE o.id IS NULL. Или NOT EXISTS.",
  note="Из TODO — классическая SQL задача на собесах.")

Q("A", "SOLID", "Что означает S в SOLID (классически)?",
  "Single Responsibility — один класс, одна причина для изменения",
  ["Single method — один public метод на класс",
   "Single instance — только один объект класса",
   "Single package — класс в одном package"],
  "SRP: класс меняется только по одной оси ответственности. На собесах иногда ждут «одна функция» — уточняй формулировку.",
  note="Из TODO — иногда ждут habr-версию «одна функция».")

Q("A", "SOLID", "Расшифруй O и L в SOLID.",
  "Open/Closed — открыт для расширения, закрыт для изменения; Liskov — подтипы заменяемы",
  ["Open — все методы public; Liskov — только наследование",
   "Open — open source; Liskov — list interface",
   "Open API; Liskov substitution — только для Java 17"],
  "OCP — расширяем поведение без правки существующего кода. LSP — подкласс не ломает контракт базового класса.")

Q("B", "Java Core", "finally vs try-with-resources?",
  "try-with-resources автоматически закрывает AutoCloseable; finally — для любого cleanup",
  ["finally всегда быстрее try-with-resources",
   "try-with-resources не вызывает close при exception",
   "finally заменяет catch полностью"],
  "try-with-resources (Java 7+) вызывает close() автоматически, suppress exceptions. finally — ручной cleanup, риск забыть close.",
  note="Из TODO.")

Q("B", "Java Core", "Область видимости переменной, объявленной в try-with-resources?",
  "Только внутри try-блока; ресурс закрыт после блока",
  ["На весь метод",
   "На весь класс если final",
   "До конца catch, но не finally"],
  "Resource в try-with-resources scoped to try block. close() вызывается до выхода из try/catch.")

Q("B", "Микросервисы", "Что гласит теорема CAP?",
  "Из Consistency, Availability, Partition tolerance — одновременно только два",
  ["Можно иметь все три при Kafka",
   "CAP — про CPU, ALU, Pipeline",
   "Consistency и Availability всегда вместе в SQL"],
  "При network partition (P) выбирают между C (strong consistency) и A (availability). CP — ZooKeeper; AP — Cassandra.")

Q("B", "Микросервисы", "Transaction Outbox — зачем?",
  "Атомарно записать в БД и событие для брокера без dual write",
  ["Дублировать каждую таблицу в Redis",
   "Заменить Saga полностью",
   "Хранить только dead-letter сообщения"],
  "Outbox: в одной локальной транзакции business row + outbox row; отдельный relay публикует в Kafka/Rabbit.")

Q("B", "SQL", "Зачем смотреть EXPLAIN план запроса?",
  "Увидеть seq scan vs index scan, cost, join order — найти узкое место",
  ["Только для проверки синтаксиса SQL",
   "EXPLAIN блокирует таблицу на чтение",
   "Заменяет профилирование JVM"],
  "EXPLAIN (ANALYZE, BUFFERS) показывает как СУБД выполнит запрос: индексы, nested loop, cost, rows.")

Q("B", "SQL", "Расшифруй ACID для транзакций.",
  "Atomicity, Consistency, Isolation, Durability",
  ["Async, Cache, Index, Data",
   "Availability, Consistency, Isolation, Distribution",
   "Atomic, Concurrent, Isolated, Distributed"],
  "Atomicity — всё или ничего. Consistency — инварианты. Isolation — уровни изоляции. Durability — после commit данные сохранены.")

Q("B", "Многопоточность", "Mutex vs synchronized в Java?",
  "synchronized — встроенный монитор JVM; Mutex — явный lock (ReentrantLock)",
  ["Mutex быстрее synchronized всегда",
   "synchronized работает только в static методах",
   "Mutex — только в operating system, Java не поддерживает"],
  "synchronized — monitor enter/exit на object. ReentrantLock — явный lock/unlock, tryLock, fairness.")


def main():
    out = textwrap.dedent('''\
        # -*- coding: utf-8 -*-
        """Банк вопросов для Telegram-тренажёра.
        Поля: t, topic, err, q, correct, wrong[], a, note?.
        Сгенерировано gen_bank.py — правки в gen_bank.py, затем python gen_bank.py
        """

        QUESTIONS = ''')
    out += json.dumps(RAW, ensure_ascii=False, indent=4)
    out = out.replace(": false", ": False").replace(": true", ": True")
    out += "\n"
    path = __file__.replace("gen_bank.py", "questions.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote {len(RAW)} questions to {path}")


if __name__ == "__main__":
    main()
