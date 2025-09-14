# Crawl4AI MCP Server

Мощный Model Context Protocol (MCP) сервер для веб-скрапинга и анализа контента с поддержкой JavaScript, снимков экрана и экспорта в PDF.

[![CI Status](https://github.com/stgmt/crawl4ai-mcp/workflows/Basic%20Tests/badge.svg)](https://github.com/stgmt/crawl4ai-mcp/actions)
[![Code Quality](https://github.com/stgmt/crawl4ai-mcp/workflows/Code%20Quality/badge.svg)](https://github.com/stgmt/crawl4ai-mcp/actions)
[![Docker](https://github.com/stgmt/crawl4ai-mcp/workflows/Docker%20Build%20and%20Push/badge.svg)](https://github.com/stgmt/crawl4ai-mcp/actions)

## 🚀 Особенности

- **MCP совместимость**: Поддержка stdio, HTTP и SSE транспортов
- **Универсальные форматы**: HTML, Markdown, PDF, скриншоты
- **JavaScript выполнение**: Полная поддержка современных веб-приложений
- **Bearer токен аутентификация**: Безопасный доступ к API
- **Docker готов**: Multi-stage сборка с оптимизацией размера
- **TypeScript тестирование**: Комплексная система тестирования
- **Production ready**: Готов к промышленному использованию

## 🛠️ Доступные MCP инструменты

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `md` | Конвертация веб-страниц в Markdown | `url` |
| `html` | Извлечение HTML контента | `url` |
| `screenshot` | Снимки веб-страниц | `url`, `options` |
| `pdf` | Конвертация страниц в PDF | `url`, `options` |
| `execute_js` | Выполнение JavaScript на странице | `url`, `js_code` |
| `crawl` | Расширенное сканирование с опциями | `urls[]`, `options` |

## 📦 Быстрый старт

### Option 1: Docker (Рекомендуется)

```bash
# Клонирование и сборка
git clone https://github.com/stgmt/crawl4ai-mcp.git
cd crawl4ai-mcp

# Сборка и запуск с Docker Compose
docker-compose up --build

# Или сборка отдельного контейнера
cd python-mcp-server
docker build -t crawl4ai-mcp .

# Запуск контейнера
docker run -p 3000:3000 \
  -e CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com" \
  -e CRAWL4AI_BEARER_TOKEN="your-token" \
  crawl4ai-mcp
```

### Option 2: Локальная установка

```bash
# Python MCP Server
cd python-mcp-server
pip install -r requirements.txt

# Запуск STDIO режима
python -m src.server

# Запуск HTTP режима
python -m src.server --http

# Запуск SSE режима
python -m src.server --sse
```

## ⚙️ Конфигурация

### Переменные окружения

```bash
# ОБЯЗАТЕЛЬНЫЕ
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-api.com"

# ОПЦИОНАЛЬНЫЕ
export CRAWL4AI_BEARER_TOKEN="your-bearer-token"
export HTTP_PORT="3000"
export SSE_PORT="9001"
export LOG_LEVEL="INFO"
export DEBUG="false"
export REQUEST_TIMEOUT="30"
```

### Конфигурация MCP клиента

Добавьте в ваш `.mcp.json`:

```json
{
  "mcpServers": {
    "crawl4ai": {
      "transport": "stdio",
      "command": "python",
      "args": ["-m", "python-mcp-server.src.server"],
      "env": {
        "CRAWL4AI_ENDPOINT": "https://your-server.com",
        "CRAWL4AI_BEARER_TOKEN": "your-token"
      }
    }
  }
}
```

Для HTTP транспорта:

```json
{
  "mcpServers": {
    "crawl4ai-http": {
      "transport": "http",
      "url": "http://localhost:3000/mcp",
      "bearerToken": "your-bearer-token"
    }
  }
}
```

## 🐳 Docker команды

```bash
# Разработка
docker build -t crawl4ai-mcp:dev .
docker run --rm -p 3000:3000 crawl4ai-mcp:dev

# Продакшн с переменными окружения
docker run -d --name crawl4ai-mcp \
  -p 3000:3000 \
  -e CRAWL4AI_ENDPOINT="https://api.crawl4ai.com" \
  -e CRAWL4AI_BEARER_TOKEN="sk_..." \
  -e LOG_LEVEL="INFO" \
  --restart unless-stopped \
  crawl4ai-mcp:latest

# Проверка здоровья
docker exec crawl4ai-mcp curl -f http://localhost:3000/health

# Логи
docker logs -f crawl4ai-mcp

# Остановка
docker stop crawl4ai-mcp && docker rm crawl4ai-mcp
```

### Docker Compose

```yaml
version: '3.8'
services:
  crawl4ai-mcp:
    build: ./python-mcp-server
    ports:
      - "3000:3000"
      - "9001:9001"
    environment:
      - CRAWL4AI_ENDPOINT=https://your-api.com
      - CRAWL4AI_BEARER_TOKEN=your-token
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

## 🧪 Тестирование

```bash
# TypeScript тестер
cd mcp-server-tester
npm install && npm run build

# Запуск всех тестов
npm test

# Тест конкретных инструментов
node dist/cli.js tools test-all-tools.yaml --server-config ../server-config.example.json

# Локальное тестирование
cp server-config.example.json server-config.json
# Отредактируйте server-config.json с вашими параметрами
npm test
```

## 📁 Структура проекта

```
crawl4ai-mcp/
├── python-mcp-server/          # Python MCP сервер
│   ├── src/                    # Исходный код
│   │   ├── handles/            # Обработчики инструментов
│   │   ├── config/             # Конфигурация
│   │   └── server.py           # Главный сервер
│   ├── tests/                  # Python тесты
│   ├── Dockerfile              # Multi-stage Docker сборка
│   ├── docker-compose.yml      # Docker Compose конфиг
│   ├── requirements.txt        # Python зависимости
│   └── pyproject.toml          # Python конфигурация
├── mcp-server-tester/          # TypeScript тестер
│   ├── src/                    # TypeScript исходники
│   ├── test/                   # Тестовые сюиты
│   ├── examples/               # Примеры использования
│   └── test-all-tools.yaml     # Конфигурация тестов
├── .github/workflows/          # CI/CD пайплайны
├── server-config.example.json  # Пример конфигурации
├── BEARER_AUTH.md              # Руководство по аутентификации
└── README.md                   # Эта документация
```

## 🔒 Безопасность

### Bearer Token аутентификация

Для производственного использования настройте Bearer токен:

```bash
# Установка токена
export CRAWL4AI_BEARER_TOKEN="sk_your_secure_token_here"

# HTTP заголовок
Authorization: Bearer sk_your_secure_token_here
```

Подробности в [BEARER_AUTH.md](BEARER_AUTH.md).

### Рекомендации безопасности

- ✅ Всегда используйте HTTPS в продакшне
- ✅ Настройте сильные Bearer токены
- ✅ Ограничьте доступ по IP (nginx/cloudflare)
- ✅ Регулярно ротируйте токены
- ✅ Мониторьте подозрительную активность

## 📊 Мониторинг и логирование

```bash
# Проверка здоровья
curl http://localhost:3000/health

# Структурированные логи (JSON)
docker logs crawl4ai-mcp | jq '.'

# Метрики производительности
docker stats crawl4ai-mcp
```

## 🚀 Производственное развертывание

### Системные требования

- **CPU**: 2+ ядра
- **RAM**: 1GB+ (рекомендуется 2GB)
- **Storage**: 1GB+
- **Network**: Стабильное соединение
- **Docker**: 20.10+

### Reverse Proxy (nginx)

```nginx
upstream crawl4ai-mcp {
    server 127.0.0.1:3000;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL конфигурация...

    location /mcp {
        proxy_pass http://crawl4ai-mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Authorization $http_authorization;
    }
}
```

## 🤝 Разработка

```bash
# Клонирование
git clone https://github.com/stgmt/crawl4ai-mcp.git
cd crawl4ai-mcp

# Установка зависимостей
cd python-mcp-server && pip install -r requirements.txt
cd ../mcp-server-tester && npm install

# Линтинг и проверки
cd python-mcp-server
ruff check .
mypy src --ignore-missing-imports

cd ../mcp-server-tester
npm run lint
npm run typecheck

# Запуск в режиме разработки
python -m src.server --debug
```

## 📝 Лицензия

MIT License - см. [LICENSE](LICENSE) для деталей.

## 🆘 Поддержка

- **Issues**: [GitHub Issues](https://github.com/stgmt/crawl4ai-mcp/issues)
- **Документация**: [Полная документация](docs/)
- **Примеры**: [examples/](examples/)

---

**Готов к продакшн использованию с комплексной системой безопасности и тестирования.**