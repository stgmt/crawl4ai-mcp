# Архитектура тестов Crawl4AI MCP Server

## Обзор

Тесты переписаны с использованием лучших практик тестирования от сеньор тестировщика:

- **Тестирование через публичные интерфейсы** - НЕ тестируем внутренние детали реализации
- **Dependency Injection** - все зависимости инжектируются через фикстуры
- **Полная изоляция** - каждый тест независим и воспроизводим
- **Правильные моки** - мокаем только внешние зависимости (HTTP, файловая система)
- **Edge cases** - покрываем граничные случаи и ошибки

## Структура тестов

### `conftest.py`
Централизованные pytest фикстуры для всех тестов:
- `mock_settings` - конфигурация сервера
- `mock_httpx_client` - HTTP клиент для API вызовов
- `mock_tool_registry` - реестр инструментов
- `crawl4ai_server` - настроенный экземпляр сервера
- `error_scenarios` - типовые сценарии ошибок

### `test_server.py`
Тесты основного MCP сервера:
- **TestCrawl4AIMCPServer** - инициализация и основные хендлеры
- **TestTransportModes** - STDIO, SSE, HTTP транспорты
- **TestToolRegistry** - регистрация и получение инструментов
- **TestErrorHandling** - обработка ошибок и edge cases

### `test_tools.py`
Тесты отдельных инструментов:
- **TestMdTool** - конвертация в Markdown
- **TestHtmlTool** - извлечение HTML
- **TestScreenshotTool** - создание скриншотов
- **TestExecuteJsTool** - выполнение JavaScript
- **TestCrawlTool** - массовый краулинг
- **TestPdfTool** - генерация PDF

### `test_integration.py`
Интеграционные тесты:
- **TestEndToEndScenarios** - полные сценарии использования
- **TestTransportIntegration** - взаимодействие транспортов
- **TestAuthenticationAndSecurity** - аутентификация и безопасность

## Принципы тестирования

### 1. Тестирование поведения, а не реализации

❌ **Плохо:**
```python
# Тестирует внутренние детали
handlers = server._tool_handlers  # Доступ к приватному атрибуту
assert handlers.get("list_tools") is not None
```

✅ **Хорошо:**
```python
# Тестирует через публичный интерфейс
result = await server.list_tools()
assert len(result) > 0
```

### 2. Правильное использование моков

❌ **Плохо:**
```python
# Мокает всё подряд
with patch("crawl4ai_mcp.server.Crawl4AIMCPServer"):
    # Теряется смысл теста
```

✅ **Хорошо:**
```python
# Мокает только внешние зависимости
with patch("httpx.AsyncClient") as mock_client:
    # Тестирует реальную логику с моком HTTP
```

### 3. Изоляция тестов

Каждый тест:
- Независим от других тестов
- Имеет свой setup/teardown через фикстуры
- Не изменяет глобальное состояние
- Может выполняться в любом порядке

### 4. Покрытие edge cases

Тесты покрывают:
- Успешные сценарии
- Ошибки сети (timeout, connection errors)
- HTTP ошибки (404, 500, 401)
- Невалидный JSON
- Пустые/None аргументы
- Конкурентные вызовы

## Запуск тестов

### Установка зависимостей
```bash
pip install -e .
pip install pytest pytest-asyncio httpx
```

### Запуск всех тестов
```bash
pytest tests/
```

### Запуск с покрытием
```bash
pytest tests/ --cov=crawl4ai_mcp --cov-report=html
```

### Запуск конкретного теста
```bash
pytest tests/test_server.py::TestCrawl4AIMCPServer::test_server_initialization
```

### Запуск с verbose output
```bash
pytest tests/ -v
```

## Примеры использования фикстур

### Базовый тест с фикстурами
```python
@pytest.mark.asyncio
async def test_example(crawl4ai_server, mock_tool_registry):
    """Пример теста с использованием фикстур."""
    # crawl4ai_server - готовый сервер с моками
    # mock_tool_registry - мок реестра инструментов
    
    # Настройка мока
    mock_tool_registry.get_all_tools.return_value = [...]
    
    # Выполнение теста
    result = await crawl4ai_server.some_method()
    
    # Проверка
    assert result is not None
```

### Тест с мокированием HTTP
```python
@pytest.mark.asyncio
async def test_api_call(mock_httpx_client):
    """Тест с мокированием HTTP вызовов."""
    # Настройка ответа
    mock_httpx_client.post.return_value.json.return_value = {"data": "test"}
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
        
        # Тестируемый код
        result = await some_function_that_calls_api()
        
        # Проверка
        assert result["data"] == "test"
```

## Checklist для code review

При review тестов проверяйте:

- [ ] Тесты независимы друг от друга
- [ ] Используются фикстуры для setup/teardown
- [ ] Мокаются только внешние зависимости
- [ ] Тестируется поведение, а не реализация
- [ ] Покрыты успешные и error сценарии
- [ ] Названия тестов описывают что тестируется
- [ ] Assertions проверяют ожидаемое поведение
- [ ] Нет hardcoded значений (используются фикстуры)
- [ ] Тесты быстрые (< 1 сек на тест)
- [ ] Документированы сложные тест-кейсы

## Метрики качества

Целевые показатели:
- **Code coverage**: > 80%
- **Время выполнения**: < 30 сек для всех тестов
- **Flakiness**: 0% (все тесты стабильные)
- **Независимость**: 100% (можно запускать в любом порядке)

## Дальнейшие улучшения

1. **Performance тесты** - добавить тесты производительности
2. **Load тесты** - тестирование под нагрузкой
3. **Contract тесты** - проверка контрактов API
4. **Mutation testing** - проверка качества тестов
5. **Property-based testing** - использование hypothesis