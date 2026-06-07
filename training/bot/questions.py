# -*- coding: utf-8 -*-
"""Банк вопросов для Telegram-тренажёра.
Поля: t, topic, err, q, correct, wrong[], a, note?.
Сгенерировано gen_bank.py — правки в gen_bank.py, затем python gen_bank.py
"""

QUESTIONS = [
    {
        "t": "S",
        "topic": "Транзакции",
        "err": False,
        "q": "Какие уровни изоляции транзакций определены в SQL?",
        "correct": "READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE",
        "wrong": [
            "READ COMMITTED, REPEATABLE READ, SERIALIZABLE, SNAPSHOT",
            "READ UNCOMMITTED, READ COMMITTED, SERIALIZABLE, READ SNAPSHOT",
            "READ COMMITTED, REPEATABLE READ, PHANTOM READ, SERIALIZABLE"
        ],
        "a": "Стандарт SQL определяет четыре уровня: READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE. Чем выше уровень — тем меньше аномалий чтения, но ниже параллелизм."
    },
    {
        "t": "S",
        "topic": "Транзакции",
        "err": False,
        "q": "Какой уровень изоляции по умолчанию в PostgreSQL и MySQL (InnoDB)?",
        "correct": "PostgreSQL — READ COMMITTED; MySQL InnoDB — REPEATABLE READ",
        "wrong": [
            "Оба — REPEATABLE READ",
            "PostgreSQL — REPEATABLE READ; MySQL — READ COMMITTED",
            "PostgreSQL — SERIALIZABLE; MySQL — READ UNCOMMITTED"
        ],
        "a": "PostgreSQL и Oracle по умолчанию используют READ COMMITTED. MySQL с движком InnoDB — REPEATABLE READ."
    },
    {
        "t": "S",
        "topic": "Транзакции",
        "err": True,
        "q": "Что такое грязное чтение (dirty read)?",
        "correct": "Транзакция читает незакоммиченные изменения другой транзакции",
        "wrong": [
            "Транзакция читает только закоммиченные данные дважды с разным результатом",
            "Две транзакции одновременно пишут в одну строку без блокировки",
            "Чтение данных из другой схемы БД без прав доступа"
        ],
        "a": "Грязное чтение — когда транзакция видит незакоммиченные изменения другой. На уровне READ COMMITTED и выше это запрещено.",
        "note": "Раньше отвечал неверно — учить."
    },
    {
        "t": "S",
        "topic": "Транзакции",
        "err": True,
        "q": "Почему в PostgreSQL READ UNCOMMITTED фактически = READ COMMITTED?",
        "correct": "MVCC не показывает незакоммиченные версии строк — dirty read невозможен",
        "wrong": [
            "PostgreSQL автоматически повышает уровень до SERIALIZABLE",
            "READ UNCOMMITTED в PG блокирует все чтения shared lock",
            "Потому что PG не поддерживает MVCC для чтения"
        ],
        "a": "В PostgreSQL из-за MVCC каждая транзакция видит свой снимок данных; незакоммиченные версии строк ей недоступны, поэтому настоящего dirty read нет."
    },
    {
        "t": "S",
        "topic": "JMM",
        "err": True,
        "q": "Делает ли volatile операции атомарными?",
        "correct": "Нет — volatile не делает read-modify-write атомарным",
        "wrong": [
            "Да, любая операция над volatile полем атомарна",
            "Да, но только для примитивов int и boolean",
            "Да, если поле объявлено final и volatile одновременно"
        ],
        "a": "volatile даёт видимость и запрет переупорядочивания, но count++ — это read-modify-write из трёх шагов и не атомарен. Нужны Atomic*, synchronized или Lock.",
        "note": "Задача «0 или 13»: result не был volatile."
    },
    {
        "t": "S",
        "topic": "JMM",
        "err": False,
        "q": "Что такое happens-before в Java Memory Model?",
        "correct": "Гарантия видимости: результаты действия A будут видны в B",
        "wrong": [
            "Гарантия, что поток A завершится раньше потока B по wall-clock",
            "Порядок вызова методов в одном synchronized-блоке",
            "Синхронная очередь событий между потоками в ExecutorService"
        ],
        "a": "happens-before — отношение упорядочивания: если A happens-before B, результаты A видны в B. Примеры: unlock→lock, запись volatile→чтение, start потока→его код."
    },
    {
        "t": "S",
        "topic": "Spring",
        "err": False,
        "q": "Как Spring DI-контейнер создаёт и связывает бины?",
        "correct": "Сканирует классы, строит BeanDefinition, создаёт бины и внедряет зависимости",
        "wrong": [
            "Создаёт все бины через reflection без метаданных",
            "Компилирует конфигурацию в bytecode и загружает один Singleton",
            "Читает только application.properties и создаёт бины по имени свойства"
        ],
        "a": "При старте Spring сканирует пакеты, находит компоненты по аннотациям, строит BeanDefinition, создаёт экземпляры и внедряет зависимости через конструктор, сеттер или поле."
    },
    {
        "t": "S",
        "topic": "Spring",
        "err": False,
        "q": "Как Spring решает циклические зависимости бинов?",
        "correct": "Через early reference / @Lazy; цикл через конструктор — ошибка",
        "wrong": [
            "Всегда создаёт прокси CGLIB для обоих бинов",
            "Разрешает любые циклы через конструктор с @Autowired",
            "Откладывает создание обоих бинов до первого HTTP-запроса"
        ],
        "a": "Цикл через конструктор разрешить нельзя — будет ошибка. Через сеттер/поле Spring может внедрить early reference или прокси через @Lazy."
    },
    {
        "t": "S",
        "topic": "Многопоточность",
        "err": False,
        "q": "Что такое deadlock?",
        "correct": "Потоки взаимно ждут ресурсы, удерживаемые друг другом",
        "wrong": [
            "Один поток бесконечно крутится в busy-wait",
            "Главный поток завершился, а daemon-потоки ещё работают",
            "Пул потоков исчерпал лимит и отклоняет новые задачи"
        ],
        "a": "Deadlock — взаимная блокировка: каждый поток держит ресурс и ждёт ресурс другого. Классика: A→B и B→A."
    },
    {
        "t": "S",
        "topic": "Многопоточность",
        "err": False,
        "q": "Как избежать deadlock при переводах между счетами?",
        "correct": "Захватывать локи в едином порядке (например, по id счёта)",
        "wrong": [
            "Использовать только один глобальный synchronized на весь сервис",
            "Всегда блокировать счёт с большим балансом первым",
            "Отключить транзакции и работать только с AtomicLong"
        ],
        "a": "Стандартное решение — единый порядок захвата локов (по id), tryLock с таймаутом, стратегии Wait-Die/Wound-Wait."
    },
    {
        "t": "S",
        "topic": "БД блокировки",
        "err": False,
        "q": "Чем отличается пессимистичная блокировка от оптимистичной?",
        "correct": "Пессимистичная блокирует строку сразу; оптимистичная проверяет версию при коммите",
        "wrong": [
            "Пессимистичная только в NoSQL; оптимистичная только в SQL",
            "Оптимистичная использует SELECT FOR UPDATE; пессимистичная — версионное поле",
            "Пессимистичная быстрее при редких конфликтах записи"
        ],
        "a": "Пессимистичная — блокируем строку заранее (FOR UPDATE), другие ждут. Оптимистичная — читаем версию, при конфликте откат и повтор; подходит при редких коллизиях."
    },
    {
        "t": "S",
        "topic": "БД блокировки",
        "err": False,
        "q": "Что делает SELECT ... FOR UPDATE?",
        "correct": "Блокирует выбранные строки до конца транзакции",
        "wrong": [
            "Сразу удаляет строки после чтения",
            "Читает данные без блокировки, но с hint на индекс",
            "Обновляет строки атомарно без WHERE"
        ],
        "a": "SELECT FOR UPDATE берёт эксклюзивную блокировку на строки до commit/rollback — другие транзакции не могут их изменить."
    },
    {
        "t": "A",
        "topic": "Java Core",
        "err": False,
        "q": "Каков контракт equals и hashCode?",
        "correct": "equals → одинаковый hashCode обязателен; обратное не гарантировано",
        "wrong": [
            "hashCode → equals обязателен; equals может не совпадать",
            "equals и hashCode должны совпадать для всех объектов в иерархии",
            "hashCode переопределять не нужно, если есть equals"
        ],
        "a": "Если a.equals(b), то a.hashCode()==b.hashCode() обязательно. Обратное не обязательно (коллизии). Переопредил equals — переопредели hashCode."
    },
    {
        "t": "A",
        "topic": "Java Core",
        "err": False,
        "q": "Почему ключ HashMap должен быть неизменяемым?",
        "correct": "Изменение hashCode после вставки ломает поиск в бакете",
        "wrong": [
            "HashMap клонирует ключ при каждом put",
            "Mutable ключи запрещены компилятором Java",
            "Потому что HashMap сортирует ключи по compareTo"
        ],
        "a": "Хэш считается при вставке и определяет бакет. Если поле, влияющее на hashCode, изменится — get не найдёт объект. Поэтому ключи immutable (String, Integer)."
    },
    {
        "t": "A",
        "topic": "ООП",
        "err": False,
        "q": "Назови четыре принципа ООП.",
        "correct": "Инкапсуляция, наследование, полиморфизм, абстракция",
        "wrong": [
            "Инкапсуляция, композиция, агрегация, абстракция",
            "SOLID, DRY, KISS, YAGNI",
            "Класс, объект, интерфейс, пакет"
        ],
        "a": "Инкапсуляция, наследование, полиморфизм, абстракция. На практике предпочитают композицию наследованию."
    },
    {
        "t": "A",
        "topic": "ООП",
        "err": False,
        "q": "Чем композиция отличается от агрегации?",
        "correct": "Композиция — часть не живёт без целого; агрегация — части независимы",
        "wrong": [
            "Композиция — is-a; агрегация — has-a",
            "Агрегация всегда через наследование; композиция — через интерфейс",
            "Разницы нет — это синонимы в UML"
        ],
        "a": "Композиция — жёсткое владение (двигатель в машине). Агрегация — слабая связь (студенты в группе живут отдельно)."
    },
    {
        "t": "A",
        "topic": "ООП",
        "err": False,
        "q": "Когда выбрать интерфейс, а когда абстрактный класс?",
        "correct": "Интерфейс — контракт и множественная реализация; абстрактный класс — общий код и состояние",
        "wrong": [
            "Интерфейс только до Java 7; дальше всегда abstract class",
            "Абстрактный класс можно инстанцировать через anonymous class",
            "Интерфейс хранит поля экземпляра; abstract class — только static"
        ],
        "a": "Абстрактный класс — частичная реализация + состояние, одно наследование. Интерфейс — контракт, несколько реализаций, без состояния (до Java 8)."
    },
    {
        "t": "A",
        "topic": "Коллекции",
        "err": False,
        "q": "ArrayList vs LinkedList — когда что?",
        "correct": "ArrayList почти всегда быстрее; LinkedList — редкие вставки по итератору",
        "wrong": [
            "LinkedList быстрее для доступа по индексу O(1)",
            "ArrayList не поддерживает null элементы",
            "LinkedList — единственный thread-safe List в JDK"
        ],
        "a": "ArrayList — массив, O(1) доступ, cache-friendly. LinkedList — O(n) доступ, O(1) вставка по узлу; на практике LinkedList нужен редко."
    },
    {
        "t": "A",
        "topic": "Коллекции",
        "err": False,
        "q": "Как реализовать LRU-кэш в Java?",
        "correct": "LinkedHashMap(accessOrder=true) + removeEldestEntry",
        "wrong": [
            "HashMap + PriorityQueue по timestamp",
            "TreeMap с Comparator по lastAccess",
            "ConcurrentHashMap с TTL в значениях"
        ],
        "a": "LinkedHashMap с accessOrder=true и переопределённым removeEldestEntry автоматически вытесняет старейший элемент при превышении размера."
    },
    {
        "t": "A",
        "topic": "Java Core",
        "err": False,
        "q": "Comparable vs Comparator?",
        "correct": "Comparable — естественный порядок внутри класса; Comparator — внешний",
        "wrong": [
            "Comparator только для примитивов; Comparable — для объектов",
            "Comparable изменяет исходный список; Comparator — нет",
            "Comparator обязателен для HashSet; Comparable — для HashMap"
        ],
        "a": "Comparable (compareTo) — естественный порядок в классе. Comparator (compare) — внешний, можно несколько, удобно через Comparator.comparing()."
    },
    {
        "t": "A",
        "topic": "JVM",
        "err": False,
        "q": "Какие основные сборщики мусора есть в JVM?",
        "correct": "Serial, Parallel, G1, ZGC, Shenandoah",
        "wrong": [
            "Serial, CMS, G1, PermGen Cleaner",
            "Только G1 и ZGC в современных JDK",
            "Mark-Sweep, Mark-Compact, Copying — без имён реализаций"
        ],
        "a": "Serial, Parallel, G1 (дефолт), ZGC и Shenandoah (низкие паузы). Принцип: найти недостижимые от GC roots объекты, обычно поколенчески."
    },
    {
        "t": "A",
        "topic": "Java Core",
        "err": False,
        "q": "Почему для денег не используют float/double?",
        "correct": "Двоичная плавающая точка даёт ошибки округления; нужен BigDecimal",
        "wrong": [
            "float быстрее BigDecimal, поэтому его используют в банках",
            "double хранит точность до 10 знаков после запятой всегда",
            "Java автоматически округляет double до копеек при println"
        ],
        "a": "float/double — двоичная плавающая точка, ошибки округления. Для денег — BigDecimal; для счётчиков при риске переполнения — long."
    },
    {
        "t": "A",
        "topic": "Индексы",
        "err": False,
        "q": "Какие типы индексов знаешь в реляционных БД?",
        "correct": "B-Tree, Hash, составной, частичный, уникальный, полнотекстовый",
        "wrong": [
            "Только B-Tree и Hash",
            "Primary, Foreign, Unique — это типы индексов",
            "Clustered и Non-clustered — единственные два типа"
        ],
        "a": "B-Tree (дефолт), Hash (равенство), составной (left-prefix), частичный, уникальный, полнотекстовый, кластеризованный."
    },
    {
        "t": "A",
        "topic": "Индексы",
        "err": False,
        "q": "Какова цена наличия индексов?",
        "correct": "Ускоряют чтение, замедляют запись и занимают место",
        "wrong": [
            "Замедляют и чтение, и запись — только для уникальности",
            "Ускоряют только INSERT; SELECT не затрагивают",
            "Индексы бесплатны, если таблица меньше 1 млн строк"
        ],
        "a": "Индексы ускоряют SELECT/JOIN, но каждая запись требует обновления индекса — INSERT/UPDATE/DELETE медленнее, плюс место на диске."
    },
    {
        "t": "A",
        "topic": "JVM",
        "err": False,
        "q": "Что такое Reflection в Java?",
        "correct": "Доступ к структуре класса в runtime: поля, методы, аннотации",
        "wrong": [
            "Компиляция Java в нативный код на лету",
            "Подмена bytecode при загрузке класса ClassLoader",
            "Анализ исходников через AST без запуска JVM"
        ],
        "a": "Reflection — introspection в runtime: поля, методы, аннотации RUNTIME, динамическое создание и вызов."
    },
    {
        "t": "A",
        "topic": "JVM",
        "err": False,
        "q": "Как устроена цепочка ClassLoader в Java?",
        "correct": "Bootstrap → Platform → Application; делегирование родителю",
        "wrong": [
            "Application → Bootstrap → Platform — снизу вверх",
            "Каждый ClassLoader грузит классы независимо без делегирования",
            "Только один ClassLoader на всё приложение"
        ],
        "a": "Иерархия с делегированием: сначала спрашивают родителя, потом грузят сами. Bootstrap → Platform → Application."
    },
    {
        "t": "A",
        "topic": "Транзакции",
        "err": False,
        "q": "Что такое MVCC в PostgreSQL?",
        "correct": "Версии строк + снимок транзакции; читатели не блокируют писателей",
        "wrong": [
            "Блокировка всей таблицы на время SELECT",
            "Один глобальный lock на базу для записи",
            "Кэширование результатов SELECT в Redis"
        ],
        "a": "Multi-Version Concurrency Control: новая версия строки на изменение, читатели видят свой snapshot. SERIALIZABLE в PG — SSI поверх snapshot isolation."
    },
    {
        "t": "A",
        "topic": "Многопоточность",
        "err": True,
        "q": "Как реализован CAS в Atomic-классах?",
        "correct": "Compare-And-Swap на уровне CPU; повтор в цикле при конфликте",
        "wrong": [
            "synchronized на каждый вызов getAndIncrement",
            "Lock-free очередь в heap для каждой операции",
            "volatile + Thread.yield() до успеха"
        ],
        "a": "CAS: сравни с ожидаемым, замени если совпало, иначе повтор. Реализация через CMPXCHG / VarHandle. Lock-free, не просто volatile++.",
        "note": "Интервьюер тянул к сути реализации."
    },
    {
        "t": "A",
        "topic": "Паттерны",
        "err": False,
        "q": "Назови три категории паттернов GoF с примерами.",
        "correct": "Порождающие, структурные, поведенческие",
        "wrong": [
            "Архитектурные, инфраструктурные, доменные",
            "Singleton, Factory, Observer — три категории",
            "Creational, SOLID, Reactive"
        ],
        "a": "Порождающие: Singleton, Factory, Builder. Структурные: Adapter, Decorator, Proxy. Поведенческие: Strategy, Observer, Command."
    },
    {
        "t": "A",
        "topic": "Сети",
        "err": True,
        "q": "Что делает DNS?",
        "correct": "Преобразует доменное имя в IP-адрес",
        "wrong": [
            "Преобразует MAC в IP в локальной сети",
            "Выдаёт IP-адрес и маску клиенту автоматически",
            "Переводит приватный IP в публичный на роутере"
        ],
        "a": "DNS — Domain Name System: резолвинг имени (example.com) в IP."
    },
    {
        "t": "A",
        "topic": "Сети",
        "err": True,
        "q": "Что делает ARP?",
        "correct": "Определяет MAC-адрес по IP в локальной сети",
        "wrong": [
            "Резолвит доменное имя в IP",
            "Назначает IP клиенту при подключении к Wi‑Fi",
            "Шифрует трафик на канальном уровне"
        ],
        "a": "ARP — Address Resolution Protocol: IP → MAC в пределах L2-сегмента."
    },
    {
        "t": "A",
        "topic": "Сети",
        "err": True,
        "q": "Что делает DHCP?",
        "correct": "Автоматически выдаёт IP и сетевые параметры клиенту",
        "wrong": [
            "Маршрутизирует пакеты между подсетями",
            "Преобразует домен в IP через кэш",
            "Создаёт VPN-туннель между хостами"
        ],
        "a": "DHCP — Dynamic Host Configuration Protocol: IP, маска, шлюз, DNS при подключении."
    },
    {
        "t": "A",
        "topic": "Сети",
        "err": True,
        "q": "Что делает NAT?",
        "correct": "Переводит приватные IP в публичный (и обратно) на границе сети",
        "wrong": [
            "Определяет MAC по IP в Ethernet",
            "Выдаёт сертификаты TLS для HTTPS",
            "Балансирует HTTP-запросы между серверами"
        ],
        "a": "NAT — Network Address Translation: private IP ↔ public IP на выходе в интернет."
    },
    {
        "t": "A",
        "topic": "Сети",
        "err": True,
        "q": "На каком уровне OSI работают IP-маршрутизация и MAC-адреса?",
        "correct": "IP — сетевой (L3); MAC/кадры — канальный (L2)",
        "wrong": [
            "IP — канальный; MAC — сетевой",
            "Оба на транспортном уровне (L4)",
            "IP — прикладной; MAC — физический"
        ],
        "a": "Маршрутизация между сетями — L3 (IP). MAC и Ethernet-кадры — L2.",
        "note": "Была путаница ARP/DNS/NAT."
    },
    {
        "t": "B",
        "topic": "Kafka",
        "err": False,
        "q": "Чем Kafka отличается от классической очереди (RabbitMQ)?",
        "correct": "Durable-лог с retention; сообщения не удаляются после чтения",
        "wrong": [
            "Сообщение удаляется сразу после ack потребителя",
            "Kafka не поддерживает партиции и порядок",
            "RabbitMQ хранит все сообщения на диске бессрочно по умолчанию"
        ],
        "a": "Kafka — распределённый лог: retention, чтение по offset, consumer groups, упорядоченность в партиции, высокая пропускная способность."
    },
    {
        "t": "B",
        "topic": "Kafka",
        "err": False,
        "q": "Что если consumer-ов меньше, чем партиций?",
        "correct": "Один consumer может читать несколько партиций; лишние партиции не простаивают",
        "wrong": [
            "Лишние партиции блокируются до появления consumer",
            "Kafka удаляет лишние партиции автоматически",
            "Сообщения теряются в партициях без consumer"
        ],
        "a": "Consumer group распределяет партиции между участниками. Если consumers < partitions — один consumer берёт несколько партиций."
    },
    {
        "t": "B",
        "topic": "Kafka",
        "err": False,
        "q": "Что если consumer-ов больше, чем партиций?",
        "correct": "Лишние consumer-ы простаивают без назначенных партиций",
        "wrong": [
            "Kafka создаёт новые партиции автоматически",
            "Лишние consumer-ы получают копию всех сообщений",
            "Kafka перенаправляет их в dead-letter queue"
        ],
        "a": "Максимум активных consumers в группе = число партиций. Лишние idle до rebalance или добавления партиций."
    },
    {
        "t": "B",
        "topic": "Kafka",
        "err": False,
        "q": "Что такое exactly-once в Kafka?",
        "correct": "Идempotent producer + транзакции + read_committed consumer",
        "wrong": [
            "Гарантия без дубликатов без участия producer",
            "Только один consumer на топик",
            "Отключение retry у producer"
        ],
        "a": "Exactly-once — комбинация idempotent producer, transactional writes и consumer с isolation.level=read_committed."
    },
    {
        "t": "B",
        "topic": "REST",
        "err": False,
        "q": "Как сделать REST API надёжным?",
        "correct": "Идемпотентность, таймауты, retry с backoff, circuit breaker, DLQ",
        "wrong": [
            "Только HTTPS и JWT",
            "Увеличить timeout до 5 минут на все вызовы",
            "Всегда использовать POST вместо GET"
        ],
        "a": "Идемпотентность (idempotency key для POST), таймауты, экспоненциальный backoff, circuit breaker, корректные статус-коды, DLQ."
    },
    {
        "t": "B",
        "topic": "System Design",
        "err": False,
        "q": "Лента новостей: fan-out on read vs fan-out on write?",
        "correct": "Read — собирать при запросе; write — разлить пост подписчикам заранее",
        "wrong": [
            "Read быстрее для знаменитостей с миллионами подписчиков",
            "Write дешевле по записи, чем read",
            "Разницы нет — всегда используют только push"
        ],
        "a": "Pull (fan-out on read) — дёшево писать, дорого читать. Push (fan-out on write) — быстрое чтение, дорого для «звёзд». Обычно гибрид + кэш."
    },
    {
        "t": "B",
        "topic": "Микросервисы",
        "err": False,
        "q": "Что такое Saga?",
        "correct": "Цепочка локальных транзакций с компенсирующими действиями",
        "wrong": [
            "Двухфазный commit между всеми сервисами",
            "Один глобальный lock на все микросервисы",
            "Паттерн кэширования read-through"
        ],
        "a": "Saga — распределённая транзакция без 2PC: локальные шаги + компенсации при сбое. Оркестрация или хореография."
    },
    {
        "t": "B",
        "topic": "Тестирование",
        "err": False,
        "q": "Что мокать в unit-тестах с Mockito?",
        "correct": "Внешние зависимости: репозитории, HTTP-клиенты, очереди",
        "wrong": [
            "Класс, который тестируем",
            "Все private-методы через reflection",
            "Примитивы и String"
        ],
        "a": "Мокаем внешние зависимости для изоляции логики. when/thenReturn, verify. Не мокаем SUT и простые value-объекты."
    },
    {
        "t": "B",
        "topic": "Реактивность",
        "err": True,
        "q": "Зачем Spring WebFlux / Reactor?",
        "correct": "Неблокирующий I/O: много соединений малым числом потоков",
        "wrong": [
            "Для красивого UI в браузере",
            "Чтобы заменить все synchronized блоки",
            "Только для CPU-bound вычислений на всех ядрах"
        ],
        "a": "Реактивность — про non-blocking I/O и backpressure (Mono/Flux), не про UI. Выигрыш на I/O-bound.",
        "note": "Ранее назвал «для UI» — неверно."
    },
    {
        "t": "B",
        "topic": "Многопоточность",
        "err": False,
        "q": "ConcurrentHashMap vs Collections.synchronizedMap?",
        "correct": "ConcurrentHashMap лочит сегменты; synchronizedMap — всю карту",
        "wrong": [
            "synchronizedMap быстрее при высокой конкуренции",
            "ConcurrentHashMap блокирует всю таблицу на каждый get",
            "Разницы в производительности нет"
        ],
        "a": "synchronizedMap — lock на всю map. ConcurrentHashMap — lock по bin/сегменту, чтения почти без блокировок."
    },
    {
        "t": "B",
        "topic": "Многопоточность",
        "err": False,
        "q": "Что такое ThreadLocal и какая ловушка?",
        "correct": "Своя копия переменной на поток; в пулах нужно remove()",
        "wrong": [
            "Глобальная переменная для всех потоков",
            "Аналог volatile для потоков",
            "Автоматически очищается GC без remove"
        ],
        "a": "ThreadLocal — значение на поток. В thread pool без remove() — утечка памяти и «грязное» состояние между задачами."
    },
    {
        "t": "B",
        "topic": "Stream API",
        "err": False,
        "q": "Промежуточные vs терминальные операции Stream?",
        "correct": "Промежуточные ленивы; терминальные запускают конвейер",
        "wrong": [
            "Все операции Stream выполняются eagerly",
            "Терминальные возвращают Stream",
            "filter и map — терминальные"
        ],
        "a": "Промежуточные (filter, map) ленивы. Терминальные (collect, count) запускают pipeline. Short-circuit: findFirst, limit."
    },
    {
        "t": "B",
        "topic": "DDD",
        "err": False,
        "q": "Что такое bounded context?",
        "correct": "Граница, где термины модели однозначны",
        "wrong": [
            "Пакет в Java с аннотацией @Context",
            "Один микросервис = один bounded context всегда",
            "Слой DAO в Spring"
        ],
        "a": "Bounded context — семантическая граница DDD: «Заказ» в sales и shipping значит разное."
    },
    {
        "t": "B",
        "topic": "CQRS",
        "err": True,
        "q": "Кто меняет состояние в CQRS?",
        "correct": "Command пишет; Query только читает",
        "wrong": [
            "Query обновляет read-модель и меняет write-store",
            "Command и Query всегда в одной таблице",
            "Только Event Sourcing без команд"
        ],
        "a": "Command — изменение без возврата данных. Query — чтение без побочных эффектов.",
        "note": "Раньше путал: говорил «Query меняет»."
    },
    {
        "t": "B",
        "topic": "Масштабирование",
        "err": False,
        "q": "Репликация vs шардирование?",
        "correct": "Репликация — копии данных; шардирование — разные данные на узлах",
        "wrong": [
            "Шардирование — копии одной таблицы на всех узлах",
            "Репликация — горизонтальное разбиение по ключу",
            "Это синонимы PostgreSQL partitioning"
        ],
        "a": "Репликация — те же данные на нескольких узлах (HA, read scale). Шардирование — данные partitioned по ключу на разные узлы."
    },
    {
        "t": "B",
        "topic": "Паттерны",
        "err": False,
        "q": "Double-checked locking для Singleton — зачем volatile?",
        "correct": "Чтобы не опубликовать недоинициализированный объект",
        "wrong": [
            "Чтобы ускорить synchronized без семантики",
            "volatile заменяет synchronized полностью",
            "Чтобы singleton был thread-local"
        ],
        "a": "Без volatile другой поток может увидеть partially constructed instance. DCL: volatile поле + synchronized блок + двойная проверка."
    },
    {
        "t": "B",
        "topic": "SQL",
        "err": False,
        "q": "Чем WHERE отличается от HAVING?",
        "correct": "WHERE фильтрует строки до группировки; HAVING — после, по агрегатам",
        "wrong": [
            "HAVING работает без GROUP BY всегда",
            "WHERE может фильтровать COUNT(*) > 5",
            "WHERE и HAVING — синонимы в PostgreSQL"
        ],
        "a": "GROUP BY группирует для агрегатов. WHERE — до группировки. HAVING — после, по результатам агрегации (HAVING COUNT(*) > 5)."
    },
    {
        "t": "C",
        "topic": "Java Core",
        "err": False,
        "q": "Чем String отличается от StringBuilder?",
        "correct": "String immutable; StringBuilder — изменяемый, для конкатенации в цикле",
        "wrong": [
            "StringBuilder immutable после append",
            "String быстрее StringBuilder в цикле",
            "String хранится только в stack"
        ],
        "a": "String immutable, thread-safe, кэш в pool. StringBuilder — мутабельный, быстрый для сборки строк. StringBuffer — synchronized версия."
    },
    {
        "t": "C",
        "topic": "Java Core",
        "err": False,
        "q": "Что такое String Pool (intern)?",
        "correct": "Пул литералов; одинаковые строки переиспользуются",
        "wrong": [
            "Пул всех объектов String в heap без dedup",
            "Кэш только для строк из new String()",
            "Область памяти для char[] в native memory"
        ],
        "a": "String pool хранит литералы; intern() позволяет переиспользовать каноническую копию."
    },
    {
        "t": "C",
        "topic": "Сети",
        "err": False,
        "q": "Главное отличие HTTP/2 от HTTP/1.1?",
        "correct": "Мультиплексирование потоков в одном TCP-соединении",
        "wrong": [
            "HTTP/2 использует только UDP",
            "HTTP/1.1 уже мультиплексирует запросы по умолчанию",
            "HTTP/2 отказался от заголовков"
        ],
        "a": "HTTP/2 — multiplexing, binary frames, HPACK сжатие заголовков, server push (редко используется)."
    },
    {
        "t": "C",
        "topic": "Сети",
        "err": False,
        "q": "Что такое gRPC?",
        "correct": "RPC поверх HTTP/2 с Protobuf и кодогенерацией",
        "wrong": [
            "REST JSON только с XML-обёрткой",
            "Очередь сообщений как Kafka",
            "Протокол только для gRPC-Gateway без HTTP"
        ],
        "a": "gRPC — RPC на HTTP/2, Protobuf, стриминг, контракты через .proto, компактнее JSON REST."
    },
    {
        "t": "C",
        "topic": "Контейнеры",
        "err": False,
        "q": "Контейнер vs виртуальная машина?",
        "correct": "Контейнер делит ядро ОС; VM — отдельная ОС на гипервизоре",
        "wrong": [
            "Контейнер включает полную гостевую ОС",
            "VM всегда легче контейнера",
            "Контейнер — это тип VM с меньшим RAM"
        ],
        "a": "VM виртуализирует железо + своя ОС. Контейнер — namespaces + cgroups, общее ядро, быстрый старт."
    },
    {
        "t": "C",
        "topic": "Java Core",
        "err": False,
        "q": "Checked vs unchecked исключения?",
        "correct": "Checked — обязаны обработать; unchecked (RuntimeException) — нет",
        "wrong": [
            "Unchecked требуют throws в сигнатуре",
            "Error — подкласс RuntimeException",
            "Checked — только в Spring приложениях"
        ],
        "a": "Checked (Exception) — compile-time проверка. Unchecked (RuntimeException) — ошибки логики. Error — фатальные (OutOfMemory)."
    },
    {
        "t": "C",
        "topic": "Java Core",
        "err": False,
        "q": "Зачем Optional в Java?",
        "correct": "Явно обозначить отсутствие значения в возвращаемом результате",
        "wrong": [
            "Заменить null в полях entity",
            "Ускорить доступ к полям объекта",
            "Обязательный параметр каждого REST API"
        ],
        "a": "Optional — для return type, заставляет обработать empty (map, orElseThrow). Не для полей/параметров/DTO."
    },
    {
        "t": "C",
        "topic": "JVM",
        "err": True,
        "q": "Утечка памяти — это про heap или stack?",
        "correct": "Heap: объекты достижимы по ссылкам, но логически не нужны",
        "wrong": [
            "Stack: переменные local не удаляются",
            "Stack: frame не pop-ится при return",
            "Heap: GC намеренно не собирает young gen"
        ],
        "a": "Утечка — heap: статические коллекции, незакрытые ресурсы, ThreadLocal в pool. Stack overflow — другое (глубокая рекурсия).",
        "note": "Раньше путал heap и stack."
    },
    {
        "t": "C",
        "topic": "Масштабирование",
        "err": False,
        "q": "Синхронная vs асинхронная репликация БД?",
        "correct": "Sync — ждём реплику перед commit (выше latency); async — commit сразу",
        "wrong": [
            "Async сильнее консистентность sync",
            "Sync не влияет на latency записи",
            "Async гарантирует zero data loss всегда"
        ],
        "a": "Sync replication — подтверждение реплики до commit. Async — быстрее, но возможна потеря последних транзакций при сбое."
    },
    {
        "t": "C",
        "topic": "БД",
        "err": False,
        "q": "Партиционирование vs шардирование?",
        "correct": "Партиционирование — части таблицы в одной БД; шардирование — по узлам",
        "wrong": [
            "Шардирование только внутри одного PostgreSQL instance",
            "Партиционирование всегда через сеть",
            "Это одно и то же в MySQL"
        ],
        "a": "Partition — split таблицы в одной БД (range/hash). Sharding — partition по разным серверам для horizontal scale."
    },
    {
        "t": "C",
        "topic": "Коллекции",
        "err": False,
        "q": "Почему Arrays.asList().add() падает?",
        "correct": "Возвращает fixed-size обёртку над массивом",
        "wrong": [
            "Arrays.asList клонирует массив в новый ArrayList",
            "add запрещён только для primitive arrays",
            "List из asList thread-safe и immutable навсегда"
        ],
        "a": "Arrays.asList — view с фиксированным размером; add/remove → UnsupportedOperationException. Нужен new ArrayList<>(Arrays.asList(...))."
    },
    {
        "t": "B",
        "topic": "JVM",
        "err": False,
        "q": "Прервётся ли поток, если в main удалить ссылку на Thread?",
        "correct": "Нет — поток живёт, пока не завершит run() (если не daemon)",
        "wrong": [
            "Да — GC сразу останавливает поток",
            "Да — JVM завершает все потоки при null в main",
            "Только если поток помечен volatile"
        ],
        "a": "Ссылка в main не удерживает поток. Non-daemon потоки держат JVM живой. Daemon завершатся при exit main. GC не «убивает» потоки.",
        "note": "Вопрос из TODO — проверка понимания GC и потоков."
    },
    {
        "t": "B",
        "topic": "JVM",
        "err": False,
        "q": "С какой версии Java G1 стал сборщиком по умолчанию?",
        "correct": "Java 9 (до этого — Parallel GC в Java 8)",
        "wrong": [
            "Java 8",
            "Java 11 только на серверах",
            "Java 17 — первый раз G1"
        ],
        "a": "G1 default с Java 9. Java 8 default — Parallel GC. Современные GC (ZGC, Shenandoah) — отдельные флаги."
    },
    {
        "t": "B",
        "topic": "GRASP",
        "err": False,
        "q": "Что такое Information Expert в GRASP?",
        "correct": "Назначить ответственность классу, у которого есть нужная информация",
        "wrong": [
            "Всегда передавать логику в Controller",
            "Один Service на всё приложение",
            "Expert — это Singleton паттерн"
        ],
        "a": "Information Expert: метод там, где данные. Low Coupling / High Cohesion — соседние принципы GRASP.",
        "note": "Из TODO — GRASP редко спрашивают, но полезно."
    },
    {
        "t": "B",
        "topic": "GRASP",
        "err": False,
        "q": "Low Coupling и High Cohesion — суть?",
        "correct": "Минимум зависимостей между классами; максимум связности внутри класса",
        "wrong": [
            "Максимум зависимостей для гибкости",
            "Cohesion — число public методов > 20",
            "Coupling — использование только final классов"
        ],
        "a": "Low Coupling — слабая связь между модулями. High Cohesion — класс делает одну связную задачу хорошо."
    },
    {
        "t": "B",
        "topic": "Миграции БД",
        "err": False,
        "q": "Flyway / Liquibase — зачем?",
        "correct": "Версионирование и автоматическое применение миграций схемы БД",
        "wrong": [
            "ORM Hibernate замена",
            "Резервное копирование production nightly",
            "Шардирование таблиц по hash"
        ],
        "a": "Flyway/Liquibase — migration scripts в VCS, repeatable deploy, audit history. Hibernate ddl-auto=update не для prod."
    },
    {
        "t": "B",
        "topic": "Spring",
        "err": False,
        "q": "Что делает @Transactional?",
        "correct": "Открывает/коммитит/откатывает транзакцию вокруг метода через AOP",
        "wrong": [
            "Создаёт новый поток для каждого вызова",
            "Кэширует результат метода в Redis",
            "Заменяет synchronized на уровне JVM"
        ],
        "a": "Spring управляет transaction boundary: begin, commit, rollback. Работает через proxy — только public методы бина снаружи."
    },
    {
        "t": "B",
        "topic": "Spring",
        "err": False,
        "q": "Сработает ли @Transactional на private методе?",
        "correct": "Нет — Spring AOP не перехватывает private",
        "wrong": [
            "Да — если включить aspectj-weaver",
            "Да — для всех методов в @Service",
            "Да — но только для read-only"
        ],
        "a": "Proxy видит только public методы бина. private / internal call (this.foo()) — self-invocation, транзакция не начнётся.",
        "note": "Из TODO — частый лайв-coding вопрос."
    },
    {
        "t": "B",
        "topic": "Spring",
        "err": False,
        "q": "Почему @Transactional не работает при вызове this.method()?",
        "correct": "Self-invocation минует Spring proxy",
        "wrong": [
            "Transactional работает только в main()",
            "Нужен keyword synchronized",
            "Только один @Transactional на класс"
        ],
        "a": "Вызов через this — не через proxy, AOP не применяется. Решение: вынести в другой bean, self-injection, AspectJ weaving."
    },
    {
        "t": "B",
        "topic": "SQL",
        "err": False,
        "q": "Как выбрать поле для индекса?",
        "correct": "Высокая селективность, часто в WHERE/JOIN, не слишком частые UPDATE",
        "wrong": [
            "Всегда индексировать каждое поле таблицы",
            "Только boolean флаги",
            "Только TEXT и JSONB колонки"
        ],
        "a": "Индекс на колонках из WHERE/JOIN с хорошей селективностью. Не индексировать всё подряд — цена на write."
    },
    {
        "t": "B",
        "topic": "SQL",
        "err": False,
        "q": "Long vs UUID для первичного ключа?",
        "correct": "Long — компактнее, быстрее индекс; UUID — глобальная уникальность, но шире и random I/O",
        "wrong": [
            "UUID всегда быстрее B-Tree",
            "Long нельзя использовать в distributed системах",
            "UUID sequential всегда хуже Long без исключений"
        ],
        "a": "Long/BIGSERIAL — меньше, монотонный insert в B-Tree. UUID — merge реплик, API, но 16 байт и random UUID фрагментирует индекс."
    },
    {
        "t": "B",
        "topic": "SQL",
        "err": False,
        "q": "Клиенты без заказов — какой JOIN?",
        "correct": "LEFT JOIN orders + WHERE orders.id IS NULL (или NOT EXISTS)",
        "wrong": [
            "INNER JOIN — покажет клиентов без заказов",
            "CROSS JOIN clients orders",
            "RIGHT JOIN только orders"
        ],
        "a": "Классика: SELECT c.* FROM clients c LEFT JOIN orders o ON o.client_id = c.id WHERE o.id IS NULL. Или NOT EXISTS.",
        "note": "Из TODO — классическая SQL задача на собесах."
    },
    {
        "t": "A",
        "topic": "SOLID",
        "err": False,
        "q": "Что означает S в SOLID (классически)?",
        "correct": "Single Responsibility — один класс, одна причина для изменения",
        "wrong": [
            "Single method — один public метод на класс",
            "Single instance — только один объект класса",
            "Single package — класс в одном package"
        ],
        "a": "SRP: класс меняется только по одной оси ответственности. На собесах иногда ждут «одна функция» — уточняй формулировку.",
        "note": "Из TODO — иногда ждут habr-версию «одна функция»."
    },
    {
        "t": "A",
        "topic": "SOLID",
        "err": False,
        "q": "Расшифруй O и L в SOLID.",
        "correct": "Open/Closed — открыт для расширения, закрыт для изменения; Liskov — подтипы заменяемы",
        "wrong": [
            "Open — все методы public; Liskov — только наследование",
            "Open — open source; Liskov — list interface",
            "Open API; Liskov substitution — только для Java 17"
        ],
        "a": "OCP — расширяем поведение без правки существующего кода. LSP — подкласс не ломает контракт базового класса."
    },
    {
        "t": "B",
        "topic": "Java Core",
        "err": False,
        "q": "finally vs try-with-resources?",
        "correct": "try-with-resources автоматически закрывает AutoCloseable; finally — для любого cleanup",
        "wrong": [
            "finally всегда быстрее try-with-resources",
            "try-with-resources не вызывает close при exception",
            "finally заменяет catch полностью"
        ],
        "a": "try-with-resources (Java 7+) вызывает close() автоматически, suppress exceptions. finally — ручной cleanup, риск забыть close.",
        "note": "Из TODO."
    },
    {
        "t": "B",
        "topic": "Java Core",
        "err": False,
        "q": "Область видимости переменной, объявленной в try-with-resources?",
        "correct": "Только внутри try-блока; ресурс закрыт после блока",
        "wrong": [
            "На весь метод",
            "На весь класс если final",
            "До конца catch, но не finally"
        ],
        "a": "Resource в try-with-resources scoped to try block. close() вызывается до выхода из try/catch."
    },
    {
        "t": "B",
        "topic": "Микросервисы",
        "err": False,
        "q": "Что гласит теорема CAP?",
        "correct": "Из Consistency, Availability, Partition tolerance — одновременно только два",
        "wrong": [
            "Можно иметь все три при Kafka",
            "CAP — про CPU, ALU, Pipeline",
            "Consistency и Availability всегда вместе в SQL"
        ],
        "a": "При network partition (P) выбирают между C (strong consistency) и A (availability). CP — ZooKeeper; AP — Cassandra."
    },
    {
        "t": "B",
        "topic": "Микросервисы",
        "err": False,
        "q": "Transaction Outbox — зачем?",
        "correct": "Атомарно записать в БД и событие для брокера без dual write",
        "wrong": [
            "Дублировать каждую таблицу в Redis",
            "Заменить Saga полностью",
            "Хранить только dead-letter сообщения"
        ],
        "a": "Outbox: в одной локальной транзакции business row + outbox row; отдельный relay публикует в Kafka/Rabbit."
    },
    {
        "t": "B",
        "topic": "SQL",
        "err": False,
        "q": "Зачем смотреть EXPLAIN план запроса?",
        "correct": "Увидеть seq scan vs index scan, cost, join order — найти узкое место",
        "wrong": [
            "Только для проверки синтаксиса SQL",
            "EXPLAIN блокирует таблицу на чтение",
            "Заменяет профилирование JVM"
        ],
        "a": "EXPLAIN (ANALYZE, BUFFERS) показывает как СУБД выполнит запрос: индексы, nested loop, cost, rows."
    },
    {
        "t": "B",
        "topic": "SQL",
        "err": False,
        "q": "Расшифруй ACID для транзакций.",
        "correct": "Atomicity, Consistency, Isolation, Durability",
        "wrong": [
            "Async, Cache, Index, Data",
            "Availability, Consistency, Isolation, Distribution",
            "Atomic, Concurrent, Isolated, Distributed"
        ],
        "a": "Atomicity — всё или ничего. Consistency — инварианты. Isolation — уровни изоляции. Durability — после commit данные сохранены."
    },
    {
        "t": "B",
        "topic": "Многопоточность",
        "err": False,
        "q": "Mutex vs synchronized в Java?",
        "correct": "synchronized — встроенный монитор JVM; Mutex — явный lock (ReentrantLock)",
        "wrong": [
            "Mutex быстрее synchronized всегда",
            "synchronized работает только в static методах",
            "Mutex — только в operating system, Java не поддерживает"
        ],
        "a": "synchronized — monitor enter/exit на object. ReentrantLock — явный lock/unlock, tryLock, fairness."
    }
]
