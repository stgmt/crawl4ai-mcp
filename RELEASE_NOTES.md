# Release v1.0.4

## 🎉 Crawl4AI MCP Server v1.0.4

### 📝 Что нового

#### 🧹 Очистка и оптимизация
- **Удалены лишние директории** - очищены `mcp-server-tester`, `python-mcp-server` и другие артефакты
- **Обновлен .gitignore** - добавлены паттерны для временных файлов, логов и OS-специфичных файлов
- **Удален устаревший setup.py** - проект теперь полностью использует `pyproject.toml`

#### 📚 Улучшена документация
- **Расширена секция тестирования** - добавлена подробная информация о тестировании с помощью MCP Server Tester
- **Добавлены примеры** для всех трех транспортных протоколов (STDIO, SSE, HTTP)
- **Интерактивное тестирование** - документированы команды для ручного тестирования

#### 🔧 Технические улучшения
- **Синхронизированы версии** во всех конфигурационных файлах
- **Очищены зависимости** в package.json и pyproject.toml
- **Обновлен index.js** с актуальной версией

### 🧪 Тестирование

Теперь сервер можно протестировать с помощью [MCP Server Tester](https://github.com/stgmt/mcp-server-tester-sse-http-stdio):

```bash
# Docker
docker run -it stgmt/mcp-server-tester test \
  --transport stdio \
  --command "crawl4ai-mcp --stdio"

# NPM
npm install -g mcp-server-tester-sse-http-stdio
mcp-server-tester test --transport stdio --command "crawl4ai-mcp --stdio"
```

---

# Release v1.0.3

## 🎉 Crawl4AI MCP Server v1.0.3

### 📝 Что нового

#### 🐛 Исправления
- **Улучшенное определение версии Python для NPM пакета** - добавлена поддержка флагов `--user` и `--break-system-packages` для совместимости с различными окружениями
- **Безопасность** - удалены чувствительные токены из тестовых отчетов
- **Улучшен .gitignore** - добавлено исключение кэш-файлов Python (__pycache__)

#### ✨ Улучшения
- **GitHub Actions** - добавлена автоматизация публикации в PyPI, NPM и Docker Hub
- **Docker оптимизация** - упрощен Dockerfile для лучшей производительности сборки
- **NPM установка** - улучшена совместимость с различными версиями Python

### 📦 Установка

#### Через NPM (рекомендуется для MCP):
```bash
npm install -g crawl4ai-mcp-sse-stdio@1.0.3
npx crawl4ai-mcp --help
```

#### Через PyPI:
```bash
pip install crawl4ai-mcp-sse-stdio==1.0.3
crawl4ai-mcp --help
```

#### Через Docker:
```bash
docker pull stgmt/crawl4ai-mcp:1.0.3
docker run -it stgmt/crawl4ai-mcp:1.0.3 --help
```

### 🔧 Использование с Claude Desktop

Добавьте в ваш `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "npx",
      "args": ["crawl4ai-mcp", "--stdio"]
    }
  }
}
```

### 🌐 Поддерживаемые транспортные протоколы

- **STDIO** - для CLI инструментов и Claude Desktop
- **SSE (Server-Sent Events)** - для веб-клиентов
- **HTTP** - для REST API интеграций

### 📋 Доступные инструменты

- **md** - конвертация веб-страниц в чистый Markdown
- **html** - получение обработанного HTML контента
- **screenshot** - создание скриншотов страниц
- **pdf** - генерация PDF документов
- **execute_js** - выполнение JavaScript на странице
- **crawl** - массовое извлечение данных с нескольких URL

### 🔗 Ссылки

- [NPM Package](https://www.npmjs.com/package/crawl4ai-mcp-sse-stdio)
- [PyPI Package](https://pypi.org/project/crawl4ai-mcp-sse-stdio/)
- [Docker Hub](https://hub.docker.com/r/stgmt/crawl4ai-mcp)
- [GitHub Repository](https://github.com/stgmt/crawl4ai-mcp)
- [Документация](https://github.com/stgmt/crawl4ai-mcp#readme)

### 🤝 Благодарности

Спасибо всем контрибьюторам и пользователям за обратную связь и поддержку!

---

**Full Changelog**: https://github.com/stgmt/crawl4ai-mcp/commits/v1.0.3