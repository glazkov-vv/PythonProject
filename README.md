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

    @classMethod
    Open(path:string)->Workspace

    getFiles(self) -> iterable[File]
    getAllFilesInSubdirectories(self) -> iterable[File]
    getSelection(self)->Selection
    

class FilePermissions
    
    file:File

    u:set
    g:set
    o:set
    

class FSInteraction:

    @classMethod
    Create,Delete,Rename и т.д - базовые методы взаимодействия с файловой системой - обертки над командами терминала/функциями модуля os

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



Архитектура интерфейса будет в значительной мере зависеть от типа интерфейса, классы, вероятно, будут соответствовать сущностям в иерархии интерфейса

Panel <-> Workspace

FileEntry <-> File

InstrumentationPanel
ActionButton



Взаимодействие с файлами будет осуществляться через объект Workspace (получение списка файлов), Selection (изменение набора выбранных файлов), Transaction (изменения), TransactionStack(откат)

