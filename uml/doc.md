# Описание архитектуры

## Транзакции

Основной логической единицей для манипуляций с файлами является транзакция (Transaction), реализующая паттерн Command.

В каждом из видов транзакций хранится информация об исзодном и целевом состоянии файла. 
Транзакция реализует методы:

- execute - исполнить действие
- revert - получить обратную транзакцию,

а также (если транзакция потенциально займет продолжительное время):
- set_callback - задать callback для получения информации о прогрессе исполнения транзакции

Возвращаемое значение, отличное от None, всегда явялется сообщением ошибки

## Интерфейс

Для перехода между окнами с сохранением контекста и порядка использован базовый класс StackedView, который упорядочивает окна в односвязный список, отвечает за взаимодействие с top-level компонентом cli и предоставляет интерфейс для перехода между окнами

Расширение этого класса - ExecutesTransaction - также предоставляет метод для запуска транзакций:

1) Непосредственно исполнение транзакции
2) Создание записи в истории транзакций
3) Создание ProgressWindow (при необходимости)
4) Создание ErrorWindow (при необходимости)


### FileEntry
Отвечает за отображение информации об одном файле. В соответствии с атрибутом schema отрисовывает как статические текстовые поля, так и произвольные виджеты

### FilePanel
Отвечает за открытую директорию.
Отрисовывает список FileEntry, а также PanelPath (путь к файлу) и TitleEntry (названия колонок + сортировка)

### TwoTabs
Контейнер интерфейса верхнего уровня. Хранит 2 FilePanel и предоставляет механизм переключения между ними

## Взаимодействие между логикой и интерфейсом

Для удобной работы с данными на уровне FileEntry и FilePanel созданы классы File и Workspace, отвечающие за работу с данными.

Следует отметить, что данные, связанные с файлами вне контекста работы файлового менеджера не хранятся в объектах, а получаются динамически, т. к., могут меняться вне программы


### Передача сообщений

При любых изменениях, которые возникают на уровне транзакции/UI, обработка событий идет следующим образом:

1) Информация о событии отправляется в наиболее низкий компонент logic, способный полностью обработать данное событие (WorkspaceManager - если меняется структура директории, Workspace - если меняются параметры отображения, File - если меняется информация о файле)
2) Информация передается компонентам logic более низкого уровня
3) На каждом шаге информация передается в функцию (обычно rebuild) соответствующего компонента cli (паттерн Observer, реализуется через класс Subscriptable)

Такой подход:

1) Позволяет в момент создания события понимать, на каком уровне оно будет обработано
2) Не требует создания сложной структуры самих событий (если искать компонент, способный обработать событие, поиском вверх по родителям, требуется хранить информацию о самом событии, которая избыточна в случае, если кол-во типов событий мало)

# Manager

Реализует хранение глобальной информации о работе приложения и истории транзакций (паттерн Singleton)

# Возможные улучшения

1. Выделить проверку разрешений в отдельный модуль
2. Применить паттерн State для работы в режимах select_for_copy/select_for_move
3. Выделить константы (0.2 сек для double-click, 1000 файлов в папке и т. д.) в конфигурационный файл




