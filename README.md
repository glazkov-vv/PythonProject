# Описание проекта

### Реализация файлового менеджера с консольным и GUI- интерфейcом под ОС семейства Linux.

# Функционал

- Отображение в консоли 2-х независимых панелей с файлами с возможностью навигации по папкам
- Аналогичный GUI-интерфейс
- Бвзовые операции с файлами (создание пустого файла/копирование/перемещение/удаление/переименование)
- Поддержка создания ссылок
- Поддержка просмотра/изменения разрешений/владельца файла
- Отображение папки в древовидном формате
- Отмена и повторение операций (Ctrl-Z/Ctrl-Y)
- Добавление возможности привязки форматов файла к командам (возможно, нескольких) для быстрого редактирования/запуска
- Сортировка по параметрам (имени/размеру/дате/типу)
    ### Дополнительно (если останется время)
- Поддержка вкладок в GUI-интерфейсе
- Поддержка drag-and-drop-операций в GUI-интерфейсе
- Поддержка стандартных горячих клавиш в GUI-интерфейсе
- При недостаточных разрешениях - возможность непосредственно в консольном/графическом интерфейсе авторизоваться как суперпользователь и продолжить запрошенное действие
- Выбор и копирование/перемещение нескольких файлов одновременно

# Описание архитектуры (предварительное)

Проект представляет собой типичный случай наличия нескольких различных интерфейсов, привязанных к единой логике, в связи с чем реализация этих частей должна быть строго разделена (паттерн Bridge)

### Описание основных классов и методов 


class Workspace - основной класс, задающий директорию в файловой системе, которая в настоящий момент открыта у пользователя

    @classmethod
    open(path:string)->Workspace

    get_files(self) -> iterable[File]
    get_selection(self)->Selection
    

class FilePermissions
    
    file:File

    u:set
    g:set
    o:set
    

class FSInteraction:

    @classmethod
    create,delete,rename и т.д - базовые методы взаимодействия с файловой системой - обертки над командами терминала/функциями модуля os

    copy(source:File,destination:string)->None
    move(source:File,destination:string)->None
    link(source:File,destination:string)->None

class File - позволяет выполнять операции с файлами/директориями
    
    name:string
    owner:string
    permissions:FilePermissions
    type:string
    size:int
    path:string
    created:datetime
    modified:datetime
    Предоставляется read-only доступ


    open(self)->None (присутствует, если type=='file')


    copy(self)->FileTransaction
    move(self)->FileTransaction
    link(self)->FileTransaction


class FileTransaction - для копирования/перемещения/создания ссылки/создания/удаления

    execute()->None
    reversed()->FileTransaction

Наследники класса: для операций копирования/перемещения/переименования/изменения привилегий и т. д.

class GroupFileTransaction(FileTransaction) - если несколько операций происходят одновременно и должны при необходимости быть отменены одновременно

    transactions:iterable[FileTransaction]


class EventsMonitor - класс, который посылает сообщение о необходимости обновления при любом успешном действии в файловой системе

    def subscribe (self,callback)
    def call(self)


class TransactionStack:

    push(transaction)->None
    pop()->FileTransaction

class Selection:

    type:string
    files:iterable[File]



Классы в архитектура интерфейса будут соответствовать сущностям в иерархии логической части

Panel <-> Workspace

FileEntry <-> File

InstrumentationPanel
ActionButton



Взаимодействие с файлами будет осуществляться через объект Workspace (получение списка файлов), Selection (изменение набора выбранных файлов), Transaction (изменения), TransactionStack(откат)

# Используемые библиотеки
- urwid (для создания CLI-интерфейса)
- PyQt (для создания GUI-интерфейса)
- threading, asyncio (для возможности выполнять неблокирующие операции с большими файлами, с отслеживанием прогресса)

# Алгоритм работы

1. Запуск приложения. Создание 2-х панелей (объектов Panel), соответствующих объекту Workspace (получается поиском файлов в текущей директории)
2. Переход по директориям. Новая директория выбирается клавишами (CLI) или мышью (в GUI). Переход осуществляется при помощи создания нового Workspace по пути через функцию open
3. Операции с файлами.
    3.1. Выбор одного файла (получение Selection из Panel через Workspace)
        3.1.1 Переименование (создание MoveFileTransaction)
        3.1.2 Изменение разрешений (создание ChangePermissionTransaction)
    3.2 Выбор нескольких файлов (получение Selection из Panel через Workspace)
        3.2.1 Перемещение (создание MoveFileTransaction)
        3.2.2 Копирование (создание CopyFileTransaction)
        3.2.3 Удаление (без создания FileTransaction)
    3.3 Создание директории
    
    Пункты 3.1.1, 3.1.2 реализуются через диалоговое окно Properties файла

    Пункты 3.2.* позволяют отслеживать статус операции через диалоговое окно ProgressDialog (операции с файлами выполняются в отдельном потоке)

    При недостаточных привилегиях для любой из операций запрашивается пароль sudo через диалоговое окно SudoDialog

    Любая ошибка отображается через диалоговое окно ErrorDialog

4. Отмена последних FileTransaction сочетаниями клавиш (создание и исполнение обратных FileTransaction)

----------------------------

Интерфейс - аналогичен (упрощенно) GNU Midnight Commander

Отрисовка объектов происходит путем создания прокси-объектов уровня интерфейса, ссылающиеся на данные, имеющие метод draw (предоставляющие непосредственно виджет CLI/GUI библиотеки), также выполняющие изменение данных в них на основе пользовательского ввода

Сортировка, древовидное отображение - через изменение свойств getFiles



--------
# Как использовать

Навигация осуществляется стрелками на клавиатуре/мышью

Чтобы переключить состояние объекта, нажмите на пробел

Для перехода в директорию/открытия файла нажмите Enter или сделайте двойной клик мышью

Для перехода в родительскую директорию нажмите Backspace

Для копирования (перемещения) выбранных файлов нажмите C (X). Перейдите в целевую директорию в соседней вкладке и нажмите V. Для отмены нажмите esc

Для включения/выключения древовидного отображения нажмите T

Для того, чтобы просмотреть/изменить свойства файла, нажмите f12

Для того, чтобы создать новую папку в текущей директории, нажмите M

Зеленым шрифтом отображаются исполняемые файлы, синим - директории

Для обновления информации о файлах нажмите f5

Для запуска в режиме отладки используйте флаг -d

### ВАЖНО
Не следует изменять разрешения директорий, которые в настоящий момент открыты в программе

# Покрытие тестами

Модули, отвечающие за внутреннюю логику (не UI) покрыты тестами на:

![cov](https://glazkov-vv.github.io/PythonProject/badge.svg)

